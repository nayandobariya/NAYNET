<<<<<<< HEAD
# Job Portal Django WebApp: Resume Analysis & Scoring with NLP and ML

[![Django](https://img.shields.io/badge/Django-4.2.27-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Django-based Job Portal web application featuring advanced resume analysis and scoring using Natural Language Processing (NLP) and Machine Learning techniques. The system automates resume screening, candidate evaluation, and interview management with intelligent scoring algorithms.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛠️ Technology Stack](#️-technology-stack)
- [📊 Database Schema](#-database-schema)
- [🚀 Installation Guide](#-installation-guide)
- [⚙️ Configuration](#️-configuration)
- [📖 Usage Guide](#-usage-guide)
- [🔧 API Documentation](#-api-documentation)
- [🤖 NLP & ML Implementation](#-nlp--ml-implementation)
- [🚀 Deployment](#-deployment)
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Overview

This Job Portal application revolutionizes the recruitment process by combining traditional job portal functionality with cutting-edge AI-powered resume analysis. The system uses advanced NLP techniques and LSTM-based machine learning models to automatically score and rank resumes based on job requirements, significantly reducing manual screening efforts and improving hiring efficiency.

### 🎯 Core Objectives

- **Automated Resume Screening**: AI-powered analysis of resumes against job descriptions
- **Intelligent Candidate Scoring**: Multi-factor scoring including resume analysis and quiz performance
- **Streamlined Recruitment**: End-to-end job posting, application, and interview management
- **Advanced Analytics**: Comprehensive dashboards for employers and administrators

## ✨ Key Features

### 👥 User Management
- **Dual Role System**: Separate interfaces for Employers and Candidates
- **Secure Authentication**: Django's built-in authentication with role-based access
- **Profile Management**: Comprehensive user profiles with additional information

### 💼 Employer Features
- **Job Posting**: Rich job descriptions with detailed requirements
- **Candidate Management**: View, filter, and manage job applications
- **Interview Management**: Schedule and conduct online interviews
- **Quiz Creation**: Custom assessment quizzes for job-specific evaluations
- **Analytics Dashboard**: Real-time insights into recruitment metrics

### 👨‍💻 Candidate Features
- **Job Search & Application**: Advanced search with filtering capabilities
- **Resume Upload**: Support for multiple file formats (PDF, DOCX)
- **Quiz Participation**: Automated assessment system
- **Application Tracking**: Real-time status updates
- **Interview Scheduling**: Integrated interview management

### 🤖 AI-Powered Features
- **Resume Analysis**: NLP-based content extraction and analysis
- **Intelligent Scoring**: ML algorithms for relevance assessment
- **Automated Ranking**: Smart candidate prioritization
- **Category Classification**: Job-specific categorization

### 👨‍💼 Admin Features
- **System Management**: Complete administrative control
- **User Management**: CRUD operations for all user types
- **Content Moderation**: Job and application oversight
- **Analytics & Reporting**: Comprehensive system analytics
- **Database Management**: Multi-database support (SQLite/MySQL)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/CSS/JS) │◄──►│   Django        │◄──►│   SQLite/MySQL  │
│                 │    │   Views/Models  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   NLP Engine    │    │   ML Models     │
│   (Django)      │◄──►│   (NLTK/spaCy)  │◄──►│   (LSTM/TF)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🏛️ Architectural Components

- **Presentation Layer**: Django Templates with Bootstrap styling
- **Application Layer**: Django Views, Forms, and Business Logic
- **Data Layer**: Django ORM with multi-database support
- **AI Layer**: NLP processing and ML model inference
- **Background Tasks**: Celery for asynchronous processing

## 🛠️ Technology Stack

### Backend Framework
- **Django 4.2.27**: High-level Python web framework
- **Python 3.11+**: Core programming language

### Database
- **SQLite**: Default lightweight database
- **MySQL**: Production-ready database option
- **Redis**: Caching and message broker

### Frontend
- **HTML5/CSS3**: Semantic markup and styling
- **JavaScript**: Dynamic client-side functionality
- **Bootstrap**: Responsive UI framework
- **Chart.js**: Data visualization

### AI & ML
- **NLTK**: Natural Language Processing toolkit
- **spaCy**: Advanced NLP library
- **TensorFlow/Keras**: Deep learning framework
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation and analysis

### Additional Tools
- **Celery**: Distributed task queue
- **Django Channels**: WebSocket support
- **Pillow**: Image processing
- **django-ckeditor**: Rich text editing
- **django-taggit**: Tagging functionality

## 📊 Database Schema

### Core Models

#### User Management
```python
User (AbstractUser):
    - email (unique)
    - role (employer/employee)
    - gender
    - profile_picture

Student:
    - user (OneToOneField)
    - profile_pic
    - address, mobile

Teacher:
    - user (OneToOneField)
    - profile_pic
    - address, mobile, status, salary
```

#### Job Management
```python
Category:
    - name

Job:
    - user (ForeignKey)
    - title, description
    - tags (TaggableManager)
    - location, job_type
    - category (ForeignKey)
    - salary, company_name
    - last_date, is_published, is_closed

Applicant:
    - user (ForeignKey)
    - job (ForeignKey)
    - resume (FileField)
    - timestamp

BookmarkJob:
    - user (ForeignKey)
    - job (ForeignKey)
    - timestamp
```

#### Assessment System
```python
Course:
    - course_name
    - question_number, total_marks

Question:
    - course (ForeignKey)
    - marks, question
    - option1-4, answer

Result:
    - student (ForeignKey)
    - exam (ForeignKey)
    - marks
```

#### Interview Management
```python
InterviewRound:
    - job (ForeignKey)
    - round_type, is_active

InterviewSelection:
    - interview_round (ForeignKey)
    - applicant (ForeignKey)
    - total_score, selected_for_next_round
    - salary_offer

InterviewSession:
    - interview_selection (OneToOneField)
    - session_id, interviewer
    - scheduled_at, completed
    - feedback, final_salary
```

## 🚀 Installation Guide

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git
- MySQL (optional, for production)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Job-Portal-Django-WebApp-Resume-Analysis-Scoring-NLP-ML.git
   cd Job-Portal-Django-WebApp-Resume-Analysis-Scoring-NLP-ML
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # Linux/Mac
   python -m venv env
   source env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # For SQLite (default)
   python manage.py migrate

   # For MySQL (configure settings.py first)
   python manage.py migrate --database=mysql
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load Sample Data (Optional)**
   ```bash
   python manage.py populate_data
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Main Application: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://user:password@localhost:3306/jobportal
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
Update `job/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobportal',
        'USER': 'your-username',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Email Configuration
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 📖 Usage Guide

### For Employers

1. **Registration & Login**
   - Register as an employer
   - Complete your profile

2. **Job Management**
   - Post new jobs with detailed descriptions
   - Create assessment quizzes
   - Review and manage applications

3. **Candidate Evaluation**
   - View applicant resumes and scores
   - Schedule interviews
   - Make hiring decisions

### For Candidates

1. **Registration & Login**
   - Register as a candidate
   - Upload your resume and complete profile

2. **Job Search**
   - Browse available jobs
   - Use filters to find relevant positions
   - Save interesting jobs

3. **Application Process**
   - Apply to jobs with resume upload
   - Take assessment quizzes
   - Participate in interviews

### For Administrators

1. **System Management**
   - Access admin panel at `/admin/`
   - Manage users, jobs, and applications
   - View system analytics

2. **Content Moderation**
   - Moderate job postings
   - Handle user reports
   - Manage system settings

## 🔧 API Documentation

### REST API Endpoints

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

#### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job

#### Applications
- `GET /api/applications/` - List user applications
- `POST /api/applications/` - Submit application
- `GET /api/applications/{id}/` - Get application details

#### Resume Analysis
- `POST /api/analyze-resume/` - Analyze resume
- `GET /api/analysis/{id}/` - Get analysis results

### WebSocket Endpoints
- `/ws/interview/{session_id}/` - Real-time interview communication

## 🤖 NLP & ML Implementation

### Resume Analysis Pipeline

1. **Text Extraction**
   - PDF/DOCX parsing using PyPDF2/docx
   - Text cleaning and normalization

2. **NLP Processing**
   ```python
   # Tokenization and preprocessing
   tokens = nltk.word_tokenize(text)
   lemmatized = [lemmatizer.lemmatize(token) for token in tokens]

   # Feature extraction
   vectorizer = TfidfVectorizer()
   features = vectorizer.fit_transform([text])
   ```

3. **ML Classification**
   ```python
   # LSTM model for relevance scoring
   model = Sequential([
       Embedding(max_words, embedding_dim, input_length=max_len),
       LSTM(128, return_sequences=True),
       LSTM(64),
       Dense(32, activation='relu'),
       Dense(1, activation='sigmoid')
   ])
   ```

### Scoring Algorithm

The final candidate score is calculated as:
```
Final Score = (Resume Score × 0.7) + (Quiz Score × 0.3)
```

Where:
- **Resume Score**: AI-generated relevance score (0-100)
- **Quiz Score**: Performance in assessment quiz (0-100)

## 🚀 Deployment

### Docker Deployment

1. **Build Docker Image**
   ```bash
   docker build -t job-portal .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Production Deployment

1. **Environment Setup**
   ```bash
   export DJANGO_SETTINGS_MODULE=job.settings.production
   export DEBUG=False
   export SECRET_KEY=your-production-secret-key
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

4. **Gunicorn Setup**
   ```bash
   gunicorn job.wsgi:application --bind 0.0.0.0:8000
   ```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/static/files/;
    }
}
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
python manage.py dbshell
```

#### Migration Issues
```bash
# Reset migrations
python manage.py reset_db
python manage.py migrate
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
```

#### Email Not Sending
```bash
# Test email settings
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Performance Optimization

1. **Database Indexing**
   ```python
   # Add indexes to frequently queried fields
   class Meta:
       indexes = [
           models.Index(fields=['created_at']),
           models.Index(fields=['user', 'job']),
       ]
   ```

2. **Caching**
   ```python
   from django.core.cache import cache

   # Cache expensive operations
   @cache_page(60 * 15)  # 15 minutes
   def job_list_view(request):
       # View logic
   ```

3. **Background Tasks**
   ```python
   # Use Celery for heavy processing
   @shared_task
   def analyze_resume(resume_id):
       # Resume analysis logic
   ```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**
4. **Run Tests**
   ```bash
   python manage.py test
   ```
5. **Submit Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@jobportal.com
- Documentation: [Wiki](https://github.com/yourusername/Job-Portal-Django-WebApp-Resume-Analysis-Scoring-NLP-ML/wiki)

## 🙏 Acknowledgments

- Django Framework Community
- NLTK and spaCy contributors
- TensorFlow/Keras teams
- Open source community

---

**Made with ❤️ by the Job Portal Development Team**
=======
# NAYNET
>>>>>>> da9cc4e1a4201546f287c64ff6595413f0416365
