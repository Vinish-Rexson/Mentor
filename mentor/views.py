from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.staticfiles import finders

from .forms import *
from .forms import StudentFollowup_Form
from .models import *

from io import BytesIO
import qrcode, base64, secrets
from docxtpl import DocxTemplate



def Redirect(request):
    return redirect('accounts/login')


def mentor_signup(request):
    if request.method == 'POST':
        form = MentorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and automatically assign to Mentor group
            mentor_group = Group.objects.get_or_create(name='MENTOR')
            mentor_group[0].user_set.add(user)
            login(request, user)  # Log in the new user
            return redirect('mentor_dashboard')  # Redirect to the mentor's dashboard
    else:
        form = MentorSignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def mentor_dashboard(request, student_id=None):
    mentor = request.user
    if student_id:
        student = get_object_or_404(MentorshipData, id=student_id)
    else:
        student = None  # or handle this case as needed
    
    readable_name = mentor.username.replace('_', ' ').title()
    students = MentorshipData.objects.filter(faculty_mentor=readable_name)
    
    # Call recents and unpack it directly into context
    recent_forms = recents(request)
    
    context = {
        'student': student,
        'mentor': mentor,
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students],
        'recent_mainform': recent_forms['mainform'],        # Main form
        'recent_followupform': recent_forms['followupform'] # Follow-up form
    }
    
    return render(request, 'mentor_dashboard.html', context)



@login_required
def recents(request):
    latest_forms = StudentForm.objects.all().order_by('-date')[:3]  # Now orders by both date and time
    latest_followupforms = StudentFollowupForm.objects.order_by('-date')[:3]
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


def form_student_generate(request, student_id, mentor_id):
    # Fetch the student and mentor based on their IDs
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)

    # Get current date for display
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()#pass current datetime to form models to pass recent forms
    # Validate the token from GET or POST
    token = request.GET.get('token') or request.POST.get('token')
    
    # Check if token is valid and not expired
    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    # Check if a form for this student's roll number already exists
    existing_submission = StudentForm.objects.filter(rollno=student.roll_number).first()

    if existing_submission:
        # If the form was already submitted, return an HttpResponse
        # return HttpResponse(f"Form already submitted for roll number {student.roll_number}.", status=403)
        return render(request,"already_submit.html",{'student':student})
    if request.method == 'POST':
        # If it's a POST request, populate the form with POST data
        form = StudentSemForm(request.POST)
        
        if form.is_valid():
            # Save the form but don't commit immediately to set additional fields
            student_form = form.save(commit=False)
            student_form.name = student.name  # Automatically set student name
            student_form.rollno = student.roll_number  # Automatically set student roll number
            student_form.mentor_name = mentor.username  # Automatically set mentor's name
            student_form.date = form_datetime#pass current datetime to form models to pass recent forms
            student_form.save()  # Save the form to the database
            
            
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
                'token': token  # Pass the token to the template for security
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
        'token': token  # Pass the token to the template
    })

def form_student(request, student_id, mentor_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Fetch the mentor based on the ID in the URL

    # Get the current date in both formats
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")
    form_datetime = timezone.now()#pass current datetime to form models to pass recent forms

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
                'success_message': 'Form has been successfully updated for roll number ' + student_form.rollno  # Success message
            })
        else:
            print("Form errors:", form.errors)  # Debugging statement
            return render(request, 'form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,  # Pass the mentor (user) to the template
                'date': form_date,
                'display_date': display_date,
                'errors': form.errors
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
        'display_date': display_date
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
                'success_message': 'Follow Form has been successfully updated for roll number ' + student_form.rollno  # Success message
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
                'errors': form.errors
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
        'display_date': display_date
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
    # te_students = MentorshipData.objects.filter(year__iexact="TE",faculty_mentor=readable_name)
    te_students = Student.objects.filter(year = "TE ")
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
    # be_students = MentorshipData.objects.filter(year__iexact="BE",faculty_mentor=readable_name)
    be_students = Student.objects.filter(year = "BE")

    context = {
        'student_count': be_students.count(),
        'students': be_students,
        'student_names': [student.name for student in be_students],
        'mentor': mentor,
    }

    return render(request, 'se.html', context)


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    # student = get_object_or_404(Student, id=student_id)
    mentor = request.user
    
    context = {
        'student': student,
        'mentor': mentor,   
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
from django.contrib import messages
import json
from .forms import SessionForm

@login_required
def create_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = request.user  # Set the logged-in user as mentor
            
            additional_info_text = form.cleaned_data['additional_info']
            
            try:
                additional_info_dict = json.loads(additional_info_text)
                session.additional_info = additional_info_dict
            except (ValueError, TypeError):
                session.additional_info = {"note": additional_info_text}
                messages.warning(request, "Additional Info was not valid JSON, stored as a note.")
            
            session.save()
            return redirect('session_list')
    else:
        form = SessionForm()

    return render(request, 'create_session.html', {'form': form})



@login_required
def session_list(request):
    sessions = Session.objects.filter(mentor=request.user)
    return render(request, 'session_list.html', {'sessions': sessions})


# views.py
from django.shortcuts import render
from .models import StudentForm, MentorshipData
from django.http import JsonResponse

def progress(request):
    # Query SE, TE, and BE students from MentorshipData
    se_students = MentorshipData.objects.filter(year="SE").values_list('roll_number', flat=True)
    te_students = MentorshipData.objects.filter(year="TE").values_list('roll_number', flat=True)
    be_students = MentorshipData.objects.filter(year="BE").values_list('roll_number', flat=True)

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

    return render(request, 'progress.html', {
        'chart_data_se': chart_data_se,
        'chart_data_te': chart_data_te,
        'chart_data_be': chart_data_be,
    })



from django.http import JsonResponse

from django.http import JsonResponse

def attendance_data_view(request):
    # Function to get attendance data percentage for a specific year
    def get_attendance_data(year):
        # Query mentorship data for students in the given year
        students = MentorshipData.objects.filter(year=year).values_list('roll_number', flat=True)

        # Fetch attendance data from the Student1 model
        attendance_data = Student1.objects.filter(mentorship_data__roll_number__in=students).values('atte_ise1', 'atte_mse', 'attendance')

        # Get total number of students in that year
        total_students = attendance_data.count()

        # Avoid division by zero if there are no students
        if total_students == 0:
            return {
                "labels": ["ISE 1", "MSE", "Overall Attendance"],
                "datasets": [
                    {
                        'label': f'{year} Attendance',
                        'data': [0, 0, 0],  # No data available
                        'backgroundColor': 'rgba(255, 99, 132, 0.5)' if year == 'SE' else (
                            'rgba(54, 162, 235, 0.5)' if year == 'TE' else 'rgba(75, 192, 192, 0.5)'
                        ),
                    }
                ]
            }

        # Calculate the sum of attendance values
        total_atte_ise1 = sum(student['atte_ise1'] for student in attendance_data)
        total_atte_mse = sum(student['atte_mse'] for student in attendance_data)
        total_attendance = sum(student['attendance'] for student in attendance_data)

        # Calculate percentages
        percentage_ise1 = (total_atte_ise1 / (total_students * 100)) * 100  # ISE 1 attendance percentage
        percentage_mse = (total_atte_mse / (total_students * 100)) * 100  # MSE attendance percentage
        percentage_overall = (total_attendance / (total_students * 100)) * 100  # Overall attendance percentage

        # Prepare chart data with percentage
        return {
            "labels": ["ISE 1", "MSE", "Overall Attendance"],
            "datasets": [
                {
                    'label': f'{year} Attendance',
                    'data': [percentage_ise1, percentage_mse, percentage_overall],
                    'backgroundColor': 'rgba(255, 99, 132, 0.5)' if year == 'SE' else (
                        'rgba(54, 162, 235, 0.5)' if year == 'TE' else 'rgba(75, 192, 192, 0.5)'
                    ),
                }
            ]
        }

    # Get data for SE, TE, and BE
    chart_data_se = get_attendance_data('SE')
    chart_data_te = get_attendance_data('TE')
    chart_data_be = get_attendance_data('BE')
    
    # Prepare the final response with the percentage data
    return JsonResponse({
        'se': chart_data_se,
        'te': chart_data_te,
        'be': chart_data_be
    })



