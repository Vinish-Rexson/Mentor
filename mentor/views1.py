from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import *
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode, base64
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from docxtpl import DocxTemplate
import secrets 


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
def mentor_dashboard(request):
    students = Student.objects.all()
    context = {
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students]
    }
    return render(request, 'mentor_dashboard.html',context)

def student_detail(request):
    
    # Fetch all students from the database
    students = Student.objects.all()
    
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


from django.utils import timezone
import secrets

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
    student = get_object_or_404(Student, id=student_id)
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
    student = get_object_or_404(Student, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)

    # Get current date for display
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")

    # Validate the token from GET or POST
    token = request.GET.get('token') or request.POST.get('token')
    
    # Check if token is valid and not expired
    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    # Check if a form for this student's roll number already exists
    existing_submission = StudentForm.objects.filter(rollno=student.roll_number).first()

    if existing_submission:
        # If the form was already submitted, return an HttpResponse
        return HttpResponse(f"Form already submitted for roll number {student.roll_number}.", status=403)

    if request.method == 'POST':
        # If it's a POST request, populate the form with POST data
        form = StudentSemForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit immediately to set additional fields
            student_form = form.save(commit=False)
            student_form.name = student.name  # Automatically set student name
            student_form.rollno = student.roll_number  # Automatically set student roll number
            student_form.mentor_name = mentor.username  # Automatically set mentor's name
            student_form.save()  # Save the form to the database

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
    student = get_object_or_404(Student, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Fetch the mentor based on the ID in the URL

    # Get the current date in both formats
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")

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
            student_form.save()
            print("Form successfully saved for student:", student_form.rollno)  # Debugging statement

            return render(request, 'form_submitted.html', {'rollno': student_form.rollno})
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


def download_follow_document(request, rollno):
    # Fetch all entries with the given rollno
    forms = StudentFollowupForm.objects.filter(rollno=rollno)

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
    "mentor_name":form.mentor_name,
}

    
    # Call the document generation function
    return generate_follow_document(form_dict)



def generate_follow_document(form_dict):
    # Find the template document (adjust the path according to your project structure)
    doc_path = finders.find('followup_form.docx')
    
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
    'sem': "3",                    # Static semester number; adjust as needed
    'semcgpa': form_dict["semcgpa"],
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






def followup_form_student_generate(request, student_id, mentor_id):
    # Fetch the student and mentor based on their IDs
    student = get_object_or_404(Student, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)

    # Get current date for display
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")

    # Validate the token from GET or POST
    token = request.GET.get('token') or request.POST.get('token')

    # Check if token is valid and not expired
    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    # Check if a follow-up form for this student already exists
    existing_submission = StudentFollowupForm.objects.filter(rollno=student.roll_number).first()

    if existing_submission:
        # If a form was already submitted for this student, return an error response
        return HttpResponse(f"Follow-up form already submitted for {student.name} (Roll No: {student.roll_number}).", status=403)

    if request.method == 'POST':
        # If it's a POST request, populate the form with POST data
        form = StudentFollowup_Form(request.POST)
        if form.is_valid():
            # Save the form but don't commit immediately to set additional fields
            student_form = form.save(commit=False)
            student_form.student = student  # Automatically associate the student
            student_form.mentor = mentor  # Automatically associate the mentor
            student_form.save()  # Save the form to the database

            # Redirect to a success page or confirmation that the form is filled
            return render(request, 'follow_form_submitted.html', {'rollno': student.roll_number})
        else:
            # If the form is invalid, stay on the same page and show errors
            return render(request, 'followup_form_student_view.html', {
                'form': form,  # Return the form with errors
                'student': student,
                'mentor': mentor,
                'date': form_date,
                'display_date': display_date,
                'token': token  # Pass the token to the template for security
            })
    else:
        # For GET requests, return an empty form
        form = StudentFollowup_Form()

    # Render the form for GET requests
    return render(request, 'followup_form_student_view.html', {
        'form': form,
        'student': student,
        'mentor': mentor,
        'date': form_date,
        'display_date': display_date,
        'token': token  # Pass the token to the template
    })

from django.utils import timezone

def followup_form_student(request, student_id, mentor_id):
    student = get_object_or_404(Student, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Fetch the mentor based on the ID in the URL

    # Get the current date in both formats
    display_date = timezone.now().strftime("%d/%m/%Y")
    form_date = timezone.now().strftime("%Y-%m-%d")

    if request.method == 'POST':
        form = StudentFollowup_Form(request.POST)
        if form.is_valid():
            print("valid")
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.mentor = mentor  # Set the mentor based on the URL
            student_form.save()

            return render(request, 'follow_form_submitted.html', {'rollno': student_form.rollno})
        else:
            # Handling the case when form is not valid
            return render(request, 'followup_form.html', {
                'form': form,
                'student': student,
                'mentor': mentor,  # Pass the mentor (user) to the template
                'date': form_date,
                'display_date': display_date,
                'errors': form.errors  # Display form errors
            })
    else:
        # Corrected the form instantiation to use StudentFollowup_Form
        form = StudentFollowup_Form()

    return render(request, 'followup_form.html', {
        'form': form,
        'student': student,
        'mentor': mentor,  # Pass the mentor to the template
        'date': form_date,
        'display_date': display_date
    })



def generate_qr_followup(request, student_id, mentor_id):
    student = get_object_or_404(Student, id=student_id)
    mentor = get_object_or_404(User, id=mentor_id)  # Get mentor object

    # Check if the token has expired or doesn't exist
    if not student.token or student.is_token_expired():
        # Generate a new token and update the timestamp
        student.token = secrets.token_urlsafe()
        student.token_created_at = timezone.now()
        student.save()

    # Generate the form URL with student_id, mentor_id, and token
    form_url = request.build_absolute_uri(f"/followup_form/generate/{student.id}/{mentor.id}/?token={student.token}")
    
    # Generate the QR code for the URL
    qr_code = generate_qr_code(form_url)
    
    return render(request, 'qr_code_page.html', {
        'student': student,
        'mentor': mentor,  # Pass mentor info to the template if needed
        'qr_code': qr_code
    })




def SE(request):
    se_students = Student.objects.filter(year__iexact="SE")  # using __iexact for case-insensitivity
    mentor = request.user

    context = {
        'student_count': se_students.count(),
        'students': se_students,
        'student_names': [student.name for student in se_students],
        'mentor': mentor,
    }

    return render(request, 'se.html', context)


def TE(request):
    te_students = Student.objects.filter(year__iexact="TE ")  # using __iexact for case-insensitivity
    
    mentor = request.user

    context = {
        'student_count': te_students.count(),
        'students': te_students,
        'student_names': [student.name for student in te_students],
        'mentor': mentor,
    }

    return render(request, 'te.html', context)


def BE(request):
    be_students = Student.objects.filter(year__iexact="BE")  # using __iexact for case-insensitivity
    mentor = request.user

    context = {
        'student_count': be_students.count(),
        'students': be_students,
        'student_names': [student.name for student in be_students],
        'mentor': mentor,
    }

    return render(request, 'be.html', context)


def form_dashboard(request):
    
    # Fetch all students from the database
    students = Student.objects.all()
    
    # Create a dictionary to pass to the template
    context = {
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students],

    }
    
    # Render the template with the context
    return render(request, 'form_dashboard.html', context)

def dashboard_home(request):
    return render(request, 'dashboard_home.html')


