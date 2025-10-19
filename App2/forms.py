from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, Course, Module, Task, Quiz, QuizQuestion, Discussion, DiscussionReply, Lesson, Enrollment, Review, ContactMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Div, HTML
from crispy_bootstrap5.bootstrap5 import BS5Accordion


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Full Name")
    last_name = forms.CharField(max_length=30, required=False)  # We'll combine first and last for full name
    phone = forms.CharField(max_length=15, required=True, label="Mobile Number")
    college = forms.CharField(max_length=100, required=True, label="College of Graduation")
    education = forms.ChoiceField(
        choices=[
            ('undergraduate', 'Undergraduate'),
            ('graduate', 'Graduate'),
            ('postgraduate', 'Postgraduate'),
            ('others', 'Others')
        ],
        required=True,
        label="Education Level"
    )
    state = forms.ChoiceField(
        choices=[
            ('andhra_pradesh', 'Andhra Pradesh'),
            ('telangana', 'Telangana'),
            ('tamil_nadu', 'Tamil Nadu'),
            ('karnataka', 'Karnataka'),
            ('maharashtra', 'Maharashtra'),
            ('others', 'Others')
        ],
        required=True,
        label="State"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Create Your Account',
                'username',
                'email',
                'first_name',
                'phone',
                'college',
                'education',
                'state',
                'password1',
                'password2',
            ),
            ButtonHolder(
                Submit('submit', 'Register', css_class='btn btn-primary btn-lg w-100')
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                college=self.cleaned_data['college'],
                education=self.cleaned_data['education'],
                state=self.cleaned_data['state']
            )
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Login to Your Account',
                'username',
                'password',
            ),
            ButtonHolder(
                Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100')
            )
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'college', 'education', 'state', 'profile_image', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Update Profile',
                'phone',
                'college',
                'education',
                'state',
                'profile_image',
                'date_of_birth',
            ),
            ButtonHolder(
                Submit('submit', 'Update Profile', css_class='btn btn-primary')
            )
        )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'short_description', 'thumbnail', 'cover_image',
                 'course_type', 'price', 'category', 'level', 'duration_hours', 'instructor',
                 'prerequisites', 'learning_objectives', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'learning_objectives': forms.Textarea(attrs={'rows': 3}),
            'prerequisites': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Course Information',
                'title',
                'description',
                'short_description',
                'thumbnail',
                'cover_image',
                'course_type',
                'price',
                'category',
                'level',
                'duration_hours',
                'instructor',
                'prerequisites',
                'learning_objectives',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', 'Save Course', css_class='btn btn-primary')
            )
        )


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Module Information',
                'title',
                'description',
                'order',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', 'Save Module', css_class='btn btn-primary')
            )
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'content_file', 'video_url',
                 'text_content', 'coding_instructions', 'duration_minutes', 'order',
                 'is_required', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Task Information',
                'title',
                'description',
                'task_type',
                'content_file',
                'video_url',
                'text_content',
                'coding_instructions',
                'duration_minutes',
                'order',
                'is_required',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', 'Save Task', css_class='btn btn-primary')
            )
        )


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit_minutes', 'passing_score', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Quiz Information',
                'title',
                'description',
                'time_limit_minutes',
                'passing_score',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', 'Save Quiz', css_class='btn btn-primary')
            )
        )


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'question_type', 'options', 'correct_answer', 'explanation', 'points', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Question Information',
                'question_text',
                'question_type',
                'options',
                'correct_answer',
                'explanation',
                'points',
                'order',
            ),
            ButtonHolder(
                Submit('submit', 'Save Question', css_class='btn btn-primary')
            )
        )


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Start Discussion',
                'title',
                'content',
            ),
            ButtonHolder(
                Submit('submit', 'Post Discussion', css_class='btn btn-primary')
            )
        )


class DiscussionReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'content',
            ButtonHolder(
                Submit('submit', 'Post Reply', css_class='btn btn-primary')
            )
        )


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'content_type', 'content_file', 'video_url',
                 'text_content', 'duration_minutes', 'order', 'is_preview', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Lesson Information',
                'title',
                'description',
                'content_type',
                'content_file',
                'video_url',
                'text_content',
                'duration_minutes',
                'order',
                'is_preview',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', 'Save Lesson', css_class='btn btn-primary')
            )
        )


class EnrollmentForm(forms.Form):
    course_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'course_id',
            ButtonHolder(
                Submit('submit', 'Enroll Now', css_class='btn btn-success btn-lg')
            )
        )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Write a Review',
                'rating',
                'review_text',
            ),
            ButtonHolder(
                Submit('submit', 'Submit Review', css_class='btn btn-primary')
            )
        )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Contact Us',
                'name',
                'email',
                'subject',
                'message',
            ),
            ButtonHolder(
                Submit('submit', 'Send Message', css_class='btn btn-primary')
            )
        )


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Reset Your Password',
                'email',
            ),
            ButtonHolder(
                Submit('submit', 'Send Reset Link', css_class='btn btn-primary')
            )
        )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Set New Password',
                'new_password1',
                'new_password2',
            ),
            ButtonHolder(
                Submit('submit', 'Set Password', css_class='btn btn-primary')
            )
        )