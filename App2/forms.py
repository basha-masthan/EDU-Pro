from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, Course, Module, Task, Quiz, QuizQuestion, Discussion, DiscussionReply, Lesson, Enrollment, Review, ContactMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Div, HTML
from crispy_bootstrap5.bootstrap5 import BS5Accordion


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    first_name = forms.CharField(max_length=30, required=True, label="Full Name", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your full name'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter last name (optional)'
    }))
    phone = forms.CharField(max_length=15, required=True, label="Mobile Number", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your mobile number',
        'pattern': r'^\+?1?\d{9,15}$',
        'title': 'Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
    }))
    college = forms.CharField(max_length=100, required=True, label="College of Graduation", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your college name'
    }))
    education = forms.ChoiceField(
        choices=[
            ('', 'Select Education Level'),
            ('undergraduate', 'Undergraduate'),
            ('graduate', 'Graduate'),
            ('postgraduate', 'Postgraduate'),
            ('others', 'Others')
        ],
        required=True,
        label="Education Level",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    state = forms.ChoiceField(
        choices=[
            ('', 'Select State'),
            ('andhra_pradesh', 'Andhra Pradesh'),
            ('telangana', 'Telangana'),
            ('tamil_nadu', 'Tamil Nadu'),
            ('karnataka', 'Karnataka'),
            ('maharashtra', 'Maharashtra'),
            ('others', 'Others')
        ],
        required=True,
        label="State",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
            if field_name == 'password1':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Create a strong password (min 8 characters)'
                })
            elif field_name == 'password2':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Confirm your password'
                })

        # Remove Crispy Forms helper to use standard Django forms
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.layout = Layout(...)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Basic phone validation - should start with + or digit, 10-15 digits
        import re
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
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