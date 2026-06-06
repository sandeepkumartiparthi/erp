import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Q

from .models import (
    HODProfile, TeacherProfile, StudentProfile, DailyAttendanceLog, 
    StudentSubjectGrade, HistoryLog, DepartmentChoices, RoleChoices, SectionChoices
)
from .forms import HODForm, TeacherForm, StudentForm, GradingUpdateForm, DailyAttendanceMarkingForm
from .pagination import paginate_queryset

def index_view(request):
    return render(request, 'erp/index.html')

def portal_login_view(request, role_type):
    if role_type not in ['admin', 'hod', 'teacher', 'student']:
        return redirect('index')
    
    error_msg = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if role_type == 'admin' and user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            elif role_type == 'hod' and HODProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('hod_dashboard')
            elif role_type == 'teacher' and TeacherProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('teacher_dashboard')
            elif role_type == 'student' and StudentProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('student_dashboard')
            else:
                error_msg = f"Security Clearance Mismatch for portal target: {role_type.upper()}"
        else:
            error_msg = "Invalid account tracking authentication credentials."

    return render(request, 'erp/login.html', {'role_type': role_type, 'error_msg': error_msg})

def logout_view(request):
    logout(request)
    return redirect('index')

def access_denied(request):
    return render(request, 'erp/access_denied.html')

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('access_denied')
    hods = HODProfile.objects.all().order_by('-id')
    page_obj = paginate_queryset(request, hods, 10)
    
    history_logs = HistoryLog.objects.all().order_by('-timestamp')
    history_page = paginate_queryset(request, history_logs, 15)
    
    form = HODForm()

    if request.method == 'POST':
        form = HODForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                u = form.cleaned_data['username']
                p = form.cleaned_data['password']
                if User.objects.filter(username=u).exists():
                    form.add_error('username', 'Username already exists inside registry indices.')
                else:
                    user_obj = User.objects.create_user(username=u, password=p)
                    hod_prof = form.save(commit=False)
                    hod_prof.user = user_obj
                    hod_prof.save()

                    HistoryLog.objects.create(
                        modified_by=request.user.username, role=RoleChoices.ADMIN,
                        target_record=f"HOD Node: {u}", action="CREATE_HOD",
                        old_value="", new_value=json.dumps(form.cleaned_data),
                        description=f"Admin initialized Head of Department profile mapping vector for {hod_prof.name} ({hod_prof.department})"
                    )
                    return redirect('admin_dashboard')

    return render(request, 'erp/admin_dashboard.html', {'page_obj': page_obj, 'history_page': history_page, 'form': form})

@login_required
def hod_dashboard_view(request):
    hod = getattr(request.user, 'hod_profile', None)
    if not hod:
        return redirect('access_denied')

    # ISOLATE SYSTEM SUBSYSTEM BY FORCE: Limit query scopes strictly to this logged-in HOD's active branch department
    current_department = hod.department
    teachers = TeacherProfile.objects.filter(branch=current_department).order_by('-id')
    students = StudentProfile.objects.filter(branch=current_department).order_by('-id')

    # Live Search Vector Processors Array Setup
    q_t = request.GET.get('search_teacher', '')
    if q_t:
        teachers = teachers.filter(Q(teacher_name__icontains=q_t) | Q(employee_id__icontains=q_t))
    
    q_s = request.GET.get('search_student', '')
    sem_s = request.GET.get('semester', '')
    if q_s:
        students = students.filter(Q(name_of_student__icontains=q_s) | Q(registration_number__icontains=q_s))
    if sem_s:
        students = students.filter(semester=sem_s)

    teachers_page = paginate_queryset(request, teachers, 10)
    students_page = paginate_queryset(request, students, 10)

    # ==========================================================================
    # FIXED CHART ENGINE: Dynamic Analytics Scoped strictly to current HOD Branch
    # ==========================================================================
    dept_labels = [f"{current_department} Branch"]
    branch_avg_cgpa = students.aggregate(avg_cgpa=Avg('cgpa'))['avg_cgpa'] or 0.0
    dept_performance = [round(float(branch_avg_cgpa), 2)]
    
    attendance_labels = ['<75% Defaulter', '75-85% Passing', '85-100% Elite']
    total_st_count = students.count()
    attendance_data = [
        students.filter(attendance__lt=75).count(),
        students.filter(attendance__gte=75, attendance__lt=85).count(),
        students.filter(attendance__gte=85).count()
    ]

    teacher_form = TeacherForm()

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                u = form.cleaned_data['username']
                p = form.cleaned_data['password']
                if User.objects.filter(username=u).exists():
                    form.add_error('username', 'Username signature conflict detected.')
                else:
                    user_obj = User.objects.create_user(username=u, password=p)
                    prof = form.save(commit=False)
                    prof.user = user_obj
                    prof.created_by_hod = hod
                    prof.save()

                    HistoryLog.objects.create(
                        modified_by=request.user.username, role=RoleChoices.HOD,
                        target_record=f"Teacher: {u}", action="CREATE_TEACHER",
                        old_value="", new_value=json.dumps(form.cleaned_data, default=str),
                        description=f"HOD onboarded system instructor account mapped under ID {prof.employee_id}"
                    )
                    return redirect('hod_dashboard')

    context = {
        'hod': hod, 'teachers_page': teachers_page, 'students_page': students_page, 'teacher_form': teacher_form,
        'dept_labels': json.dumps(dept_labels), 'dept_performance': json.dumps(dept_performance),
        'attendance_labels': json.dumps(attendance_labels), 'attendance_data': json.dumps(attendance_data),
        'total_st_count': total_st_count, 'total_t_count': teachers.count()
    }
    return render(request, 'erp/hod_dashboard.html', context)

@login_required
def teacher_dashboard_view(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('access_denied')

    # STRICT SEPARATION LAYER: Restricts instructor visibility solely to their assigned functional department branch roster
    students = StudentProfile.objects.filter(branch=teacher.branch).order_by('-id')
    
    q = request.GET.get('search', '')
    sem = request.GET.get('semester', '')
    if q:
        students = students.filter(Q(name_of_student__icontains=q) | Q(registration_number__icontains=q))
    if sem:
        students = students.filter(semester=sem)

    students_page = paginate_queryset(request, students, 10)
    student_form = StudentForm()
    update_form = GradingUpdateForm()
    attendance_form = DailyAttendanceMarkingForm()

    # Metrics Distribution Generators Block
    grade_distribution_labels = ['F (<5.0)', 'B (5.0-7.5)', 'A (7.5-10.0)']
    grade_distribution_data = [
        students.filter(cgpa__lt=5.0).count(),
        students.filter(cgpa__gte=5.0, cgpa__lt=7.5).count(),
        students.filter(cgpa__gte=7.5).count()
    ]

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_student':
            form = StudentForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    u = form.cleaned_data['username']
                    p = form.cleaned_data['password']
                    if User.objects.filter(username=u).exists():
                        form.add_error('username', 'Username string allocation conflict.')
                    else:
                        user_obj = User.objects.create_user(username=u, password=p)
                        prof = form.save(commit=False)
                        prof.user = user_obj
                        prof.created_by_teacher = teacher
                        prof.save()

                        HistoryLog.objects.create(
                            modified_by=request.user.username, role=RoleChoices.TEACHER,
                            target_record=f"Student: {u}", action="CREATE_STUDENT",
                            old_value="", new_value=json.dumps(form.cleaned_data, default=str),
                            description=f"Instructor self-managed provisioning pipeline successfully added student profile target {prof.registration_number}"
                        )
                        return redirect('teacher_dashboard')
        
        elif action == 'update_grading':
            pk = request.POST.get('pk')
            student_obj = get_object_or_404(StudentProfile, pk=pk, branch=teacher.branch)
            old_data = GradingUpdateForm(instance=student_obj).initial
            form = GradingUpdateForm(request.POST, instance=student_obj)
            if form.is_valid():
                with transaction.atomic():
                    # Note: Internal calculation weights (out of 30) are automatically handled inside the model save override layer
                    form.save()

                    HistoryLog.objects.create(
                        modified_by=request.user.username, role=RoleChoices.TEACHER,
                        target_record=f"Marks Update: {student_obj.registration_number}", action="MUTATE_GRADES",
                        old_value=json.dumps(old_data, default=str), new_value=json.dumps(form.cleaned_data, default=str),
                        description=f"Teacher reassigned grading fields for target register context: {student_obj.registration_number}"
                    )
                    return redirect('teacher_dashboard')

        # SYNCHRONOUS LEADING ENTRY SHEET BATCH ATTENDANCE: Submits everyday log parameters for all students on the fly
        elif action == 'bulk_submit_attendance':
            today = datetime.date.today()
            with transaction.atomic():
                for student_obj in students:
                    post_key = f"student_status_{student_obj.pk}"
                    if post_key in request.POST:
                        status_val = request.POST.get(post_key)
                        
                        attendance_record, created = DailyAttendanceLog.objects.get_or_create(
                            student=student_obj,
                            date=today,
                            defaults={'recorded_by': teacher, 'status': status_val}
                        )
                        if not created:
                            attendance_record.status = status_val
                            attendance_record.recorded_by = teacher
                            attendance_record.save()
                        
                        # Re-calculate average tracking percentage vector dynamically from daily matrix logs
                        student_obj.recalculate_attendance_percentage()
                        student_obj.save()

                HistoryLog.objects.create(
                    modified_by=request.user.username, role=RoleChoices.TEACHER,
                    target_record=f"Bulk Attendance Sheet: Branch {teacher.branch}",
                    action="BULK_MARK_ATTENDANCE",
                    description=f"Teacher committed session status arrays for all active branch students synchronously on date: {today}"
                )
            return redirect('teacher_dashboard')

    return render(request, 'erp/teacher_dashboard.html', {
        'teacher': teacher, 'students_page': students_page, 'student_form': student_form, 
        'update_form': update_form, 'attendance_form': attendance_form,
        'grade_labels': json.dumps(grade_distribution_labels), 'grade_data': json.dumps(grade_distribution_data)
    })

@login_required
def student_dashboard_view(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        return redirect('access_denied')
    
    # DYNAMIC PERFORMANCE REPORT SCORECARD SHEET ENGINE: 
    # Handles dynamic semester tab filtering and SGPA calculation
    active_sem = request.GET.get('sem', student.semester or "1-1")
    dynamic_grades = student.subject_grades.filter(semester=active_sem)
    
    # CALCULATE DYNAMIC SGPA
    GRADE_POINTS = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}
    total_weighted_points = 0
    total_credits = 0
    for g in dynamic_grades:
        points = GRADE_POINTS.get(g.grade.upper(), 0)
        total_weighted_points += (points * float(g.credits))
        total_credits += float(g.credits)
    
    sgpa = round(total_weighted_points / total_credits, 2) if total_credits > 0 else 0.0
    
    chart_labels = ['Internal Matrix Performance', 'External University Board Performance', 'Daily Attendance Efficiency']
    
    # NORMALIZATION CALCULATOR BALANCING ARRAY: Mapped precisely out of the updated 30 and 70 score ceiling thresholds
    chart_data = [
        round((float(student.internal_marks or 0.0) / 30.0) * 100.0, 2),
        round((float(student.external_marks or 0.0) / 70.0) * 100.0, 2),
        round(float(student.attendance or 0.0), 2)
    ]

    return render(request, 'erp/student_dashboard.html', {
        'student': student,
        'grades_list': dynamic_grades, 
        'active_sem': active_sem,
        'sgpa': sgpa,
        'chart_labels': json.dumps(chart_labels), 
        'chart_data': json.dumps(chart_data)
    })