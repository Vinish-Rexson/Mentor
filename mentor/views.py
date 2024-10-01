# views.py
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


# QR code generation function
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



# View to generate and display QR code
import secrets
from django.utils import timezone

def generate_qr(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Check if the token has expired
    if not student.token or student.is_token_expired():
        # Generate a new token and update the timestamp
        student.token = secrets.token_urlsafe()
        student.token_created_at = timezone.now()
        student.save()

    form_url = request.build_absolute_uri(f"/form/{student.id}/?token={student.token}")
    qr_code = generate_qr_code(form_url)
    return render(request, 'qr_code_page.html', {'student': student, 'qr_code': qr_code})



#student side
def form_student_generate(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Validate token
    token = request.GET.get('token')
    if not token or token != student.token or student.is_token_expired():
        return HttpResponse("Invalid or expired token", status=403)

    if request.method == 'POST':
        form = StudentSemForm(request.POST)
        if form.is_valid():
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.save()
            return render(request, 'form_submitted.html', {'rollno': student_form.rollno}) 
        else:
            return render(request, 'form.html', {'form': form, 'student': student})
    else:
        form = StudentSemForm()

    return render(request, 'form.html', {'form': form, 'student': student})


def form_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    forms = StudentForm.objects.all()


    forms = StudentForm.objects.all()  # Assuming rollno links to the correct form
    if forms.exists():
        form_instance = forms.first()  # Get the first form instance (customize as needed)
        formatted_date = form_instance.date.strftime("%d/%m/%Y") if form_instance.date else ""
    else:
        formatted_date = ""
    

    if request.method == 'POST':
        form = StudentSemForm(request.POST)
        if form.is_valid():
            student_form = form.save(commit=False)
            student_form.student = student
            student_form.save()
            return render(request, 'form_submitted.html', {'rollno': student_form.rollno}) 
        else:
            print(form.errors)
            return render(request, 'form.html', {'form': form, 'student': student, 'date':formatted_date})
    else:
        form = StudentSemForm()

    return render(request, 'form.html', {'form': form, 'student': student, 'date':formatted_date})





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
    'line10': form_dict["question10"], # Higher studies plans
    'line11': form_dict["question11"], # Job offer details
    'date': formatted_date,
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



def SE(request):
    se_students = Student.objects.filter(year="SE")
    # students = Student.objects.all()
    
    # Create a dictionary to pass to the template
    context = {
        'student_count': se_students.count(),
        'students': se_students,
        'student_names': [student.name for student in se_students],

    }
    return render(request, 'se.html', {'se_students': se_students})


def TE(request):
    te_students = Student.objects.filter(year="TE ")
    context = {
        'student_count': te_students.count(),
        'students': te_students,
        'student_names': [student.name for student in te_students],

    }
    return render(request, 'te.html', {'te_students': te_students})


def BE(request):
    be_students = Student.objects.filter(year="BE")
    context = {
        'student_count': be_students.count(),
        'students': be_students,
        'student_names': [student.name for student in be_students],

    }
    return render(request, 'be.html', {'be_students': be_students})

def form_dashboard(request):
    return render(request, 'form_dashboard.html')



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


