import os
import django
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import requests
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj1.settings')
django.setup()

from App2.models import Course, Module, Lesson

def download_image(url, filename):
    """Download image from URL and return as Django File object"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Create Django File object directly from content
        from io import BytesIO
        django_file = File(BytesIO(response.content), name=filename)
        return django_file
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def create_course(title, description, short_description, category, level, course_type, price, instructor, duration_hours, thumbnail_url=None):
    """Create a course with thumbnail"""
    from django.utils.text import slugify
    import uuid

    # Generate unique slug
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Course.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    course = Course.objects.create(
        title=title,
        slug=slug,
        description=description,
        short_description=short_description,
        category=category,
        level=level,
        course_type=course_type,
        price=price,
        instructor=instructor,
        duration_hours=duration_hours,
        is_active=True
    )

    # Download and set thumbnail if URL provided
    if thumbnail_url:
        filename = f"{title.lower().replace(' ', '_')}_thumbnail.jpg"
        image_file = download_image(thumbnail_url, filename)
        if image_file:
            course.thumbnail.save(filename, image_file, save=True)
            image_file.close()

    return course

def create_module(course, title, description, order):
    """Create a module for a course"""
    return Module.objects.create(
        course=course,
        title=title,
        description=description,
        order=order,
        is_active=True
    )

def create_lesson(module, title, description, content_type, video_url, duration_minutes, order):
    """Create a lesson for a module"""
    return Lesson.objects.create(
        module=module,
        title=title,
        description=description,
        content_type=content_type,
        video_url=video_url,
        duration_minutes=duration_minutes,
        order=order,
        is_active=True
    )

# Clear existing data
print("Clearing existing courses...")
Course.objects.all().delete()

# Course data with thumbnails
courses_data = [
    # FREE COURSES
    {
        'title': 'Python Programming Fundamentals',
        'description': 'Master Python programming from basics to advanced concepts. Learn variables, data structures, functions, OOP, and build real-world applications.',
        'short_description': 'Complete Python programming course for beginners to advanced learners',
        'category': 'Programming',
        'level': 'beginner',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 40,
        'thumbnail_url': 'https://img.youtube.com/vi/rfscVS0vtbw/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Python Basics',
                'description': 'Introduction to Python programming language',
                'lessons': [
                    ('Introduction to Python', 'Learn what Python is and why it\'s popular', 'video', 'https://www.youtube.com/watch?v=rfscVS0vtbw', 15),
                    ('Installing Python', 'Set up Python development environment', 'video', 'https://www.youtube.com/watch?v=Kn1HF3oD19c', 10),
                    ('Variables and Data Types', 'Understanding variables, strings, numbers, booleans', 'video', 'https://www.youtube.com/watch?v=k9TUPpGqYTo', 20),
                    ('Basic Input/Output', 'Working with print() and input() functions', 'video', 'https://www.youtube.com/watch?v=4u2ClNCtcgY', 15),
                ]
            },
            {
                'title': 'Control Structures',
                'description': 'Learn about loops and conditional statements',
                'lessons': [
                    ('If-Else Statements', 'Conditional programming in Python', 'video', 'https://www.youtube.com/watch?v=AWek49wXGzI', 20),
                    ('For Loops', 'Iterating through sequences', 'video', 'https://www.youtube.com/watch?v=94UHCEmprCY', 18),
                    ('While Loops', 'Conditional looping', 'video', 'https://www.youtube.com/watch?v=6TEagWqLMO8', 15),
                    ('Break and Continue', 'Loop control statements', 'video', 'https://www.youtube.com/watch?v=4TGZ9VN4qSc', 12),
                ]
            },
            {
                'title': 'Data Structures',
                'description': 'Lists, tuples, dictionaries, and sets',
                'lessons': [
                    ('Lists in Python', 'Creating and manipulating lists', 'video', 'https://www.youtube.com/watch?v=W8KRzm-HUcc', 25),
                    ('Tuples and Sets', 'Immutable sequences and unique collections', 'video', 'https://www.youtube.com/watch?v=WcJgW-KbxCk', 20),
                    ('Dictionaries', 'Key-value pair data structures', 'video', 'https://www.youtube.com/watch?v=daefaLgNkw0', 22),
                    ('List Comprehensions', 'Advanced list operations', 'video', 'https://www.youtube.com/watch?v=3dt4OGnU5sM', 18),
                ]
            },
            {
                'title': 'Functions and Modules',
                'description': 'Creating reusable code with functions',
                'lessons': [
                    ('Defining Functions', 'Function syntax and parameters', 'video', 'https://www.youtube.com/watch?v=9Os0o3wzS_I', 20),
                    ('Return Values', 'Getting data back from functions', 'video', 'https://www.youtube.com/watch?v=Vt0C3MP2Bis', 15),
                    ('Lambda Functions', 'Anonymous functions', 'video', 'https://www.youtube.com/watch?v=25ovCm9jKfA', 12),
                    ('Modules and Packages', 'Organizing code into modules', 'video', 'https://www.youtube.com/watch?v=sugvnHA7ElY', 18),
                ]
            },
        ]
    },
    {
        'title': 'C Programming Language',
        'description': 'Learn C programming from scratch. Understand memory management, pointers, data structures, and build efficient C applications.',
        'short_description': 'Comprehensive C programming course with practical examples',
        'category': 'Programming',
        'level': 'beginner',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 35,
        'thumbnail_url': 'https://img.youtube.com/vi/KJgsSFOSQv0/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Introduction to C',
                'description': 'Getting started with C programming',
                'lessons': [
                    ('What is C Programming?', 'Overview of C language and its importance', 'video', 'https://www.youtube.com/watch?v=KJgsSFOSQv0', 15),
                    ('Setting up C Environment', 'Installing compilers and IDEs', 'video', 'https://www.youtube.com/watch?v=oT2K2V8Uvfg', 12),
                    ('First C Program', 'Writing and running Hello World', 'video', 'https://www.youtube.com/watch?v=io2blgoT6Rs', 10),
                    ('Basic Syntax', 'Understanding C program structure', 'video', 'https://www.youtube.com/watch?v=8PopR3x-AME', 18),
                ]
            },
            {
                'title': 'Variables and Data Types',
                'description': 'Understanding data types and variables in C',
                'lessons': [
                    ('Data Types in C', 'int, float, char, and more', 'video', 'https://www.youtube.com/watch?v=8PopR3x-AME', 20),
                    ('Variables and Constants', 'Declaring and using variables', 'video', 'https://www.youtube.com/watch?v=5vX7QXd5R5A', 15),
                    ('Type Conversion', 'Implicit and explicit casting', 'video', 'https://www.youtube.com/watch?v=8PopR3x-AME', 12),
                    ('Input/Output Functions', 'printf() and scanf()', 'video', 'https://www.youtube.com/watch?v=io2blgoT6Rs', 18),
                ]
            },
        ]
    },
    {
        'title': 'Java Programming Fundamentals',
        'description': 'Complete Java programming course covering OOP concepts, collections, exception handling, and building Java applications.',
        'short_description': 'Master Java programming with hands-on projects',
        'category': 'Programming',
        'level': 'intermediate',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 45,
        'thumbnail_url': 'https://img.youtube.com/vi/eIrMbAQSU34/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Java Basics',
                'description': 'Introduction to Java programming',
                'lessons': [
                    ('Introduction to Java', 'What is Java and why learn it?', 'video', 'https://www.youtube.com/watch?v=eIrMbAQSU34', 15),
                    ('Installing Java JDK', 'Setting up Java development environment', 'video', 'https://www.youtube.com/watch?v=OllgnTf6YNU', 12),
                    ('First Java Program', 'Hello World in Java', 'video', 'https://www.youtube.com/watch?v=Hl-zzrqQoSE', 10),
                    ('Java Syntax Basics', 'Variables, data types, operators', 'video', 'https://www.youtube.com/watch?v=GoXwIVyNvX0', 20),
                ]
            },
            {
                'title': 'Object-Oriented Programming',
                'description': 'Core OOP concepts in Java',
                'lessons': [
                    ('Classes and Objects', 'Creating classes and objects', 'video', 'https://www.youtube.com/watch?v=8yjkWGRlUmY', 25),
                    ('Inheritance', 'Extending classes and method overriding', 'video', 'https://www.youtube.com/watch?v=8yjkWGRlUmY', 20),
                    ('Polymorphism', 'Method overloading and overriding', 'video', 'https://www.youtube.com/watch?v=8yjkWGRlUmY', 18),
                    ('Encapsulation', 'Data hiding and access modifiers', 'video', 'https://www.youtube.com/watch?v=8yjkWGRlUmY', 15),
                ]
            },
        ]
    },
    {
        'title': 'Linux Operating System',
        'description': 'Master Linux command line, file system management, user administration, and system configuration for developers and IT professionals.',
        'short_description': 'Complete Linux course for developers and system administrators',
        'category': 'System Administration',
        'level': 'beginner',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 30,
        'thumbnail_url': 'https://img.youtube.com/vi/ROjZy1WbCIA/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Linux Fundamentals',
                'description': 'Introduction to Linux operating system',
                'lessons': [
                    ('What is Linux?', 'Understanding Linux and its distributions', 'video', 'https://www.youtube.com/watch?v=ROjZy1WbCIA', 15),
                    ('Installing Linux', 'Setting up Linux environment', 'video', 'https://www.youtube.com/watch?v=L0Y4MH-K8pY', 12),
                    ('Linux Desktop Environment', 'GUI vs Command Line', 'video', 'https://www.youtube.com/watch?v=ivniiSG0oqc', 10),
                    ('Basic Navigation', 'pwd, ls, cd commands', 'video', 'https://www.youtube.com/watch?v=IVquJh3DXUA', 18),
                ]
            },
            {
                'title': 'File System Management',
                'description': 'Working with files and directories',
                'lessons': [
                    ('File Operations', 'Creating, copying, moving files', 'video', 'https://www.youtube.com/watch?v=e9gU3QeYzXc', 20),
                    ('Directory Operations', 'mkdir, rmdir, tree commands', 'video', 'https://www.youtube.com/watch?v=IVquJh3DXUA', 15),
                    ('File Permissions', 'chmod, chown, file permissions', 'video', 'https://www.youtube.com/watch?v=D-VdSO1VOYg', 22),
                    ('Text Processing', 'grep, sed, awk commands', 'video', 'https://www.youtube.com/watch?v=IVquJh3DXUA', 18),
                ]
            },
        ]
    },
    {
        'title': 'React.js Frontend Development',
        'description': 'Learn modern React.js development with hooks, state management, routing, and build responsive web applications.',
        'short_description': 'Complete React.js course with modern practices',
        'category': 'Frontend Development',
        'level': 'intermediate',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 38,
        'thumbnail_url': 'https://img.youtube.com/vi/bMknfKXIFA8/maxresdefault.jpg',
        'modules': [
            {
                'title': 'React Fundamentals',
                'description': 'Introduction to React.js',
                'lessons': [
                    ('What is React?', 'Understanding React and its benefits', 'video', 'https://www.youtube.com/watch?v=bMknfKXIFA8', 15),
                    ('Setting up React', 'Creating React applications', 'video', 'https://www.youtube.com/watch?v=Ke90Tje7VS0', 12),
                    ('JSX Syntax', 'Writing JSX components', 'video', 'https://www.youtube.com/watch?v=Ke90Tje7VS0', 18),
                    ('Components and Props', 'Creating reusable components', 'video', 'https://www.youtube.com/watch?v=Ke90Tje7VS0', 20),
                ]
            },
            {
                'title': 'State and Hooks',
                'description': 'Managing state in React applications',
                'lessons': [
                    ('useState Hook', 'Managing component state', 'video', 'https://www.youtube.com/watch?v=O6P86uwfdR0', 22),
                    ('useEffect Hook', 'Handling side effects', 'video', 'https://www.youtube.com/watch?v=O6P86uwfdR0', 18),
                    ('Custom Hooks', 'Creating reusable hook logic', 'video', 'https://www.youtube.com/watch?v=O6P86uwfdR0', 15),
                    ('Context API', 'Global state management', 'video', 'https://www.youtube.com/watch?v=O6P86uwfdR0', 20),
                ]
            },
        ]
    },
    {
        'title': 'Node.js Backend Development',
        'description': 'Build scalable backend applications with Node.js, Express, MongoDB, and RESTful APIs.',
        'short_description': 'Complete Node.js backend development course',
        'category': 'Backend Development',
        'level': 'intermediate',
        'course_type': 'free',
        'price': 0,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 42,
        'thumbnail_url': 'https://img.youtube.com/vi/Oe421EPjeBE/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Node.js Fundamentals',
                'description': 'Introduction to Node.js',
                'lessons': [
                    ('What is Node.js?', 'Understanding server-side JavaScript', 'video', 'https://www.youtube.com/watch?v=Oe421EPjeBE', 15),
                    ('Installing Node.js', 'Setting up Node.js environment', 'video', 'https://www.youtube.com/watch?v=Oe421EPjeBE', 10),
                    ('NPM Package Manager', 'Managing dependencies', 'video', 'https://www.youtube.com/watch?v=Oe421EPjeBE', 12),
                    ('First Node.js App', 'Creating Hello World server', 'video', 'https://www.youtube.com/watch?v=Oe421EPjeBE', 18),
                ]
            },
            {
                'title': 'Express.js Framework',
                'description': 'Building web applications with Express',
                'lessons': [
                    ('Express Basics', 'Setting up Express server', 'video', 'https://www.youtube.com/watch?v=L72fhGm1tfE', 20),
                    ('Routing', 'Handling different HTTP routes', 'video', 'https://www.youtube.com/watch?v=L72fhGm1tfE', 18),
                    ('Middleware', 'Using Express middleware', 'video', 'https://www.youtube.com/watch?v=L72fhGm1tfE', 15),
                    ('Error Handling', 'Managing errors in Express apps', 'video', 'https://www.youtube.com/watch?v=L72fhGm1tfE', 22),
                ]
            },
        ]
    },

    # PAID COURSES
    {
        'title': 'Full Stack Web Development',
        'description': 'Complete full-stack development course covering frontend (React), backend (Node.js), database (MongoDB), and deployment.',
        'short_description': 'Become a full-stack developer with modern technologies',
        'category': 'Full Stack Development',
        'level': 'advanced',
        'course_type': 'paid',
        'price': 1299,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 80,
        'thumbnail_url': 'https://img.youtube.com/vi/7H1b8vjJG6g/maxresdefault.jpg',
        'modules': [
            {
                'title': 'Frontend Development with React',
                'description': 'Building modern user interfaces',
                'lessons': [
                    ('Advanced React Patterns', 'Higher-order components and render props', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 30),
                    ('State Management with Redux', 'Managing complex application state', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 35),
                    ('React Router', 'Client-side routing', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 25),
                    ('Testing React Apps', 'Unit and integration testing', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 28),
                ]
            },
            {
                'title': 'Backend Development with Node.js',
                'description': 'Building scalable server-side applications',
                'lessons': [
                    ('RESTful API Design', 'Creating robust APIs', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 32),
                    ('Authentication & Security', 'JWT, OAuth, security best practices', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 35),
                    ('Database Integration', 'Working with MongoDB', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 30),
                    ('Deployment & DevOps', 'Deploying to production', 'video', 'https://www.youtube.com/watch?v=7H1b8vjJG6g', 28),
                ]
            },
        ]
    },
    {
        'title': 'E-commerce Website Development',
        'description': 'Build a complete e-commerce platform with payment integration, inventory management, and admin dashboard.',
        'short_description': 'Create professional e-commerce websites from scratch',
        'category': 'Web Development',
        'level': 'advanced',
        'course_type': 'paid',
        'price': 1299,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 75,
        'thumbnail_url': 'https://img.youtube.com/vi/0W6i5LYKCSI/maxresdefault.jpg',
        'modules': [
            {
                'title': 'E-commerce Fundamentals',
                'description': 'Understanding e-commerce business logic',
                'lessons': [
                    ('E-commerce Architecture', 'Planning your online store', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 25),
                    ('Product Management', 'Adding and managing products', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 30),
                    ('Shopping Cart System', 'Building cart functionality', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 35),
                    ('Order Processing', 'Handling customer orders', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 28),
                ]
            },
            {
                'title': 'Payment Integration',
                'description': 'Integrating payment gateways and security',
                'lessons': [
                    ('Payment Gateway Setup', 'Integrating Stripe/PayPal', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 32),
                    ('Security Best Practices', 'PCI compliance and data protection', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 28),
                    ('Order Fulfillment', 'Managing order lifecycle', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 30),
                    ('Analytics & Reporting', 'Tracking sales and performance', 'video', 'https://www.youtube.com/watch?v=0W6i5LYKCSI', 25),
                ]
            },
        ]
    },
    {
        'title': 'Mobile App Development',
        'description': 'Learn cross-platform mobile app development with React Native. Build iOS and Android apps simultaneously.',
        'short_description': 'Create mobile apps for iOS and Android with React Native',
        'category': 'Mobile Development',
        'level': 'intermediate',
        'course_type': 'paid',
        'price': 1299,
        'instructor': 'FUTURE BOUND TECH',
        'duration_hours': 70,
        'thumbnail_url': 'https://img.youtube.com/vi/0-S5a0eXPoc/maxresdefault.jpg',
        'modules': [
            {
                'title': 'React Native Fundamentals',
                'description': 'Introduction to React Native development',
                'lessons': [
                    ('Setting up React Native', 'Development environment setup', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 20),
                    ('React Native Components', 'Core components and APIs', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 25),
                    ('Navigation in React Native', 'React Navigation library', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 22),
                    ('Styling Mobile Apps', 'Styling with StyleSheet', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 18),
                ]
            },
            {
                'title': 'Advanced Mobile Features',
                'description': 'Camera, location, push notifications',
                'lessons': [
                    ('Device APIs', 'Camera, GPS, sensors access', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 30),
                    ('Push Notifications', 'Firebase Cloud Messaging', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 25),
                    ('App Store Deployment', 'Publishing to App Store and Play Store', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 28),
                    ('Performance Optimization', 'Optimizing React Native apps', 'video', 'https://www.youtube.com/watch?v=0-S5a0eXPoc', 22),
                ]
            },
        ]
    },
]

print("Creating courses...")

for course_data in courses_data:
    print(f"Creating course: {course_data['title']}")

    # Create course
    course = create_course(
        title=course_data['title'],
        description=course_data['description'],
        short_description=course_data['short_description'],
        category=course_data['category'],
        level=course_data['level'],
        course_type=course_data['course_type'],
        price=course_data['price'],
        instructor=course_data['instructor'],
        duration_hours=course_data['duration_hours'],
        thumbnail_url=course_data.get('thumbnail_url')
    )

    # Create modules and lessons
    for module_order, module_data in enumerate(course_data['modules'], 1):
        print(f"  Creating module: {module_data['title']}")

        module = create_module(
            course=course,
            title=module_data['title'],
            description=module_data['description'],
            order=module_order
        )

        # Create lessons
        for lesson_order, (title, content, content_type, video_url, duration) in enumerate(module_data['lessons'], 1):
            print(f"    Creating lesson: {title}")

            create_lesson(
                module=module,
                title=title,
                description=content,
                content_type=content_type,
                video_url=video_url,
                duration_minutes=duration,
                order=lesson_order
            )

print("\nAll courses created successfully!")
print(f"Created {len(courses_data)} courses with modules and lessons.")
print("\nFree Courses:")
free_courses = [c for c in courses_data if c['course_type'] == 'free']
for course in free_courses:
    print(f"- {course['title']} ({course['duration_hours']} hours)")

print("\nPaid Courses:")
paid_courses = [c for c in courses_data if c['course_type'] == 'paid']
for course in paid_courses:
    print(f"- {course['title']} (Rs.{course['price']}) - {course['duration_hours']} hours")