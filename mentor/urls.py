# urls.py
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/', views.mentor_signup, name='mentor_signup'),
    path('dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/<int:student_id>/', views.form_student, name='form_student'),
    path('generate_qr/<int:student_id>/', views.generate_qr, name='generate_qr'),
    path('download/<str:rollno>/', views.download_document, name='download_document'),
]
