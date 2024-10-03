from django.contrib import admin
from .models import *
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'year', 'semester', 'roll_number', 'branch', 'division')

admin.site.register(Student, StudentAdmin)


class StudentFormAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentForm, StudentFormAdmin)

class StudentFollowupFormAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentFollowupForm, StudentFollowupFormAdmin)


@admin.register(MentorshipData)
class MentorshipDataAdmin(admin.ModelAdmin):
    # Customize how the model is displayed in the admin panel
    list_display = ('name', 'roll_number', 'division', 'faculty_mentor', 'be_student_mentor')
    search_fields = ('name', 'roll_number', 'faculty_mentor', 'be_student_mentor')
    list_filter = ('division',)