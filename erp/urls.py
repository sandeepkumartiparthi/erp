from django.urls import path
from . import views

urlpatterns = [
    # Core Entrypoint Landing & Authentication Gateway Channels
    path('', views.index_view, name='index'),
    path('portal/gate/login/<str:role_type>/', views.portal_login_view, name='portal_login'),
    path('portal/gate/logout/', views.logout_view, name='logout'),
    path('portal/unauthorized/clearance-fault/', views.access_denied, name='access_denied'),
    
    # Structural Dashboard Panel Node Entrypoints
    path('workspace/system-admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('workspace/learner-student/', views.student_dashboard_view, name='student_dashboard'),

    # Head of Department (HOD) Routing Clusters
    path('workspace/department-hod/', views.hod_dashboard_view, name='hod_dashboard'),
    path('workspace/department-hod/teachers/', views.hod_dashboard_view, name='hod_teachers'),
    path('workspace/department-hod/students/', views.hod_dashboard_view, name='hod_students'),
    path('workspace/department-hod/subjects/', views.hod_dashboard_view, name='hod_subjects'),
    path('workspace/department-hod/history/', views.hod_dashboard_view, name='hod_history'),

    # Instructor Faculty Core Routing Clusters (FIXES THE TEACHER SIGN-IN FAULT)
    path('workspace/instructor-faculty/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('workspace/instructor-faculty/students-group/', views.teacher_dashboard_view, name='teacher_students'),  # <-- ADD THIS MISSING ROUTE OVERLAY
]