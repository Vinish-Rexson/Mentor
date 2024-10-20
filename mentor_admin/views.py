from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import MentorAdminSignUpForm
from .models import MentorAdmin

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
def mentor_admin_dashboard(request):
    return render(request, 'mentor_admin/dashboard.html')

# View to list all mentors
@login_required
def list_mentors(request):
    mentors = MentorAdmin.objects.all()
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
