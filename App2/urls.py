from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    # Authentication URLs
    path('accounts/register/', register_view, name='register'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Main pages
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),

    # Course URLs
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:course_id>/enroll/', enroll_course, name='enroll_course'),

    # Dashboard URLs
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/profile/', profile_view, name='profile'),
    path('dashboard/enrollment/<int:enrollment_id>/', course_progress_view, name='course_progress'),
    path('dashboard/enrollment/<int:enrollment_id>/lesson/<int:lesson_id>/', lesson_view, name='lesson_view'),

    # Admin URLs - Enhanced Course Management (Custom Admin Dashboard)
    path('admin_dashboard/', admin_course_management, name='admin_course_management'),
    path('admin_dashboard/users/', admin_user_management, name='admin_user_management'),
    path('admin_dashboard/users/create/', admin_create_user, name='admin_create_user'),
    path('admin_dashboard/users/<int:user_id>/toggle/', admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin_dashboard/users/<int:user_id>/edit/', admin_edit_user, name='admin_edit_user'),
    path('admin_dashboard/users/<int:user_id>/enrollments/', admin_user_enrollments, name='admin_user_enrollments'),
    path('admin_dashboard/users/<int:user_id>/delete/', admin_delete_user, name='admin_delete_user'),
    path('admin_dashboard/courses/create/', admin_course_create, name='admin_course_create'),
    path('admin_dashboard/courses/<int:course_id>/', admin_course_detail, name='admin_course_detail'),
    path('admin_dashboard/courses/<int:course_id>/edit/', admin_course_edit, name='admin_course_edit'),
    path('admin_dashboard/courses/<int:course_id>/modules/create/', admin_module_create, name='admin_module_create'),
    path('admin_dashboard/modules/<int:module_id>/tasks/create/', admin_task_create, name='admin_task_create'),
    path('admin_dashboard/modules/<int:module_id>/quiz/create/', admin_quiz_create, name='admin_quiz_create'),
    path('admin_dashboard/quizzes/<int:quiz_id>/questions/', admin_quiz_questions, name='admin_quiz_questions'),

    # Legacy Admin URLs (keeping for compatibility)
    path('admin/courses/', AdminCourseListView.as_view(), name='admin_course_list'),
    path('admin/courses/create/', CourseCreateView.as_view(), name='admin_course_create_legacy'),
    path('admin/courses/<int:pk>/update/', CourseUpdateView.as_view(), name='admin_course_update_legacy'),
    path('admin/courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='admin_course_delete_legacy'),

    # API URLs
    path('api/mark-lesson-complete/<int:enrollment_id>/<int:lesson_id>/', mark_lesson_complete, name='mark_lesson_complete'),

    # Legacy URLs (for backward compatibility)
    path('register/', register_view, name='legacy_register'),
    path('login/', login_view, name='legacy_login'),
    path('usrp/', dashboard_view, name='legacy_dashboard'),
    path('usrgd/', dashboard_view, name='legacy_usrgd'),
    # path('admin/', adminpage, name='legacy_admin'),
    # path('admin/users/', mb_users, name='legacy_admin_users'),
    # path('admin/courses/', mb_course, name='legacy_admin_courses'),
    # path('admin/msg/', msgs, name='legacy_admin_msg'),
]