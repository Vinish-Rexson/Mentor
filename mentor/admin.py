from django.contrib import admin
from .models import *
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'year', 'semester', 'roll_number', 'branch', 'division')

admin.site.register(Student, StudentAdmin)


class StudentFormAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentForm, StudentFormAdmin)
