from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random
import smtplib
from email.message import EmailMessage

from .models import *
from .forms import *


# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with additional details
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                education=form.cleaned_data['education'],
                address=form.cleaned_data['college'],  # Using address field for college
            )
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to FUTURE BOUND TECH.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


# Home and Static Pages
def home_view(request):
    courses = Course.objects.filter(is_active=True)[:6]  # Show 6 featured courses
    context = {
        'courses': courses,
    }
    return render(request, 'home.html', context)


def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# Course Views
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        search = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category=category)
        if level:
            queryset = queryset.filter(level=level)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Course.objects.values_list('category', flat=True).distinct()
        context['levels'] = [('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        # Get enrollment status for logged-in user
        if self.request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=self.request.user, course=course).first()
            context['enrollment'] = enrollment
            context['is_enrolled'] = enrollment is not None

        # Get reviews
        context['reviews'] = Review.objects.filter(course=course)
        context['average_rating'] = context['reviews'].aggregate(Avg('rating'))['rating__avg'] or 0

        # Get modules and lessons
        context['modules'] = course.modules.filter(is_active=True).prefetch_related('lessons')

        return context


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', pk=course_id)

    # Create enrollment
    enrollment = Enrollment.objects.create(
        user=request.user,
        course=course,
        payment_status=course.course_type == 'free'
    )

    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('dashboard')


# Dashboard Views
@login_required
def dashboard_view(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    completed_count = enrollments.filter(status='completed').count()
    total_count = enrollments.filter(status='completed').count() + enrollments.filter(status='in_progress').count()
    context = {
        'enrollments': enrollments,
        'completed_count': completed_count,
        'total_count': total_count,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def course_progress_view(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    course = enrollment.course

    # Get all modules and lessons
    modules = course.modules.filter(is_active=True).prefetch_related('lessons')

    # Get user's progress
    progress_records = Progress.objects.filter(enrollment=enrollment)

    context = {
        'enrollment': enrollment,
        'course': course,
        'modules': modules,
        'progress_records': progress_records,
    }
    return render(request, 'dashboard/course_progress.html', context)


@login_required
def lesson_view(request, enrollment_id, lesson_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=enrollment.course, is_active=True)

    # Mark lesson as completed when accessed
    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'is_completed': False}
    )

    if request.method == 'POST' and 'mark_complete' in request.POST:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        enrollment.update_progress()
        messages.success(request, f'Lesson "{lesson.title}" marked as completed!')

        # Redirect to next lesson or course progress
        next_lesson = Lesson.objects.filter(
            module=lesson.module,
            order__gt=lesson.order,
            is_active=True
        ).first()

        if next_lesson:
            return redirect('lesson_view', enrollment_id=enrollment_id, lesson_id=next_lesson.id)
        else:
            return redirect('course_progress', enrollment_id=enrollment_id)

    context = {
        'enrollment': enrollment,
        'lesson': lesson,
        'progress': progress,
        'module': lesson.module,
    }
    return render(request, 'dashboard/lesson_view.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'dashboard/profile.html', {'form': form})


# Admin Views
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


def admin_course_management(request):
    """Main admin course management page"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    courses = Course.objects.all().order_by('-created_at')
    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'active_courses': courses.filter(is_active=True).count(),
        'inactive_courses': courses.filter(is_active=False).count(),
    }
    return render(request, 'admin/course_management.html', context)


def admin_course_create(request):
    """Create new course with modules, tasks, and quiz"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        if course_form.is_valid():
            course = course_form.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('admin_course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        course_form = CourseForm()

    context = {
        'course_form': course_form,
        'title': 'Create New Course'
    }
    return render(request, 'admin/course_form.html', context)


def admin_course_detail(request, course_id):
    """Detailed view of course with all components"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all().order_by('order')
    discussions = course.discussions.all().order_by('-created_at')[:10]

    context = {
        'course': course,
        'modules': modules,
        'discussions': discussions,
        'total_modules': modules.count(),
        'total_tasks': sum(module.tasks.count() for module in modules),
        'total_enrollments': Enrollment.objects.filter(course=course).count(),
    }
    return render(request, 'admin/course_detail.html', context)


def admin_course_edit(request, course_id):
    """Edit existing course"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    context = {
        'course_form': form,
        'course': course,
        'title': 'Edit Course'
    }
    return render(request, 'admin/course_form.html', context)


def admin_module_create(request, course_id):
    """Create new module for a course"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f'Module "{module.title}" created successfully!')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = ModuleForm()

    context = {
        'module_form': form,
        'course': course,
        'title': 'Create Module'
    }
    return render(request, 'admin/module_form.html', context)


def admin_task_create(request, module_id):
    """Create new task for a module"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.module = module
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = TaskForm()

    context = {
        'task_form': form,
        'module': module,
        'course': course,
        'title': 'Create Task'
    }
    return render(request, 'admin/task_form.html', context)


def admin_quiz_create(request, module_id):
    """Create quiz for a module"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    module = get_object_or_404(Module, id=module_id)
    course = module.course

    # Check if quiz already exists
    if hasattr(module, 'quiz'):
        messages.warning(request, 'Quiz already exists for this module.')
        return redirect('admin_course_detail', course_id=course.id)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            messages.success(request, f'Quiz "{quiz.title}" created successfully!')
            return redirect('admin_course_detail', course_id=course.id)
    else:
        form = QuizForm()

    context = {
        'quiz_form': form,
        'module': module,
        'course': course,
        'title': 'Create Quiz'
    }
    return render(request, 'admin/quiz_form.html', context)


def admin_quiz_questions(request, quiz_id):
    """Manage quiz questions"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by('order')

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('admin_quiz_questions', quiz_id=quiz.id)
    else:
        form = QuizQuestionForm()

    context = {
        'quiz': quiz,
        'questions': questions,
        'question_form': form,
        'course': quiz.module.course,
    }
    return render(request, 'admin/quiz_questions.html', context)


class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'admin/course_form.html'
    success_url = reverse_lazy('admin_course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)


class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'admin/course_form.html'
    success_url = reverse_lazy('admin_course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)


class CourseDeleteView(AdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'admin/course_confirm_delete.html'
    success_url = reverse_lazy('admin_course_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Course deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AdminCourseListView(AdminRequiredMixin, ListView):
    model = Course
    template_name = 'admin/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20


# API-like views for AJAX requests
def mark_lesson_complete(request, enrollment_id, lesson_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id, user=request.user)
        lesson = Lesson.objects.get(id=lesson_id, module__course=enrollment.course)

        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )

        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            enrollment.update_progress()

        return JsonResponse({
            'success': True,
            'progress_percentage': enrollment.progress_percentage
        })

    except (Enrollment.DoesNotExist, Lesson.DoesNotExist):
        return JsonResponse({'error': 'Invalid request'}, status=400)


# Utility functions
def send_otp_email(user, otp):
    """Send OTP email to user"""
    subject = 'FUTURE BOUND TECH - Email Verification'
    message = f'Your verification code is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
