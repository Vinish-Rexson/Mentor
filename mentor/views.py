# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import MentorSignUpForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import *


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
    return render(request, 'mentor_dashboard.html')


def mentor_dashboard(request):
    # Fetch all students from the database
    students = Student.objects.all()
    
    # Create a dictionary to pass to the template
    context = {
        'student_count': students.count(),
        'students': students,
        'student_names': [student.name for student in students]
    }
    
    # Render the template with the context
    return render(request, 'mentor_dashboard.html', context)


def student_form(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        # Handle form submission here
        # form = YourForm(request.POST)
        if form.is_valid():
            # Process form data
            form.save()
            # Redirect or return a success message
    # else:
        # form = YourForm()  # Replace YourForm with the actual form you're using

    return render(request, 'form_template.html', {'student': student})

def student_detail(request):
    return render(request, 'student_detail.html')

def dashboard(request):
    return render(request, 'mentor_dashboard.html')