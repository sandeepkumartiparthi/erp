from django import forms
from .models import HODProfile, TeacherProfile, StudentProfile, DailyAttendanceLog

class HODForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Enter Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Enter a secure login password'
    }))

    class Meta:
        model = HODProfile
        fields = ['name', 'department', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Name'}),
            'department': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Email'}),
        }

class TeacherForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Choose a login username for the teacher'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Set a default password for this teacher'
    }))

    class Meta:
        model = TeacherProfile
        exclude = ['user', 'created_by_hod']
        widgets = {
            'teacher_name': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Name of the Teacher'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'CSE_000'}),
            'branch': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            'subject': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Subject name'}),
            'specialized_subject': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Specialized Subject'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Qualification'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Year Of Experience '}),
            'salary': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'placeholder': 'Enter monthly salary amount'}),
            'mail_id': forms.EmailInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Gmail'}),
        }

class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Create student unique login username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control shadow-sm', 
        'placeholder': 'Set login password for the student'
    }))

    class Meta:
        model = StudentProfile
        # Excluded attendance and internal_marks because the system generates them automatically now!
        exclude = ['user', 'created_by_teacher', 'attendance', 'internal_marks']
        widgets = {
            'name_of_student': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Name Of The Student'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Reg No'}),
            'branch': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            
            # UPDATED ADMISSION TYPE SELECTOR FIELD MATRIX LINK WITH JAVASCRIPT TARGET LISTENERS
            'admission_type': forms.Select(attrs={
                'class': 'form-select shadow-sm', 
                'id': 'js-admission-selector', 
                'onchange': 'toggleFormSemesterFallback()'
            }),
            
            'section': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            
            # UPDATED TARGET ID LINK TO ALLOW AUTOMATED ASSIGNMENT REDIRECTION TO SEMESTER 2-1 FOR LATERAL STUDENTS
            'semester': forms.TextInput(attrs={
                'class': 'form-control shadow-sm', 
                'id': 'js-semester-input', 
                'placeholder': 'Year-Semester format (e.g. 1-1 or 2-1)'
            }),
            
            'mail_id': forms.EmailInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Gmail'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Phone no'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'placeholder': 'Current cumulative CGPA out of 10'}),
            'mid1_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'max': '30', 'placeholder': 'Mid-1 Marks out of 30'}),
            'mid2_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'max': '30', 'placeholder': 'Mid-2 Marks out of 30'}),
            'external_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'max': '70', 'placeholder': 'Semester End Exam Marks out of 70'}),
        }

class GradingUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        # Kept out attendance/internal fields from text-box parameters since they calculate dynamically
        fields = ['mid1_marks', 'mid2_marks', 'external_marks', 'cgpa', 'semester']
        widgets = {
            'mid1_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm js-mid1-input', 'step': '0.01', 'max': '30', 'placeholder': 'Update Mid-1 score (Max 30)'}),
            'mid2_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm js-mid2-input', 'step': '0.01', 'max': '30', 'placeholder': 'Update Mid-2 score (Max 30)'}),
            'external_marks': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'max': '70', 'placeholder': 'Update External Exam score (Max 70)'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'max': '10', 'placeholder': 'Update overall CGPA (Max 10.00)'}),
            'semester': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': 'Change current semester label'}),
        }

class DailyAttendanceMarkingForm(forms.ModelForm):
    class Meta:
        model = DailyAttendanceLog
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select shadow-sm'})
        }