from django.contrib import admin
from .models import HODProfile, TeacherProfile, StudentProfile, HistoryLog

@admin.register(HODProfile)
class HODProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'email')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'employee_id', 'branch', 'qualification')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('name_of_student', 'registration_number', 'branch', 'section', 'semester', 'cgpa')

@admin.register(HistoryLog)
class HistoryLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'modified_by', 'role', 'action', 'target_record')
    readonly_fields = ('modified_by', 'role', 'target_record', 'action', 'old_value', 'new_value', 'description', 'timestamp')