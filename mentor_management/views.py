from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
import os

class CustomLoginView(LoginView):
    def get_redirect_url(self):
        user = self.request.user

        # Check if the user belongs to the 'Mentor_admin' group first
        if user.groups.filter(name='Mentor_admin').exists():
            return '/mentor_admin/dashboard/'

        # Check if the user belongs to the 'Mentor' group
        elif user.groups.filter(name='Mentor').exists():
            return '/dashboard/'

        # Default fallback if no group is found
        return '/dashboard/'

def custom_csrf_failure(request, reason=""):
    return render(request, '403_csrf.html', status=403)

def test_media(request):
    media_root = settings.MEDIA_ROOT
    profile_pictures_path = os.path.join(media_root, 'profile_pictures')
    
    media_files = os.listdir(media_root)
    profile_pictures = os.listdir(profile_pictures_path) if os.path.exists(profile_pictures_path) else []
    
    response = f"Media files: {media_files}\n\n"
    response += f"Profile pictures: {profile_pictures}\n\n"
    response += f"MEDIA_ROOT: {media_root}\n"
    response += f"MEDIA_URL: {settings.MEDIA_URL}\n"
    
    return HttpResponse(response, content_type='text/plain')

def serve_profile_picture(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'profile_pictures', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    raise Http404("File not found")
