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
    list_display = ('name', 'roll_number', 'division', 'sem', 'year', 'faculty_mentor', 'be_student_mentor')
    search_fields = ('name', 'roll_number', 'faculty_mentor', 'be_student_mentor')
    list_filter = ('division',)



from django.contrib import admin
from .models import Session

class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'mentor', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'additional_info')
    list_filter = ('mentor', 'created_at')

admin.site.register(Session, SessionAdmin)



from django.contrib import admin
from .models import MentorshipData, Student1

# class Student1Admin(admin.ModelAdmin):
#     list_display = ('mentorship_data', 'atte_ise1', 'atte_mse', 'attendance', 'cts', 'ise1', 'mse', 'semcgpa')
#     search_fields = ['mentorship_data__name', 'mentorship_data__roll_number']


# admin.site.register(Student1, Student1Admin)

from django.contrib import admin
from .models import MentorshipData, Student1

class Student1Admin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_roll_number', 'atte_ise1', 'atte_mse', 'attendance', 'cts', 'ise1', 'mse', 'semcgpa')
    search_fields = ['mentorship_data__name', 'mentorship_data__roll_number']

    # Custom method to display the student's name from MentorshipData
    def get_student_name(self, obj):
        return obj.mentorship_data.name
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'mentorship_data__name'  # Enables sorting by student name

    # Custom method to display the roll number from MentorshipData
    def get_roll_number(self, obj):
        return obj.mentorship_data.roll_number
    get_roll_number.short_description = 'Roll Number'
    get_roll_number.admin_order_field = 'mentorship_data__roll_number'  # Enables sorting by roll number

admin.site.register(Student1, Student1Admin)


@admin.action(description='Increment semester for all students')
def increment_semester_for_all(modeladmin, request, queryset):
    for student in queryset:
        if student.sem < 8:  # Ensure that the sem doesn't exceed 8
            student.sem += 1
            student.set_year_based_on_sem()
            student.save()