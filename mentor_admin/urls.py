from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.mentor_admin_signup, name='mentor_admin_signup'),
    path('dashboard/', views.mentor_admin_dashboard, name='mentor_admin_dashboard'),
    path('sessions/', views.mentor_admin_sessions, name='mentor_admin_sessions'),
]
