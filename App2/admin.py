from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'education', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_type', 'price', 'category', 'level', 'is_active']
    list_filter = ['course_type', 'category', 'level', 'is_active']
    search_fields = ['title', 'description', 'instructor']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_active']
    list_filter = ['course', 'is_active']
    search_fields = ['title', 'course__title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'content_type', 'order', 'is_active']
    list_filter = ['content_type', 'is_active', 'module__course']
    search_fields = ['title', 'module__title']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress_percentage', 'enrollment_date']
    list_filter = ['status', 'course', 'enrollment_date']
    search_fields = ['user__username', 'course__title']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'lesson__module__course']
    search_fields = ['enrollment__user__username', 'lesson__title']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'certificate_id', 'issued_date']
    search_fields = ['enrollment__user__username', 'certificate_id']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'amount', 'payment_status', 'payment_date']
    list_filter = ['payment_status', 'payment_date']
    search_fields = ['enrollment__user__username', 'transaction_id']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'course__title', 'review_text']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']