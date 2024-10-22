from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.mentor_admin_signup, name='mentor_admin_signup'),
    path('dashboard/', views.mentor_admin_dashboard, name='mentor_admin_dashboard'),
    path('sessions/', views.mentor_admin_sessions, name='mentor_admin_sessions'),
    path('mentors/', views.mentors_list, name='mentors_list'),
    path('add_student/<int:mentor_id>/', views.add_student, name='add_student'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('change-sem/<str:action>/<str:year>/', views.change_sem_for_year, name='change_sem'),
    path('progress_report/', views.admin_progress_report, name='admin_progress_report'),
]
