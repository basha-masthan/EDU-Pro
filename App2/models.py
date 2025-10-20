from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UserProfile(models.Model):
    EDUCATION_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('others', 'Others')
    ]

    STATE_CHOICES = [
        ('andhra_pradesh', 'Andhra Pradesh'),
        ('telangana', 'Telangana'),
        ('tamil_nadu', 'Tamil Nadu'),
        ('karnataka', 'Karnataka'),
        ('maharashtra', 'Maharashtra'),
        ('others', 'Others')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    college = models.CharField(max_length=200, blank=True, verbose_name="College of Graduation")
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"


class Course(models.Model):
    COURSE_TYPES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]

    CATEGORY_TYPES = [
        ('knowledge', 'Knowledge Course'),
        ('internship', 'Internship'),
        ('project', 'Project'),
        ('specialization', 'Specialization'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/')
    cover_image = models.ImageField(upload_to='courses/covers/', blank=True, null=True)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='knowledge')
    level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    duration_hours = models.PositiveIntegerField(default=0)
    instructor = models.CharField(max_length=100)
    prerequisites = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_total_modules(self):
        return self.modules.count()

    def get_total_lessons(self):
        return sum(module.get_lesson_count() for module in self.modules.all())

    def get_total_duration(self):
        return sum(module.get_duration() for module in self.modules.all())


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_lesson_count(self):
        return self.lessons.count()

    def get_duration(self):
        return sum(lesson.duration_minutes for lesson in self.lessons.all())


class Task(models.Model):
    TASK_TYPES = [
        ('reading', 'Reading'),
        ('video', 'Video'),
        ('coding', 'Coding Exercise'),
        ('upload', 'File Upload'),
        ('quiz', 'Quiz'),
    ]

    module = models.ForeignKey('Module', related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default='reading')
    content_file = models.FileField(upload_to='tasks/content/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    text_content = models.TextField(blank=True)
    coding_instructions = models.TextField(blank=True, help_text="Instructions for coding tasks")
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Quiz(models.Model):
    module = models.OneToOneField('Module', related_name='quiz', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    passing_score = models.PositiveIntegerField(default=70, help_text="Percentage required to pass")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Quiz for {self.module.title}"


class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    options = models.JSONField(blank=True, null=True, help_text="For multiple choice: ['option1', 'option2', ...]")
    correct_answer = models.CharField(max_length=500, help_text="For multiple choice: index or text, for true/false: 'true'/'false'")
    explanation = models.TextField(blank=True, help_text="Explanation of the correct answer")
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order + 1}: {self.question_text[:50]}"


class Discussion(models.Model):
    course = models.ForeignKey(Course, related_name='discussions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    class Meta:
        ordering = ['-is_pinned', '-created_at']


class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply by {self.user.username}"

    class Meta:
        ordering = ['created_at']


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Text/PDF'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='video')
    content_file = models.FileField(upload_to='lessons/content/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    text_content = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(default=timezone.now)
    completion_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    certificate_issued = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=True)  # True for free courses, False until paid for premium

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    def update_progress(self):
        """Update enrollment progress with precise calculation to prevent bulk completion"""
        total_lessons = self.course.get_total_lessons()
        if total_lessons == 0:
            self.progress_percentage = 100.00
        else:
            completed_lessons = Progress.objects.filter(
                enrollment=self,
                is_completed=True
            ).count()
            # Use higher precision to prevent rounding errors that could cause bulk completion
            progress = (completed_lessons / total_lessons) * 100
            self.progress_percentage = round(progress, 6)  # Use 6 decimal places for precision
        self.save()

        # Update status based on progress - only mark as completed when truly 100%
        if self.progress_percentage >= 100.00 and self.status != 'completed':
            self.status = 'completed'
            self.completion_date = timezone.now()
            self.save()
        elif self.progress_percentage > 0 and self.status == 'enrolled':
            self.status = 'in_progress'
            self.save()


class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"

    def mark_completed(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            self.enrollment.update_progress()


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    issued_date = models.DateTimeField(default=timezone.now)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"Certificate for {self.enrollment.user.username} - {self.enrollment.course.title}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=50, default='razorpay')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateTimeField(blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment for {self.enrollment.course.title} by {self.enrollment.user.username}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username}'s review of {self.course.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"