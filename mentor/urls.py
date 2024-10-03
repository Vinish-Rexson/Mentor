# urls.py
from django.urls import path,include
from . import views1

urlpatterns = [
    path('signup/', views1.mentor_signup, name='mentor_signup'),
    path('dashboard/', views1.mentor_dashboard, name='mentor_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/generate/<int:student_id>/<int:mentor_id>/', views1.form_student_generate, name='form_student_generate'),
    path('form/<int:student_id>/<int:mentor_id>/', views1.form_student, name='form_student'),
    path('generate_qr/<int:student_id>/<int:mentor_id>/', views1.generate_qr, name='generate_qr'),
    path('download/<str:rollno>/', views1.download_document, name='download_document'),

    path('followup_form/generate/<int:student_id>/<int:mentor_id>/', views1.followup_form_student_generate, name='followup_form_student_generate'),
    path('followup_form/<int:student_id>/<int:mentor_id>/', views1.followup_form_student, name='followup_form_student'),
    path('generate_qr_followup/<int:student_id>/<int:mentor_id>/', views1.generate_qr_followup, name='generate_qr_followup'),
    
    path('download/<str:rollno>/', views1.download_document, name='download_document'),
    path('follow/download/<str:rollno>/', views1.download_follow_document, name='download_follow_document'),
    path('', views1.Redirect, name='Redirect'),
    path('student_detail/', views1.student_detail, name='student_detail'),
    path('student_detail/SE', views1.SE, name='SE'),
    path('student_detail/TE', views1.TE, name='TE'),
    path('student_detail/BE', views1.BE, name='BE'),
    path('form_dashboard/', views1.form_dashboard, name='form_dashboard'),
    path('dashboard/', views1.dashboard_home, name='dashboard_home'),
]


