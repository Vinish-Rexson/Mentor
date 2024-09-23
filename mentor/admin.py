from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'age', 'section']


class StudentFormAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentForm, StudentFormAdmin)
