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
import json

from .models import *
from .forms import *


# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with additional details (only if it doesn't exist)
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': form.cleaned_data['phone'],
                    'education': form.cleaned_data['education'],
                    'college': form.cleaned_data['college'],
                    'state': form.cleaned_data['state'],
                }
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

    # Get or create progress record for this lesson only
    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'is_completed': False}
    )

    # For completed courses, allow access to all lessons for review
    # For in-progress courses, check prerequisites
    can_mark_complete = False
    if enrollment.status == 'completed':
        # Allow marking as complete for review purposes, but don't change progress
        can_mark_complete = not progress.is_completed
    else:
        # For in-progress courses, check if this is the first lesson in module or previous are completed
        if lesson.order == 0:  # First lesson in module
            can_mark_complete = True
        else:
            # Check if all previous lessons in this module are completed
            previous_lessons = Lesson.objects.filter(
                module=lesson.module,
                order__lt=lesson.order,
                is_active=True
            )
            if previous_lessons.exists():
                completed_previous = Progress.objects.filter(
                    enrollment=enrollment,
                    lesson__in=previous_lessons,
                    is_completed=True
                ).count()
                can_mark_complete = completed_previous == previous_lessons.count()
            else:
                can_mark_complete = True

    if request.method == 'POST' and 'mark_complete' in request.POST:
        if can_mark_complete:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()

            # Only update enrollment progress if course is not already completed
            if enrollment.status != 'completed':
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

    # Get next lesson in the same module
    next_lesson = Lesson.objects.filter(
        module=lesson.module,
        order__gt=lesson.order,
        is_active=True
    ).first()

    # Get previous lesson in the same module
    previous_lesson = Lesson.objects.filter(
        module=lesson.module,
        order__lt=lesson.order,
        is_active=True
    ).last()

    context = {
        'enrollment': enrollment,
        'lesson': lesson,
        'progress': progress,
        'module': lesson.module,
        'course': enrollment.course,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson,
        'can_mark_complete': can_mark_complete,
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


@login_required
def admin_user_management(request):
    """Admin user management page"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    user_profiles = UserProfile.objects.all().select_related('user')

    # Get enrollment stats for each user
    user_stats = {}
    for user in users:
        enrollments = Enrollment.objects.filter(user=user)
        user_stats[user.id] = {
            'total_enrollments': enrollments.count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'in_progress_courses': enrollments.filter(status='in_progress').count(),
        }

    context = {
        'users': users,
        'user_profiles': user_profiles,
        'user_stats': user_stats,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'admin_users': users.filter(is_superuser=True).count(),
    }
    return render(request, 'admin/user_management.html', context)


@login_required
def admin_create_user(request):
    """Create new user via AJAX"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Access denied'})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            from django.contrib.auth.models import User

            # Check if user already exists
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'})

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'})

            # Create user
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password1'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                is_staff=data.get('is_staff', False),
                is_superuser=data.get('is_staff', False)
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=data.get('phone', ''),
                college=data.get('college', ''),
                education=data.get('education', ''),
                state=data.get('state', '')
            )

            return JsonResponse({'success': True, 'message': 'User created successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Access denied'})

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)

        # Prevent admin from deactivating themselves
        if user == request.user:
            return JsonResponse({'success': False, 'message': 'Cannot deactivate your own account'})

        data = json.loads(request.body)
        user.is_active = data.get('activate', True)
        user.save()

        action = 'activated' if user.is_active else 'deactivated'
        return JsonResponse({'success': True, 'message': f'User {action} successfully'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def admin_edit_user(request, user_id):
    """Edit user details"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.save()

        # Update or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': request.POST.get('phone', ''),
                'college': request.POST.get('college', ''),
                'education': request.POST.get('education', ''),
                'state': request.POST.get('state', ''),
            }
        )

        if not created:
            profile.phone = request.POST.get('phone', '')
            profile.college = request.POST.get('college', '')
            profile.education = request.POST.get('education', '')
            profile.state = request.POST.get('state', '')
            profile.save()

        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('admin_user_management')

    context = {
        'user': user,
        'profile': getattr(user, 'userprofile', None),
    }
    return render(request, 'admin/user_edit.html', context)


@login_required
def admin_user_enrollments(request, user_id):
    """Manage user enrollments - view and remove enrollments"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    enrollments = Enrollment.objects.filter(user=user).select_related('course')

    if request.method == 'POST' and 'remove_enrollment' in request.POST:
        enrollment_id = request.POST.get('enrollment_id')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, user=user)
            course_title = enrollment.course.title
            enrollment.delete()
            messages.success(request, f'Removed enrollment for "{course_title}" from {user.username}')
            return redirect('admin_user_enrollments', user_id=user_id)
        except Enrollment.DoesNotExist:
            messages.error(request, 'Enrollment not found')

    context = {
        'user': user,
        'enrollments': enrollments,
    }
    return render(request, 'admin/user_enrollments.html', context)


@login_required
def admin_delete_user(request, user_id):
    """Delete user"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Access denied'})

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)

        # Prevent admin from deleting themselves
        if user == request.user:
            return JsonResponse({'success': False, 'message': 'Cannot delete your own account'})

        user.delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


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
            defaults={'is_completed': False}
        )

        # Check if lesson can be marked complete (same logic as lesson_view)
        can_mark_complete = False
        if enrollment.status == 'completed':
            # Allow marking as complete for review purposes
            can_mark_complete = not progress.is_completed
        else:
            # For in-progress courses, check prerequisites
            if lesson.order == 0:  # First lesson in module
                can_mark_complete = True
            else:
                # Check if all previous lessons in this module are completed
                previous_lessons = Lesson.objects.filter(
                    module=lesson.module,
                    order__lt=lesson.order,
                    is_active=True
                )
                if previous_lessons.exists():
                    completed_previous = Progress.objects.filter(
                        enrollment=enrollment,
                        lesson__in=previous_lessons,
                        is_completed=True
                    ).count()
                    can_mark_complete = completed_previous == previous_lessons.count()
                else:
                    can_mark_complete = True

        if not progress.is_completed and can_mark_complete:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()

            # Only update enrollment progress if course is not already completed
            if enrollment.status != 'completed':
                # Update progress with precise calculation to prevent bulk completion
                total_lessons = enrollment.course.get_total_lessons()
                completed_lessons = Progress.objects.filter(
                    enrollment=enrollment,
                    is_completed=True
                ).count()

                # Calculate progress with high precision to avoid rounding errors
                if total_lessons > 0:
                    progress_percentage = round((completed_lessons / total_lessons) * 100, 6)
                else:
                    progress_percentage = 100.00

                enrollment.progress_percentage = progress_percentage
                enrollment.save()

                # Only mark as completed when exactly 100% (prevent bulk completion)
                if progress_percentage >= 100.00 and enrollment.status != 'completed':
                    enrollment.status = 'completed'
                    enrollment.completion_date = timezone.now()
                    enrollment.save()
                elif progress_percentage > 0 and enrollment.status == 'enrolled':
                    enrollment.status = 'in_progress'
                    enrollment.save()

                print(f"DEBUG: Lesson {lesson.id} marked complete for enrollment {enrollment.id}")
                print(f"DEBUG: Total lessons: {total_lessons}")
                print(f"DEBUG: Completed lessons: {completed_lessons}")
                print(f"DEBUG: Progress percentage: {progress_percentage}")

        # Get next lesson URL
        next_lesson = Lesson.objects.filter(
            module=lesson.module,
            order__gt=lesson.order,
            is_active=True
        ).first()

        next_lesson_url = None
        if next_lesson:
            next_lesson_url = f'/dashboard/enrollment/{enrollment_id}/lesson/{next_lesson.id}/'
        else:
            next_lesson_url = f'/dashboard/enrollment/{enrollment_id}/'

        return JsonResponse({
            'success': True,
            'progress_percentage': float(enrollment.progress_percentage),
            'next_lesson_url': next_lesson_url
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
