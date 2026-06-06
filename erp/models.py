from django.db import models
from django.contrib.auth.models import User
import datetime

class DepartmentChoices(models.TextChoices):
    CSE = 'CSE', 'Computer Science & Engineering'
    ECE = 'ECE', 'Electronics & Communication Engineering'
    EEE = 'EEE', 'Electrical & Electronics Engineering'
    MECH = 'MECH', 'Mechanical Engineering'
    CIVIL = 'CIVIL', 'Civil Engineering'

class SectionChoices(models.TextChoices):
    A = 'A', 'Section A'
    B = 'B', 'Section B'
    C = 'C', 'Section C'

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'System Admin'
    HOD = 'HOD', 'Head of Department'
    TEACHER = 'TEACHER', 'Teacher'
    STUDENT = 'STUDENT', 'Student'

class AttendanceStatusChoices(models.TextChoices):
    FULL_PRESENT = 'FULL', 'Full Present (Both Sessions)'
    HALF_DAY = 'HALF', 'Half Day (One Session)'
    ABSENT = 'ABSENT', 'Absent (No Sessions)'

class AdmissionTypeChoices(models.TextChoices):
    REGULAR = 'REGULAR', 'Regular (4-Year Entry)'
    LATERAL = 'LATERAL', 'Lateral Entry (Diploma to B.Tech 3-Year Entry)'

class HODProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hod_profile')
    name = models.CharField(max_length=150)
    department = models.CharField(max_length=10, choices=DepartmentChoices.choices)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"HOD - {self.name} ({self.department})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    created_by_hod = models.ForeignKey(HODProfile, on_delete=models.SET_NULL, null=True, blank=True)
    teacher_name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=10, choices=DepartmentChoices.choices)
    subject = models.CharField(max_length=150)
    specialized_subject = models.CharField(max_length=150)
    qualification = models.CharField(max_length=100)
    experience = models.IntegerField(help_text="In years")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    mail_id = models.EmailField()

    def __str__(self):
        return f"{self.teacher_name} ({self.employee_id})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    created_by_teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    name_of_student = models.CharField(max_length=150)
    registration_number = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=10, choices=DepartmentChoices.choices)
    
    # NEW ENTRY TRACKING SELECTION FIELD
    admission_type = models.CharField(
        max_length=10, 
        choices=AdmissionTypeChoices.choices, 
        default=AdmissionTypeChoices.REGULAR
    )
    
    section = models.CharField(max_length=2, choices=SectionChoices.choices)
    semester = models.CharField(max_length=10, default="1-1")
    mail_id = models.EmailField()
    phone_number = models.CharField(max_length=20)
    
    # Auto-calculated from session logs history
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    class_performance_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0) # alias link for cgpa calculation mapping
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    mid1_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Mid-1 Marks")
    mid2_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Mid-2 Marks")
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Calculated Internal Marks")
    external_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name_of_student} ({self.registration_number}) - [{self.get_admission_type_display()}]"

    def recalculate_attendance_percentage(self):
        """
        Loops over every single daily session log recorded for this student
        and aggregates the running percentage.
        Full = 1.0 day, Half = 0.5 day, Absent = 0.0 days.
        """
        logs = self.attendance_logs.all()
        total_days_conducted = logs.count()
        if total_days_conducted == 0:
            self.attendance = 0.0
            return

        days_present = 0.0
        for log in logs:
            if log.status == AttendanceStatusChoices.FULL_PRESENT:
                days_present += 1.0
            elif log.status == AttendanceStatusChoices.HALF_DAY:
                days_present += 0.5
        
        calculated_percentage = (days_present / total_days_conducted) * 100.0
        self.attendance = round(calculated_percentage, 2)

    def save(self, *args, **kwargs):
        # AUTOMATION RULE: Force Lateral entries to fall back to 2-1 minimum boundaries
        if self.admission_type == AdmissionTypeChoices.LATERAL and (self.semester == "1-1" or self.semester == "1-2" or not self.semester):
            self.semester = "2-1"

        # 80/20 Internal calculation sequence matrix out of 30 marks Max
        m1 = float(self.mid1_marks or 0.0)
        m2 = float(self.mid2_marks or 0.0)
        best_mid = max(m1, m2)
        worst_mid = min(m1, m2)
        
        calculated_internals = (best_mid * 0.8) + (worst_mid * 0.2)
        self.internal_marks = round(calculated_internals, 2)
        
        super(StudentProfile, self).save(*args, **kwargs)

class DailyAttendanceLog(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_logs')
    recorded_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=10, choices=AttendanceStatusChoices.choices, default=AttendanceStatusChoices.FULL_PRESENT)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.registration_number} - {self.date} - {self.get_status_display()}"

class StudentSubjectGrade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subject_grades')
    semester = models.CharField(max_length=10, default="1-1", help_text="e.g., 1-1, 1-2")
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=150)
    grade = models.CharField(max_length=5, help_text="e.g., S, A, B, C, F")
    credits = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)

    class Meta:
        unique_together = ('student', 'semester', 'subject_code')
        ordering = ['subject_code']

    def __str__(self):
        return f"{self.student.registration_number} - {self.subject_code} - {self.grade}"

class HistoryLog(models.Model):
    modified_by = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    target_record = models.CharField(max_length=250)
    action = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']