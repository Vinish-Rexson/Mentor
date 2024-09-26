# urls.py
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/', views.mentor_signup, name='mentor_signup'),
    path('dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/<int:student_id>/', views.form_student_generate, name='form_student'),
    path('form/<int:student_id>', views.form_student, name='form_student'),
    path('generate_qr/<int:student_id>/', views.generate_qr, name='generate_qr'),
    path('download/<str:rollno>/', views.download_document, name='download_document'),
    path('', views.Redirect, name='Redirect'),
    path('student_detail/', views.student_detail, name='student_detail'),
    path('student_detail/SE', views.SE, name='SE'),
    path('student_detail/TE', views.TE, name='TE'),
    path('student_detail/BE', views.BE, name='BE'),
    path('form_dashboard/', views.form_dashboard, name='form_dashboard'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
]


