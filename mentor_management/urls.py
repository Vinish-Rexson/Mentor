"""
URL configuration for mentor_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import CustomLoginView, test_media, serve_profile_picture 
from django.conf.urls import handler400, handler403, handler404, handler500
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os


# Custom error views
def custom_bad_request(request, exception):
    return render(request, '400.html', status=400)

def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)

def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

def custom_server_error(request):
    return render(request, '500.html', status=500)


# Assign custom views
handler400 = 'mentor_management.urls.custom_bad_request'
handler403 = 'mentor_management.urls.custom_permission_denied'
handler404 = 'mentor_management.urls.custom_page_not_found'
handler500 = 'mentor_management.urls.custom_server_error'
CSRF_FAILURE_VIEW = 'mentor_management.views.custom_csrf_failure'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mentor.urls')),
    path('mentor_admin/', include('mentor_admin.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('test-media/', test_media, name='test_media'),
    path('media/profile_pictures/<str:filename>', serve_profile_picture, name='serve_profile_picture'),
]

# Add this at the end of the file
if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
