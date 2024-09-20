# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import MentorSignUpForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

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
