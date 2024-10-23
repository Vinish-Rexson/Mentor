from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.staticfiles import finders
from django.db.models import Q

from .forms import *
from .forms import StudentFollowup_Form
from .models import *
from mentor_admin.models import *

from io import BytesIO
import qrcode, base64, secrets
from docxtpl import DocxTemplate
import pdfkit  # Ensure you have this package installed



def Redirect(request):
    return redirect('accounts/login')


def mentor_signup(request):
    if request.method == 'POST':
        form = MentorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and automatically assign to Mentor group
            mentor_group = Group.objects.get_or_create(name='Mentor')
            mentor_group[0].user_set.add(user)
            login(request, user)  # Log in the new user
            return redirect('mentor_dashboard')  # Redirect to the mentor's dashboard
    else:
        form = MentorSignUpForm()

    return render(request, 'signup.html', {'form': form})



@login_required
def mentor_dashboard(request, student_id=None):
    mentor = request.user
    # Fetch the students related to this mentor
    students = MentorshipData.objects.filter(faculty_mentor__iexact=mentor.username.replace('_', ' '))

    total_forms = (
        StudentForm.objects.filter(student__in=students).count() +
        StudentFollowupForm.objects.filter(student__in=students).count()
    )
    total_sessions = Session.objects.filter(mentor=mentor).count()
    # Fetch a specific student if student_id is provided
    student = None
    if student_id:
        student = get_object_or_404(MentorshipData, id=student_id)

    # Call recents and unpack it directly into context
    recent_forms = recents(request)

    context = {
        'student': student,
        'mentor': mentor,
        'student_count': students.count(),
        'students': students,  # Pass the students to the template
        'student_names': [student.name for student in students],
        'recent_mainform': recent_forms['mainform'],
        'recent_followupform': recent_forms['followupform'],
        'total_forms': total_forms,
        'total_sessions': total_sessions,
    }

    return render(request, 'mentor_dashboard.html', context)





@login_required
def recents(request):
    mentor = request.user
    latest_forms = StudentForm.objects.filter(mentor_name=mentor).order_by('-date')[:3]  # Now orders by both date and time
    latest_followupforms = StudentFollowupForm.objects.filter(mentor_name=mentor).order_by('-date')[:3]
    recents = {
        'mainform': latest_forms,
        'followupform': latest_followupforms
    }
    return recents



def student_detail(request):
    
    # Fetch all students from the database
    students = MentorshipData.objects.all()
    
    # Create a dictionary to pass to the template
    context = {
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students],

    }
    
    # Render the template with the context
    return render(request, 'student_detail.html', context)

def dashboard(request):
    return render(request, 'mentor_dashboard.html')


# Function to generate QR code
def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64


# View to generate and display QR code with student_id and mentor_id
def generate_qr(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Get mentor object

    # Check if the token has expired or doesn't exist
    if not student.token or student.is_token_expired():
        # Generate a new token and update the timestamp
        student.token = secrets.token_urlsafe()
        student.token_created_at = timezone.now()
        student.save()

    # Generate the form URL with student_id, mentor_id, and token
    form_url = request.build_absolute_uri(f"/form/generate/{student.id}/{mentor.id}/?token={student.token}")
    
    # Generate the QR code for the URL
    qr_code = generate_qr_code(form_url)
    
    return render(request, 'qr_code_page.html', {
        'student': student,
        'mentor': mentor,  # Pass mentor info to the template if needed
        'qr_code': qr_code
    })


@login_required
def form_student_generate(request, student_id, mentor_id):
    # Fetch the student and mentor based on their IDs
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)
    student1, created = Student1.objects.get_or_create(mentorship_data=student)

    # Get current date for display
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()  # pass current datetime to form models to pass recent forms
    # Validate the token from GET or POST
    token = request.GET.get('token') or request.POST.get('token')
    
    # Check if token is valid and not expired
    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    # Check if a form for this student's roll number already exists
    existing_submission = StudentForm.objects.filter(rollno=student.roll_number).first()

    if existing_submission:
        # If the form was already submitted, return an HttpResponse
        return render(request, "already_submit.html", {'student': student})

    if request.method == 'POST':
        # If it's a POST request, populate the form with POST data
        form = StudentSemForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the form but don't commit immediately to set additional fields
            student_form = form.save(commit=False)
            student_form.student = student  # Set the student field
            student_form.name = student.name  # Automatically set student name
            student_form.rollno = student.roll_number  # Automatically set student roll number
            student_form.mentor_name = mentor.username  # Automatically set mentor's name
            student_form.date = form_datetime  # pass current datetime to form models to pass recent forms
            
            student_form.save()  # Save the form to the database
            
            # Update Student1 model with form data
            student1.atte_ise1 = form.cleaned_data['atte_ise1']
            student1.atte_mse = form.cleaned_data['atte_mse']
            student1.attendance = form.cleaned_data['attendance']
            student1.cts = form.cleaned_data['cts']
            student1.ise1 = form.cleaned_data['ise1']
            student1.mse = form.cleaned_data['mse']
            student1.semcgpa = form.cleaned_data['semcgpa']
            
            if 'profile_picture' in request.FILES:
                student1.profile_picture = request.FILES['profile_picture']
            
            student1.save()  # Save Student1 data
            # Redirect to a success page or confirmation that the form is filled
            return render(request, 'form_submitted.html', {'rollno': student_form.rollno})
        else:
            # If the form is invalid, stay on the same page and show errors
            return render(request, 'form_student_view.html', {
                'form': form,  # Return the form with errors
                'student': student,
                'mentor': mentor,
                'date': form_date,
                'display_date': display_date,
                'token': token,  # Pass the token to the template for security
                'student1': student1
            })
    else:
        # For GET requests, return an empty form
        form = StudentSemForm()

    # Render the form for GET requests
    return render(request, 'form_student_view.html', {
        'form': form,
        'student': student,
        'mentor': mentor,
        'date': form_date,
        'display_date': display_date,
        'token': token,  # Pass the token to the template
        'student1': student1
    })

def form_student(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Fetch the mentor based on the ID in the URL
    preview = request.GET.get('preview', 'false').lower() == 'true'
    # Get the current date in both formats
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()#pass current datetime to form models to pass recent forms
    form_exists = StudentForm.objects.filter(rollno=student.roll_number).exists()#check if form exists for download button

    try:
        # Check if a form entry for the given student already exists
        student_form_instance = StudentForm.objects.get(rollno=student.roll_number)
        print("Existing form instance found for student:", student_form_instance)  # Debugging statement
    except StudentForm.DoesNotExist:
        student_form_instance = None
        print("No existing form instance found for student:", student.roll_number)  # Debugging statement

    if request.method == 'POST':
        if student_form_instance:
            form = StudentSemForm(request.POST, instance=student_form_instance)
        else:
            form = StudentSemForm(request.POST)

        if form.is_valid():
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.mentor_name = mentor.username  # Set the mentor name
            student_form.date = form_datetime#pass current datetime to form models to pass recent forms
            student_form.save()
            print("Form successfully saved for student:", student_form.rollno)  # Debugging statement


            student1, created = Student1.objects.get_or_create(mentorship_data=student)
            # Set the fields you want to save to Student1
            student1.atte_ise1 = form.cleaned_data['atte_ise1']
            student1.atte_mse = form.cleaned_data['atte_mse']
            student1.attendance = form.cleaned_data['attendance']
            student1.cts = form.cleaned_data['cts']
            student1.ise1 = form.cleaned_data['ise1']
            student1.mse = form.cleaned_data['mse']
            student1.semcgpa = form.cleaned_data['semcgpa']
            student1.save()  # Save Student1 data

             # Render the same form.html template with a success message
            return render(request, 'form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,  # Pass the mentor (user) to the template
                'date': form_date,
                'display_date': display_date,
                'success_message': 'Form has been successfully updated for roll number ' + student_form.rollno, # Success message,
                'preview': preview,
                'form_exists': form_exists,
            })
        else:
            print("Form errors:", form.errors)  # Debugging statement
            return render(request, 'form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,  # Pass the mentor (user) to the template
                'date': form_date,
                'display_date': display_date,
                'errors': form.errors,
                'preview': preview,
                'form_exists': form_exists,
            })
    else:
        # If there is an existing form, populate it, else use an empty form
        if student_form_instance:
            form = StudentSemForm(instance=student_form_instance)
            print("Populating form with existing data for student:", student_form_instance)  # Debugging statement
        else:
            form = StudentSemForm()
            print("Creating a new form for student:", student.roll_number)  # Debugging statement

    return render(request, 'form.html', {
        'form': form,
        'student': student,
        'mentor': mentor,  # Pass the mentor to the template
        'date': form_date,
        'display_date': display_date,
        'preview': preview,
        'form_exists': form_exists,
    })


def download_document(request, rollno):
    # Fetch all entries with the given rollno
    forms = StudentForm.objects.filter(rollno=rollno)

    if not forms.exists():
        return HttpResponse("No record found.", status=404)

    # Pick the first or latest entry (customize this logic as needed)
    form = forms.order_by('-id').first()  # Here, we pick the latest one
  
    # Create the form_dict from the selected record
    form_dict = {
    "name": form.name,
    "rollno": form.rollno,
    "attendance": form.attendance,
    "semcgpa": form.semcgpa,
    "atte_ise1": form.atte_ise1,
    "atte_mse": form.atte_mse,
    "cts": form.cts,
    "ise1": form.ise1,
    "mse": form.mse,
    "question1": form.question1,
    "question2": form.question2,
    "question3": form.question3,
    "question4": form.question4,
    "question5": form.question5,
    "question6": form.question6,
    "question7": form.question7,
    "question8": form.question8,
    "question9": form.question9,
    "question10": form.question10,
    "question11": form.question11,
    "question12": form.question12,
    "Strengths":form.Strengths,
    "Weakness" : form.Weakness, 
    "Opportunities" : form.Opportunities,
    "Challenges" : form.Challenges,  
    "nao" : form.nao, 
    "ao" : form.ao,
    "date": form.date,
    "mentor_name":form.mentor_name,
}
    # Call the document generation function
    return generate_document(form_dict)

from django.http import HttpResponse
from io import BytesIO
from docx2pdf import convert
import tempfile
import os

def download_pdf(request, rollno, form_type='main'):
    # Initialize COM library
    # pythoncom.CoInitialize()

    # Get the Word document using the existing download_document function
    if form_type == 'main':
        word_response = download_document(request, rollno)
    else:  # follow-up form
        word_response = download_follow_document(request, rollno)

    # Check if the response is valid
    if word_response.status_code != 200:
        return word_response  # Return the error response if any

    # Create a temporary directory to store the files
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the Word document to a temporary file
        word_file_path = os.path.join(tmpdirname, f"{rollno}_{form_type}.docx")
        with open(word_file_path, 'wb') as word_file:
            word_file.write(word_response.content)

        # Convert the Word document to PDF
        pdf_file_path = os.path.join(tmpdirname, f"{rollno}_{form_type}.pdf")
        convert(word_file_path, pdf_file_path)

        # Read the PDF file
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

    # Return the PDF in the response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={rollno}_{form_type}.pdf'
    return response

def generate_document(form_dict):
    # Find the template document (adjust the path according to your project structure)
    doc_path = finders.find('mentor-form-trial.docx')
    
    # Load the template using docxtpl
    doc = DocxTemplate(doc_path)

    if 'date' in form_dict and form_dict["date"]:
        date_object = form_dict["date"]
        formatted_date = date_object.strftime("%d/%m/%Y")  # Convert to DD/MM/YYYY
    else:
        formatted_date = "" 
    
    # Context for the template
    context = {
    'name': form_dict["name"],
    'rollno': form_dict["rollno"],
    'branch': "Comps",               # Static branch value; adjust as needed
    'semno': "3",                    # Static semester number; adjust as needed
    'semcgpa': form_dict["semcgpa"],
    'cts': form_dict["cts"],         # Cognitive Test Score
    'ise1': form_dict["ise1"],       # ISE 1 performance
    'mse': form_dict["mse"],         # MSE performance
    'atte_ise1': form_dict["atte_ise1"],  # Attendance till ISE 1
    'atte_mse': form_dict["atte_mse"],      # Attendance till MSE
    'attendance': form_dict["attendance"],
    'line1': form_dict["question1"],  # Counseling/Team info
    'line2': form_dict["question2"],  # Co-curricular events info
    'line3': form_dict["question3"],  # Technical activities
    'line4': form_dict["question4"],  # Financial situation
    'line5': form_dict["question5"],  # Technical courses/certifications
    'line6': form_dict["question6"],  # Soft skills training
    'line7': form_dict["question7"],  # Co-curricular events
    'line8': form_dict["question8"],  # Social cause involvement
    'line9': form_dict["question9"],  # Internship details
    'line10': form_dict["question10"],#entrepreneur
    'line11': form_dict["question11"],  # Higher studies plans
    'line12':form_dict["question12"],#joboffer
    'box1':form_dict["Strengths"],
    'box2':form_dict["Weakness"],
    'box3':form_dict["Opportunities"],
    'box4':form_dict["Challenges"],
    'box5':form_dict["nao"],
    'box6':form_dict["ao"],

    'date': formatted_date,
    'mentor_name': form_dict["mentor_name"],
}

    # Render the context into the document
    doc.render(context)
    
    # Save the document to a BytesIO object
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    # Return the generated document in the response
    response = HttpResponse(doc_io.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={form_dict["rollno"]}.docx'
    return response

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import MentorshipData, StudentFollowupForm
from .forms import StudentFollowup_Form
from io import BytesIO
from docxtpl import DocxTemplate
import secrets
from django.contrib.staticfiles import finders


def download_follow_document(request, rollno):
    forms = StudentFollowupForm.objects.filter(rollno=rollno)

    if not forms.exists():
        return HttpResponse("No record found.", status=404)

    form = forms.order_by('-id').first()  # Latest entry

    form_dict = {
        "name": form.name,
        "rollno": form.rollno,
        "attendance": form.attendance,
        "semcgpa": form.semcgpa,
        "atte_ise1": form.atte_ise1,
        "atte_mse": form.atte_mse,
        "ise1": form.ise1,
        "mse": form.mse,
        "question1": form.question1,
        "question2": form.question2,
        "question3": form.question3,
        "question4": form.question4,
        "question5": form.question5,
        "question6": form.question6,
        "question7": form.question7,
        "date": form.date,
        "mentor_name": form.mentor_name,
        "nao": form.nao,
        "ao":form.ao,
    }
    return generate_follow_document(form_dict)


def generate_follow_document(form_dict):
    doc_path = finders.find('followup_form.docx')
    doc = DocxTemplate(doc_path)

    if 'date' in form_dict and form_dict["date"]:
        date_object = form_dict["date"]
        formatted_date = date_object.strftime("%d/%m/%Y")
    else:
        formatted_date = ""

    context = {
        'name': form_dict["name"],
        'rollno': form_dict["rollno"],
        'branch': "Comps",
        'sem': "3",
        'semcgpa': form_dict["semcgpa"],
        'ise1': form_dict["ise1"],
        'mse': form_dict["mse"],
        'atte_ise1': form_dict["atte_ise1"],
        'atte_mse': form_dict["atte_mse"],
        'attendance': form_dict["attendance"],
        'line1': form_dict["question1"],
        'line2': form_dict["question2"],
        'line3': form_dict["question3"],
        'line4': form_dict["question4"],
        'line5': form_dict["question5"],
        'line6': form_dict["question6"],
        'line7': form_dict["question7"],
        'date': formatted_date,
        'mentor_name': form_dict["mentor_name"],
        'box1':form_dict["nao"],
        'box2':form_dict["ao"],
    }

    doc.render(context)
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)

    response = HttpResponse(doc_io.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={form_dict["rollno"]}.docx'
    return response


def followup_form_student_generate(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()#pass current datetime to form models to pass recent forms
    token = request.GET.get('token') or request.POST.get('token')

    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    existing_submission = StudentFollowupForm.objects.filter(rollno=student.roll_number).first()

    if existing_submission:
        # return HttpResponse(f"Follow-up form already submitted for {student.name} (Roll No: {student.roll_number}).", status=403)
        return render(request,"already_submit.html",{'student':student})
    if request.method == 'POST':
        form = StudentFollowup_Form(request.POST)
        if form.is_valid():
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.mentor = mentor
            student_form.save()
            student_form.date = form_datetime #pass current datetime to form models to pass recent forms

            student1, created = Student1.objects.get_or_create(mentorship_data=student)
            # Set the fields you want to save to Student1
            student1.atte_ise1 = form.cleaned_data['atte_ise1']
            student1.atte_mse = form.cleaned_data['atte_mse']
            student1.attendance = form.cleaned_data['attendance']
            
            student1.ise1 = form.cleaned_data['ise1']
            student1.mse = form.cleaned_data['mse']
            student1.semcgpa = form.cleaned_data['semcgpa']
            student1.save()  # Save Student1 data

            return render(request, 'follow_form_submitted.html', {'rollno': student.roll_number})
        else:
            return render(request, 'followup_form_student_view.html', {
                'form': form,
                'student': student,
                'mentor': mentor,
                'date': form_date,
                'display_date': display_date,
                'token': token
            })
    else:
        form = StudentFollowup_Form()

    return render(request, 'followup_form_student_view.html', {
        'form': form,
        'student': student,
        'mentor': mentor,
        'date': form_date,
        'display_date': display_date,
        'token': token
    })


def followup_form_student(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()#pass current datetime to form models to pass recent forms
    form_exists = StudentFollowupForm.objects.filter(rollno=student.roll_number).exists()#check if form exists for download button

    try:
        # Check if a follow-up form entry for the given student already exists
        followup_form_instance = StudentFollowupForm.objects.get(rollno=student.roll_number)
        print("Existing follow-up form instance found for student:", followup_form_instance)  # Debugging statement
    except StudentFollowupForm.DoesNotExist:
        followup_form_instance = None
        print("No existing follow-up form instance found for student:", student)  # Debugging statement

    if request.method == 'POST':
        if followup_form_instance:
            form = StudentFollowup_Form(request.POST, instance=followup_form_instance)
        else:
            form = StudentFollowup_Form(request.POST)

        if form.is_valid():
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.mentor = mentor
            student_form.date = form_datetime#pass current datetime to form models to pass recent forms
            student_form.save()


            student1, created = Student1.objects.get_or_create(mentorship_data=student)
            # Set the fields you want to save to Student1
            student1.atte_ise1 = form.cleaned_data['atte_ise1']
            student1.atte_mse = form.cleaned_data['atte_mse']
            student1.attendance = form.cleaned_data['attendance']
            student1.ise1 = form.cleaned_data['ise1']
            student1.mse = form.cleaned_data['mse']
            student1.semcgpa = form.cleaned_data['semcgpa']
            student1.save()  # Save Student1 data
            return render(request, 'followup_form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,  # Pass the mentor (user) to the template
                'date': form_date,
                'display_date': display_date,
                'success_message': 'Follow Form has been successfully updated for roll number ' + student_form.rollno,  # Success message
                'form_exists': form_exists,
            })  # Debugging statement

            # return render(request, 'follow_form_submitted.html', {'rollno': student_form.rollno})
        else:
            print("Follow-up form errors:", form.errors)  # Debugging statement
            return render(request, 'followup_form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,
                'date': form_date,
                'display_date': display_date,
                'errors': form.errors,
                'form_exists': form_exists,
            })
    else:
        # If there is an existing follow-up form, populate it, else use an empty form
        if followup_form_instance:
            form = StudentFollowup_Form(instance=followup_form_instance)
            print("Populating follow-up form with existing data for student:", followup_form_instance)  # Debugging statement
        else:
            form = StudentFollowup_Form()
            print("Creating a new follow-up form for student:", student)  # Debugging statement

    return render(request, 'followup_form.html', {
        'form': form,
        'student': student,
        'mentor': mentor,
        'date': form_date,
        'display_date': display_date,
        'form_exists': form_exists,
    })


@login_required
def generate_qr_followup(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)

    if not student.token or student.is_token_expired():
        student.token = secrets.token_urlsafe()
        student.token_created_at = timezone.now()
        student.save()

    form_url = request.build_absolute_uri(f"/followup_form/generate/{student.id}/{mentor.id}/?token={student.token}")
    qr_code = generate_qr_code(form_url)

    return render(request, 'qr_code_page.html', {
        'student': student,
        'mentor': mentor,
        'qr_code': qr_code
    })

@login_required
def SE(request):
    mentor = request.user
    username = mentor.username
    readable_name = username.replace('_', ' ').title()
    se_students = MentorshipData.objects.filter(year__iexact="SE", faculty_mentor=readable_name)

    context = {
        'student_count': se_students.count(),
        'students': se_students,
        'student_names': [student.name for student in se_students],
        'mentor': mentor,
    }
    
    return render(request, 'se.html', context)
from django.shortcuts import get_object_or_404

@login_required
def TE(request):
    mentor = request.user
    username = mentor.username
    readable_name = username.replace('_', ' ').title()
    te_students = MentorshipData.objects.filter(year__iexact="TE",faculty_mentor=readable_name)
    
    context = {
        'student_count': te_students.count(),
        'students': te_students,
        'student_names': [student.name for student in te_students],
        'mentor': mentor,
    }

    return render(request, 'te.html', context)

@login_required
def BE(request):
    mentor = request.user
    username = mentor.username
    readable_name = username.replace('_', ' ').title()
    be_students = MentorshipData.objects.filter(year__iexact="BE",faculty_mentor=readable_name)
    

    context = {
        'student_count': be_students.count(),
        'students': be_students,
        'student_names': [student.name for student in be_students],
        'mentor': mentor,
    }

    return render(request, 'be.html', context)
@login_required
def student_profile(request, student_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = request.user
    sessions = Session.objects.filter(mentor=request.user, student=student)
    username = mentor.username
    readable_name = username.replace('_', ' ').title()
    students = MentorshipData.objects.filter(faculty_mentor=readable_name)
    student1 = Student1.objects.get(mentorship_data=student)
    available_mentor_admins = MentorAdmin.objects.all()

    context = {
        'sessions': sessions,
        'students': students,
        'student': student,
        'mentor': mentor,  
        'student1': student1,
        'available_mentor_admins': available_mentor_admins,
    }
    return render(request, 'student_profile.html', context)


@login_required
def form_dashboard(request):
    students = MentorshipData.objects.all()

    context = {
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students],
    }

    return render(request, 'form_dashboard.html', context)




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .forms import SessionForm

@login_required
def create_session(request, student_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            # Save the form without committing to the database
            session = form.save(commit=False)

            # Set the mentor to the logged-in user
            session.mentor = request.user

            # Debugging: Check what additional_info contains
            print("Parsed additional_info:", form.cleaned_data['additional_info'])

            # Set the additional_info directly from the cleaned form data
            session.additional_info = form.cleaned_data['additional_info']

            # Debugging: Ensure additional_info is being set correctly
            print("Session additional_info before save:", session.additional_info)

            session.save()
            return redirect('student_profile', student.id)  # Redirect to the student's profile
        else:
            # Debugging: Show form errors
            print("Form errors:", form.errors)
            messages.error(request, "There was an error in the form.")
    else:
        form = SessionForm()

    return render(request, 'create_session.html', {'form': form})




@login_required
def session_list(request):
    mentor = request.user
    sessions = Session.objects.filter(mentor=request.user)
    username = mentor.username
    readable_name = username.replace('_', ' ').title()
    students = MentorshipData.objects.filter(faculty_mentor=readable_name)
    available_mentor_admins = MentorAdmin.objects.all()

    return render(request, 'session_list.html', {
        'sessions': sessions,
        'available_mentor_admins': available_mentor_admins
    })


def share_session_with_mentor_admin(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if request.method == "POST":
        # Get the selected mentor_admins from the form
        selected_admin_ids = request.POST.getlist('mentor_admins')
        
        # Add the selected mentor_admins to the session
        for admin_id in selected_admin_ids:
            mentor_admin = get_object_or_404(MentorAdmin, id=admin_id)
            session.mentor_admins.add(mentor_admin)
        
        messages.success(request, f'Session "{session.title}" shared with selected mentor admins.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('session_list')



from django.http import JsonResponse

@login_required
def progress(request):
    # Get the current mentor's username
    mentor_username = request.user.username.replace('_', ' ').title()

    # Filter students for this mentor
    mentor_students = MentorshipData.objects.filter(faculty_mentor=mentor_username)
    total_students = mentor_students.count()

    # Get counts for form analytics
    student_form_count = StudentForm.objects.filter(student__in=mentor_students).count()
    followup_form_count = StudentFollowupForm.objects.filter(student__in=mentor_students).count()
    total_forms = total_students*2
    remaining_forms = total_forms - student_form_count - followup_form_count

    # Query SE, TE, and BE students from MentorshipData
    se_students = mentor_students.filter(year="SE").values_list('roll_number', flat=True)
    te_students = mentor_students.filter(year="TE").values_list('roll_number', flat=True)
    be_students = mentor_students.filter(year="BE").values_list('roll_number', flat=True)

    # Fetch attendance data for SE, TE, and BE students from StudentForm
    attendance_data_se = StudentForm.objects.filter(rollno__in=se_students).values('atte_ise1', 'atte_mse', 'attendance')
    attendance_data_te = StudentForm.objects.filter(rollno__in=te_students).values('atte_ise1', 'atte_mse', 'attendance')
    attendance_data_be = StudentForm.objects.filter(rollno__in=be_students).values('atte_ise1', 'atte_mse', 'attendance')

    # Prepare chart data
    chart_data_se = {
        "labels": ["ISE 1", "MSE", "Overall Attendance"],
        "datasets": [
            {
                'label': 'SE Attendance',
                'data': [
                    sum(student['atte_ise1'] for student in attendance_data_se),
                    sum(student['atte_mse'] for student in attendance_data_se),
                    sum(student['attendance'] for student in attendance_data_se),
                ],
                'backgroundColor': 'rgba(255, 99, 132, 0.5)',
            }
        ]
    }

    chart_data_te = {
        "labels": ["ISE 1", "MSE", "Overall Attendance"],
        "datasets": [
            {
                'label': 'TE Attendance',
                'data': [
                    sum(student['atte_ise1'] for student in attendance_data_te),
                    sum(student['atte_mse'] for student in attendance_data_te),
                    sum(student['attendance'] for student in attendance_data_te),
                ],
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
            }
        ]
    }

    chart_data_be = {
        "labels": ["ISE 1", "MSE", "Overall Attendance"],
        "datasets": [
            {
                'label': 'BE Attendance',
                'data': [
                    sum(student['atte_ise1'] for student in attendance_data_be),
                    sum(student['atte_mse'] for student in attendance_data_be),
                    sum(student['attendance'] for student in attendance_data_be),
                ],
                'backgroundColor': 'rgba(75, 192, 192, 0.5)',
            }
        ]
    }

    # Analytics for StudentForm
    total_student_forms = StudentForm.objects.filter(student__in=mentor_students).count()
    forms_with_observations = StudentForm.objects.filter(
        student__in=mentor_students
    ).exclude(
        Q(nao='') & Q(ao='')
    ).count()
    forms_without_observations = total_student_forms - forms_with_observations

    # Analytics for StudentFollowupForm
    total_followup_forms = StudentFollowupForm.objects.filter(student__in=mentor_students).count()
    followup_forms_with_observations = StudentFollowupForm.objects.filter(
        student__in=mentor_students
    ).exclude(
        Q(nao='') & Q(ao='')
    ).count()
    followup_forms_without_observations = total_followup_forms - followup_forms_with_observations

    context = {
        'chart_data_se': chart_data_se,
        'chart_data_te': chart_data_te,
        'chart_data_be': chart_data_be,
        'student_form_count': student_form_count,
        'followup_form_count': followup_form_count,
        'remaining_forms': remaining_forms,
        'total_students': total_students,
        'total_student_forms': total_student_forms,
        'forms_with_observations': forms_with_observations,
        'forms_without_observations': forms_without_observations,
        'total_followup_forms': total_followup_forms,
        'followup_forms_with_observations': followup_forms_with_observations,
        'followup_forms_without_observations': followup_forms_without_observations,
    }

    return render(request, 'progress.html', context)



from django.http import JsonResponse

from django.http import JsonResponse
from django.db.models import Avg
def attendance_data_view(request):
    def get_attendance_data(year):
        students = MentorshipData.objects.filter(year=year).values_list('roll_number', flat=True)
        data = Student1.objects.filter(mentorship_data__roll_number__in=students).aggregate(
            avg_atte_ise1=Avg('atte_ise1'),
            avg_atte_mse=Avg('atte_mse'),
            avg_attendance=Avg('attendance')
        )
        
        return {
            "labels": ["ISE 1", "MSE", "Overall Attendance"],
            "datasets": [{
                'label': f'{year} Attendance',
                'data': [
                    data['avg_atte_ise1'] or 0,
                    data['avg_atte_mse'] or 0,
                    data['avg_attendance'] or 0
                ],
                'backgroundColor': 'rgba(255, 99, 132, 0.5)' if year == 'SE' else (
                    'rgba(54, 162, 235, 0.5)' if year == 'TE' else 'rgba(75, 192, 192, 0.5)'
                ),
            }]
        }

    def get_marks_data(year):
        students = MentorshipData.objects.filter(year=year).values_list('roll_number', flat=True)
        data = Student1.objects.filter(mentorship_data__roll_number__in=students).aggregate(
            avg_cts=Avg('cts'),
            avg_ise1=Avg('ise1'),
            avg_mse=Avg('mse'),
            avg_semcgpa=Avg('semcgpa')
        )
        
        # Adjust CGPA to be on a similar scale as percentage scores
        adjusted_cgpa = data['avg_semcgpa'] * 10 if data['avg_semcgpa'] else 0
        
        return {
            "labels": ["CTS", "ISE 1", "MSE", "Sem CGPA (x10)"],
            "datasets": [{
                'label': f'{year} Marks',
                'data': [
                    data['avg_cts'] or 0,
                    data['avg_ise1'] or 0,
                    data['avg_mse'] or 0,
                    adjusted_cgpa
                ],
                'backgroundColor': 'rgba(255, 206, 86, 0.5)' if year == 'SE' else (
                    'rgba(75, 192, 192, 0.5)' if year == 'TE' else 'rgba(153, 102, 255, 0.5)'
                ),
            }]
        }

    attendance_data = {
        'se': get_attendance_data('SE'),
        'te': get_attendance_data('TE'),
        'be': get_attendance_data('BE')
    }

    marks_data = {
        'se': get_marks_data('SE'),
        'te': get_marks_data('TE'),
        'be': get_marks_data('BE')
    }
    
    return JsonResponse({
        'attendance': attendance_data,
        'marks': marks_data
    })




@login_required
def main_forms_to_observe(request):
    mentor = request.user
    mentor_username = mentor.username.replace('_', ' ').title()
    mentor_students = MentorshipData.objects.filter(faculty_mentor=mentor_username)
    
    forms_without_observations = StudentForm.objects.filter(
        student__in=mentor_students,
        nao='',
        ao=''
    ).order_by('-date')

    context = {
        'forms': forms_without_observations,
        'form_type': 'Main',
        'mentor': mentor,
    }
    return render(request, 'forms_to_observe.html', context)

@login_required
def followup_forms_to_observe(request):
    mentor = request.user
    mentor_username = mentor.username.replace('_', ' ').title()
    mentor_students = MentorshipData.objects.filter(faculty_mentor=mentor_username)
    
    followup_forms_without_observations = StudentFollowupForm.objects.filter(
        student__in=mentor_students,
        nao='',
        ao=''
    ).order_by('-date')

    context = {
        'forms': followup_forms_without_observations,
        'form_type': 'Follow-up',
        'mentor': mentor,
    }
    return render(request, 'forms_to_observe.html', context)

@login_required
def remaining_forms(request):
    mentor = request.user
    mentor_username = mentor.username.replace('_', ' ').title()
    mentor_students = MentorshipData.objects.filter(faculty_mentor=mentor_username)
    
    students_with_missing_forms = []
    
    for student in mentor_students:
        main_form = StudentForm.objects.filter(student=student).exists()
        followup_form = StudentFollowupForm.objects.filter(student=student).exists()
        
        if not main_form or not followup_form:
            missing_forms = []
            if not main_form:
                missing_forms.append('Main')
            if not followup_form:
                missing_forms.append('Follow-up')
            
            students_with_missing_forms.append({
                'student': student,
                'missing_forms': missing_forms
            })
    
    context = {
        'students_with_missing_forms': students_with_missing_forms,
        'mentor': mentor,
    }
    return render(request, 'remaining_forms.html', context)







