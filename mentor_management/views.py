from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.models import Group

class CustomLoginView(LoginView):
    def get_redirect_url(self):
        user = self.request.user
        user_groups = user.groups.all()  # Get all groups the user belongs to
        
        # Debugging: Print group names to verify
        print("User groups:", [group.name for group in user_groups])

        # Check if the user belongs to the 'Mentor_admin' group first
        if user.groups.filter(name='Mentor_admin').exists():
            return '/mentor_admin/dashboard/'

        # Check if the user belongs to the 'Mentor' group
        elif user.groups.filter(name='Mentor').exists():
            return '/dashboard/'

        # Default fallback if no group is found
        return '/dashboard/'
