from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .forms import MentorAdminSignUpForm
from .models import MentorAdmin
from mentor.models import *
from django.contrib import messages

# Mentor Admin Signup View
def mentor_admin_signup(request):
    if request.method == 'POST':
        form = MentorAdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            mentor_group = Group.objects.get_or_create(name='Mentor_admin')
            mentor_group[0].user_set.add(user)
            login(request, user)
            return redirect('mentor_admin_dashboard')
    else:
        form = MentorAdminSignUpForm()
    return render(request, 'mentor_admin/signup.html', {'form': form})

# Mentor Admin Dashboard View
@login_required
def mentor_admin_dashboard(request, student_id=None):
    mentor = request.user
    # Fetch the students related to this mentor
    students = MentorshipData.objects.all()

    total_forms = (
        StudentForm.objects.filter(student__in=students).count() +
        StudentFollowupForm.objects.filter(student__in=students).count()
    )
    total_sessions = Session.objects.all().count()
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

    return render(request, 'mentor_admin/dashboard.html', context)


@login_required
def recents(request):
    mentor = request.user
    latest_forms = StudentForm.objects.all().order_by('-date')[:3]  # Now orders by both date and time
    latest_followupforms = StudentFollowupForm.objects.all().order_by('-date')[:3]
    recents = {
        'mainform': latest_forms,
        'followupform': latest_followupforms
    }
    return recents



# View to list all mentors
@login_required
def list_mentors(request):
    mentors = MentorshipData.objects.all()
    return render(request, 'mentor_admin/list_mentors.html', {'mentors': mentors})

# View to edit mentor details
@login_required
def edit_mentor(request, mentor_id):
    mentor = MentorAdmin.objects.get(id=mentor_id)
    if request.method == 'POST':
        form = MentorAdminSignUpForm(request.POST, instance=mentor.user)
        if form.is_valid():
            form.save()
            return redirect('list_mentors')
    else:
        form = MentorAdminSignUpForm(instance=mentor.user)
    return render(request, 'mentor_admin/edit_mentor.html', {'form': form, 'mentor': mentor})

# View to delete a mentor
@login_required
def delete_mentor(request, mentor_id):
    mentor = MentorAdmin.objects.get(id=mentor_id)
    if request.method == 'POST':
        mentor.user.delete()
        return redirect('list_mentors')
    return render(request, 'mentor_admin/delete_mentor.html', {'mentor': mentor})





def mentor_admin_sessions(request):
    # Get the logged-in mentor_admin
    mentor_admin = request.user.mentoradmin

    # Fetch sessions shared with this mentor_admin
    shared_sessions = mentor_admin.shared_sessions.all()

    return render(request, 'mentor_admin/mentor_admin_sessions.html', {
        'shared_sessions': shared_sessions,
    })

@login_required
def mentors_list(request):
    mentors = User.objects.filter(groups__name='Mentor')
    
    mentor_data = []
    for mentor in mentors:
        students = MentorshipData.objects.filter(faculty_mentor=mentor.username.replace('_', ' ').title())
        mentor_data.append({
            'mentor': mentor,
            'students': students
        })
    
    context = {
        'mentor_data': mentor_data
    }
    return render(request, 'mentor_admin/mentors_list.html', context)

@login_required
def add_student(request, mentor_id):
    mentor = get_object_or_404(User, id=mentor_id)
    if request.method == 'POST':
        # Process the form data
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        year = request.POST.get('year')
        division = request.POST.get('division')
        
        MentorshipData.objects.create(
            name=name,
            roll_number=roll_number,
            year=year,
            division=division,
            faculty_mentor=mentor.username.replace('_', ' ').title()
        )
        messages.success(request, f"Student {name} added successfully to {mentor.username}'s list.")
        return redirect('mentors_list')
    
    return render(request, 'mentor_admin/add_student.html', {'mentor': mentor})

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    if request.method == 'POST':
        # Process the form data
        student.name = request.POST.get('name')
        student.roll_number = request.POST.get('roll_number')
        student.year = request.POST.get('year')
        student.division = request.POST.get('division')
        student.save()
        messages.success(request, f"Student {student.name} updated successfully.")
        return redirect('mentors_list')
    
    return render(request, 'mentor_admin/edit_student.html', {'student': student})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(MentorshipData, id=student_id)
    if request.method == 'POST':
        mentor_name = student.faculty_mentor
        student.delete()
        messages.success(request, f"Student {student.name} removed from {mentor_name}'s list.")
        return redirect('mentors_list')
    
    return render(request, 'mentor_admin/delete_student.html', {'student': student})



from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from mentor.models import MentorshipData
from django.contrib.auth.decorators import user_passes_test

# Check if user is mentor_admin
def is_mentor_admin(user):
    return user.is_authenticated  # Customize this check based on your project

# View to increment the semester for students of a specific year
@user_passes_test(is_mentor_admin)
def change_sem_for_year(request, action, year):
    if request.method == 'POST':
        # Map years to their corresponding semester ranges
        year_to_semester = {
            'FE': [1, 2],
            'SE': [3, 4],
            'TE': [5, 6],
            'BE': [7, 8]
        }

        # Get the students who belong to the selected year
        students_in_selected_year = MentorshipData.objects.filter(year=year)
        updated_students = 0

        # Increment or decrement semesters for the students in the selected year
        for student in students_in_selected_year:
            if action == 'increment' and student.sem < 8:
                student.sem += 1
            elif action == 'decrement' and student.sem > 1:
                student.sem -= 1

            # Automatically update the year based on the new sem
            student.set_year_based_on_sem()
            student.save()
            updated_students += 1

        # Now, update the rest of the students who are not in the selected year
        for year_key, sem_range in year_to_semester.items():
            if year_key != year:  # Exclude the selected year group
                other_students = MentorshipData.objects.filter(year=year_key)
                for student in other_students:
                    # Increment or decrement accordingly based on the action
                    if action == 'increment' and student.sem < 8:
                        student.sem += 1
                    elif action == 'decrement' and student.sem > 1:
                        student.sem -= 1

                    # Automatically update the year based on the new sem
                    student.set_year_based_on_sem()
                    student.save()

        if action == 'increment':
            messages.success(request, f'Successfully incremented semester for {updated_students} students in {year}, and adjusted others accordingly.')
        else:
            messages.success(request, f'Successfully decremented semester for {updated_students} students in {year}, and adjusted others accordingly.')

        return redirect('mentor_admin_dashboard')  # Redirect to mentor admin dashboard

    return HttpResponse(status=405)  # Return method not allowed if it's not a POST request

