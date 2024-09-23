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



# QR code generation function (same as before)
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
def generate_qr(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form_url = request.build_absolute_uri(f"/form/{student.id}/")
    qr_code = generate_qr_code(form_url)
    
    return render(request, 'qr_code_page.html', {'student': student, 'qr_code': qr_code})




def form_student(request, student_id):
    # Fetch the student object or return 404 if not found
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        # Bind the form with POST data
        form = StudentSemForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            student_form = form.save(commit=False)
            # Assign the student to the form data if needed
            student_form.student = student  # Assuming there's a ForeignKey to Student
            student_form.save()
            # Pass rollno to the success template
            return render(request, 'form_submitted.html', {'rollno': student_form.rollno}) 
        else:
            # If form is invalid, render the form with error messages
            return render(request, 'form.html', {'form': form, 'student': student})
    else:
        # If it's a GET request, display the empty form
        form = StudentSemForm()

    # Render the form page
    return render(request, 'form.html', {'form': form, 'student': student})



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
        "sem3cgpa": form.sem3cgpa,
        "question1": form.question1,
        "question2": form.question2
    }
    
    # Call the document generation function
    return generate_document(form_dict)



def generate_document(form_dict):
    # Find the template document (adjust the path according to your project structure)
    doc_path = finders.find('mentor-form-trial.docx')
    
    # Load the template using docxtpl
    doc = DocxTemplate(doc_path)
    
    # Context for the template
    context = {
        'name': form_dict["name"],
        'rollno': form_dict["rollno"],
        'branch': "Comps",            # Static branch value; adjust as needed
        'semno': "3",                 # Static semester number; adjust as needed
        'sem3cgpa': form_dict["sem3cgpa"],
        'line1': form_dict["question1"],  # Counseling/Team info
        'line2': form_dict["question2"],  # Co-curricular events info
        'attendance': form_dict["attendance"]
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