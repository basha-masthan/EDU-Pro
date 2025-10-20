# FUTURE BOUND TECH - Online Learning Platform

A comprehensive Django-based online learning platform with cyberpunk theme, featuring courses, progress tracking, and admin management.

## Features

- **User Authentication**: Registration, login, and profile management
- **Course Management**: Create and manage courses with modules and lessons
- **Progress Tracking**: Track user progress through courses with detailed analytics
- **Admin Dashboard**: Complete admin interface for managing users, courses, and content
- **Responsive Design**: Cyberpunk-themed UI that works on all devices
- **Certificate Generation**: Issue certificates upon course completion

## Tech Stack

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Bootstrap 5, Custom CSS, JavaScript
- **Deployment**: Render
- **Static Files**: WhiteNoise

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd future-bound-tech
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Deployment to Render

### Prerequisites
- Render account
- GitHub repository

### Deployment Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Render Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure build settings:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn proj1.wsgi:application --bind 0.0.0.0:$PORT`

3. **Environment Variables**
   Set these in Render's Environment section:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   DATABASE_URL=postgresql://... (from Render's PostgreSQL database)
   ```

4. **Database Setup**
   - Create a PostgreSQL database in Render
   - Copy the DATABASE_URL to environment variables
   - The app will automatically run migrations on first deploy

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## Project Structure

```
future-bound-tech/
├── proj1/                 # Django project settings
├── App2/                  # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL patterns
│   ├── forms.py          # Django forms
│   └── admin.py          # Admin configuration
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── requirements.txt      # Python dependencies
├── runtime.txt          # Python version for Render
├── render.yaml          # Render deployment config
├── build.sh             # Build script
└── .env.example         # Environment variables template
```

## Key Features

### For Students
- Browse and enroll in courses
- Track learning progress
- Access course materials and videos
- Take quizzes and assessments
- Download certificates
- Review completed courses

### For Administrators
- User management
- Course creation and management
- Module and lesson management
- Progress analytics
- Content management

## Security Features

- CSRF protection
- Secure password hashing
- Environment variable configuration
- Debug mode disabled in production
- HTTPS enforcement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email info@futureboundtech.com or create an issue in the repository.