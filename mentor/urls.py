# urls.py
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/', views.mentor_signup, name='mentor_signup'),
    path('dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/generate/<int:student_id>/<int:mentor_id>/', views.form_student_generate, name='form_student_generate'),
    path('form/<int:student_id>/<int:mentor_id>/', views.form_student, name='form_student'),
    path('generate_qr/<int:student_id>/<int:mentor_id>/', views.generate_qr, name='generate_qr'),
    path('download/<str:rollno>/', views.download_document, name='download_document'),

    path('followup_form/generate/<int:student_id>/<int:mentor_id>/', views.followup_form_student_generate, name='followup_form_student_generate'),
    path('followup_form/<int:student_id>/<int:mentor_id>/', views.followup_form_student, name='followup_form_student'),
    path('generate_qr_followup/<int:student_id>/<int:mentor_id>/', views.generate_qr_followup, name='generate_qr_followup'),
    
    path('download/<str:rollno>/', views.download_document, name='download_document'),
    path('follow/download/<str:rollno>/', views.download_follow_document, name='download_follow_document'),
    path('', views.Redirect, name='Redirect'),
    path('student_detail/', views.student_detail, name='student_detail'),
    path('student_detail/SE', views.SE, name='SE'),
    path('student_detail/TE', views.TE, name='TE'),
    path('student_detail/BE', views.BE, name='BE'),
    path('form_dashboard/', views.form_dashboard, name='form_dashboard'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
]


