# urls.py
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/', views.mentor_signup, name='mentor_signup'),
    path('dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
]
