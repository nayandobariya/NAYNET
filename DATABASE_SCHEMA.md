# 📊 Job Portal Database Schema

## Database Overview

The Job Portal Django WebApp uses a relational database with multiple interconnected tables. The system supports both SQLite (development) and MySQL (production) databases.

## 📋 Table of Contents

- [Entity Relationship Diagram](#-entity-relationship-diagram)
- [Core Tables](#-core-tables)
- [User Management Tables](#-user-management-tables)
- [Job Management Tables](#-job-management-tables)
- [Assessment System Tables](#-assessment-system-tables)
- [Interview Management Tables](#-interview-management-tables)
- [Social Features Tables](#-social-features-tables)
- [System Tables](#-system-tables)
- [Relationships Summary](#-relationships-summary)

## 🏗️ Entity Relationship Diagram

```
══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                        🎯 JOB PORTAL DATABASE SCHEMA - ER DIAGRAM
══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                               🔐 USER MANAGEMENT SYSTEM                                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                     │
│  ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐                                   │
│  │   account_user      │◄────┤  jobapp_student    │     │  jobapp_teacher    │                                   │
│  │  (Primary Table)    │1:1  │  (Extension)       │     │  (Extension)       │                                   │
│  │                     │     │                     │     │                     │                                   │
│  │  • id (PK)          │     │  • id (PK)          │     │  • id (PK)          │                                   │
│  │  • email (UNIQUE)   │     │  • user_id (FK,UK)  │     │  • user_id (FK,UK)  │                                   │

## 📊 Core Tables

### 1. account_user (User Management)
**Primary Key:** id (AutoField)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| password | VARCHAR(128) | NOT NULL | Hashed password |
| last_login | DateTime | NULL | Last login timestamp |
| is_superuser | Boolean | NOT NULL | Superuser status |
| first_name | VARCHAR(150) | NOT NULL | User's first name |
| last_name | VARCHAR(150) | NOT NULL | User's last name |
| email | VARCHAR(254) | UNIQUE, NOT NULL | User's email address |
| is_staff | Boolean | NOT NULL | Staff status |
| is_active | Boolean | NOT NULL | Account active status |
| date_joined | DateTime | NOT NULL | Account creation date |
| role | VARCHAR(10) | NOT NULL | User role (employer/employee) |
| gender | VARCHAR(1) | NOT NULL | User gender (M/F) |
| profile_picture | VARCHAR(100) | NULL | Profile picture path |

**Indexes:**
- email (UNIQUE)
- role
- is_active

## 👥 User Management Tables

### 2. jobapp_student
**Primary Key:** id (AutoField)
**Foreign Key:** user_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | UNIQUE, NOT NULL, FK | Reference to User |
| profile_pic | VARCHAR(100) | NULL | Student profile picture |
| address | VARCHAR(40) | NULL | Student address |
| mobile | VARCHAR(20) | NULL | Student mobile number |

**Relationships:**
- One-to-One with account_user
- Referenced by jobapp_result

### 3. jobapp_teacher
**Primary Key:** id (AutoField)
**Foreign Key:** user_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | UNIQUE, NOT NULL, FK | Reference to User |
| profile_pic | VARCHAR(100) | NULL | Teacher profile picture |
| address | VARCHAR(40) | NULL | Teacher address |
| mobile | VARCHAR(20) | NULL | Teacher mobile number |
| status | Boolean | NOT NULL | Teacher employment status |
| salary | Integer | NULL | Teacher salary |

**Relationships:**
- One-to-One with account_user

## 💼 Job Management Tables

### 4. jobapp_category
**Primary Key:** id (AutoField)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| name | VARCHAR(50) | NOT NULL | Category name |

**Relationships:**
- Referenced by jobapp_job (One-to-Many)

### 5. jobapp_job
**Primary Key:** id (AutoField)
**Foreign Keys:**
- user_id → account_user(id)
- category_id → jobapp_category(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | Job poster (employer) |
| title | VARCHAR(300) | NOT NULL | Job title |
| description | TEXT | NOT NULL | Job description |
| location | VARCHAR(300) | NOT NULL | Job location |
| job_type | VARCHAR(1) | NOT NULL | Job type (1=Full, 2=Part, 3=Intern) |
| category_id | Integer | NOT NULL, FK | Job category |
| salary | VARCHAR(30) | BLANK | Salary range |
| company_name | VARCHAR(300) | NOT NULL | Company name |
| company_description | TEXT | NULL | Company description |
| url | VARCHAR(200) | NOT NULL | Company website |
| last_date | Date | NOT NULL | Application deadline |
| is_published | Boolean | NOT NULL | Publication status |
| is_closed | Boolean | NOT NULL | Job closure status |
| timestamp | DateTime | NOT NULL | Creation timestamp |

**Relationships:**
- Many-to-One with account_user (employer)
- Many-to-One with jobapp_category
- Referenced by jobapp_applicant (One-to-Many)
- Referenced by jobapp_bookmarkjob (One-to-Many)
- Referenced by jobapp_interviewround (One-to-Many)

### 6. jobapp_applicant
**Primary Key:** id (AutoField)
**Foreign Keys:**
- user_id → account_user(id)
- job_id → jobapp_job(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | Applicant user |
| job_id | Integer | NOT NULL, FK | Applied job |
| resume | VARCHAR(100) | NULL | Resume file path |
| timestamp | DateTime | NOT NULL | Application timestamp |

**Relationships:**
- Many-to-One with account_user (applicant)
- Many-to-One with jobapp_job
- Referenced by jobapp_interviewselection (One-to-Many)

**Unique Constraints:**
- (user_id, job_id) - User can apply once per job

### 7. jobapp_bookmarkjob
**Primary Key:** id (AutoField)
**Foreign Keys:**
- user_id → account_user(id)
- job_id → jobapp_job(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | User who bookmarked |
| job_id | Integer | NOT NULL, FK | Bookmarked job |
| timestamp | DateTime | NOT NULL | Bookmark timestamp |

**Relationships:**
- Many-to-One with account_user
- Many-to-One with jobapp_job

## 📚 Assessment System Tables

### 8. jobapp_course
**Primary Key:** id (AutoField)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| course_name | VARCHAR(50) | NOT NULL | Course/Quiz name |
| question_number | Integer | NOT NULL | Number of questions |
| marks_per_question | Integer | NOT NULL | Marks per question |
| total_marks | Integer | NOT NULL | Total marks |

**Relationships:**
- Referenced by jobapp_question (One-to-Many)
- Referenced by jobapp_result (One-to-Many)

### 9. jobapp_question
**Primary Key:** id (AutoField)
**Foreign Key:** course_id → jobapp_course(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| course_id | Integer | NOT NULL, FK | Associated course |
| marks | Integer | NOT NULL | Question marks |
| question | VARCHAR(600) | NOT NULL | Question text |
| option1 | VARCHAR(200) | NOT NULL | Option 1 |
| option2 | VARCHAR(200) | NOT NULL | Option 2 |
| option3 | VARCHAR(200) | NOT NULL | Option 3 |
| option4 | VARCHAR(200) | NOT NULL | Option 4 |
| answer | VARCHAR(200) | NOT NULL | Correct answer |

**Relationships:**
- Many-to-One with jobapp_course

### 10. jobapp_result
**Primary Key:** id (AutoField)
**Foreign Keys:**
- student_id → jobapp_student(id)
- exam_id → jobapp_course(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| student_id | Integer | NOT NULL, FK | Student who took exam |
| exam_id | Integer | NOT NULL, FK | Exam/Course taken |
| marks | Integer | NOT NULL | Marks obtained |
| date | DateTime | NOT NULL | Exam completion date |

**Relationships:**
- Many-to-One with jobapp_student
- Many-to-One with jobapp_course

## 🎯 Interview Management Tables

### 11. jobapp_interviewround
**Primary Key:** id (AutoField)
**Foreign Key:** job_id → jobapp_job(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| job_id | Integer | NOT NULL, FK | Associated job |
| round_type | VARCHAR(10) | NOT NULL | Interview round type |
| is_active | Boolean | NOT NULL | Round active status |
| created_at | DateTime | NOT NULL | Creation timestamp |

**Relationships:**
- Many-to-One with jobapp_job
- Referenced by jobapp_interviewselection (One-to-Many)

### 12. jobapp_interviewselection
**Primary Key:** id (AutoField)
**Foreign Keys:**
- interview_round_id → jobapp_interviewround(id)
- applicant_id → jobapp_applicant(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| interview_round_id | Integer | NOT NULL, FK | Interview round |
| applicant_id | Integer | NOT NULL, FK | Selected applicant |
| total_score | Float | NOT NULL | Combined score |
| selected_for_next_round | Boolean | NOT NULL | Selection status |
| salary_offer | Decimal(10,2) | NULL | Offered salary |
| email_sent | Boolean | NOT NULL | Email notification status |
| created_at | DateTime | NOT NULL | Selection timestamp |

**Relationships:**
- Many-to-One with jobapp_interviewround
- Many-to-One with jobapp_applicant
- Referenced by jobapp_interviewsession (One-to-One)

**Unique Constraints:**
- (interview_round_id, applicant_id) - One selection per round per applicant

### 13. jobapp_interviewsession
**Primary Key:** id (AutoField)
**Foreign Keys:**
- interview_selection_id → jobapp_interviewselection(id)
- interviewer_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| interview_selection_id | Integer | UNIQUE, NOT NULL, FK | Interview selection |
| session_id | VARCHAR(100) | UNIQUE, NOT NULL | Session identifier |
| interviewer_id | Integer | NOT NULL, FK | Interviewer user |
| scheduled_at | DateTime | NULL | Scheduled date/time |
| completed | Boolean | NOT NULL | Completion status |
| feedback | TEXT | NULL | Interview feedback |
| final_salary | Decimal(10,2) | NULL | Final salary offer |
| created_at | DateTime | NOT NULL | Session creation timestamp |

**Relationships:**
- One-to-One with jobapp_interviewselection
- Many-to-One with account_user (interviewer)

## 👥 Social Features Tables

### 14. account_post
**Primary Key:** id (AutoField)
**Foreign Key:** author_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| author_id | Integer | NOT NULL, FK | Post author |
| content | TEXT | NOT NULL | Post content |
| image | VARCHAR(100) | NULL | Post image |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

**Relationships:**
- Many-to-One with account_user
- Referenced by account_like (One-to-Many)
- Referenced by account_comment (One-to-Many)

### 15. account_like
**Primary Key:** id (AutoField)
**Foreign Keys:**
- user_id → account_user(id)
- post_id → account_post(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | User who liked |
| post_id | Integer | NOT NULL, FK | Liked post |
| created_at | DateTime | NOT NULL | Like timestamp |

**Relationships:**
- Many-to-One with account_user
- Many-to-One with account_post

**Unique Constraints:**
- (user_id, post_id) - User can like a post once

### 16. account_comment
**Primary Key:** id (AutoField)
**Foreign Keys:**
- user_id → account_user(id)
- post_id → account_post(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | Comment author |
| post_id | Integer | NOT NULL, FK | Commented post |
| content | TEXT | NOT NULL | Comment content |
| created_at | DateTime | NOT NULL | Comment timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

**Relationships:**
- Many-to-One with account_user
- Many-to-One with account_post

### 17. account_message
**Primary Key:** id (AutoField)
**Foreign Keys:**
- sender_id → account_user(id)
- receiver_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| sender_id | Integer | NOT NULL, FK | Message sender |
| receiver_id | Integer | NOT NULL, FK | Message receiver |
| content | TEXT | NOT NULL | Message content |
| is_read | Boolean | NOT NULL | Read status |
| created_at | DateTime | NOT NULL | Message timestamp |

**Relationships:**
- Many-to-One with account_user (sender)
- Many-to-One with account_user (receiver)

### 18. account_follow
**Primary Key:** id (AutoField)
**Foreign Keys:**
- follower_id → account_user(id)
- following_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| follower_id | Integer | NOT NULL, FK | Following user |
| following_id | Integer | NOT NULL, FK | Followed user |
| created_at | DateTime | NOT NULL | Follow timestamp |

**Relationships:**
- Many-to-One with account_user (follower)
- Many-to-One with account_user (following)

**Unique Constraints:**
- (follower_id, following_id) - User can follow another user once

### 19. account_connectionrequest
**Primary Key:** id (AutoField)
**Foreign Keys:**
- sender_id → account_user(id)
- receiver_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| sender_id | Integer | NOT NULL, FK | Request sender |
| receiver_id | Integer | NOT NULL, FK | Request receiver |
| status | VARCHAR(20) | NOT NULL | Request status |
| created_at | DateTime | NOT NULL | Request timestamp |

**Relationships:**
- Many-to-One with account_user (sender)
- Many-to-One with account_user (receiver)

**Unique Constraints:**
- (sender_id, receiver_id) - One request per user pair

## 🔧 System Tables

### 20. jobapp_uservisit
**Primary Key:** id (AutoField)
**Foreign Key:** user_id → account_user(id)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| user_id | Integer | NOT NULL, FK | Visiting user |
| ip_address | VARCHAR(39) | NOT NULL | User IP address |
| user_agent | TEXT | NOT NULL | Browser user agent |
| path | VARCHAR(500) | NOT NULL | Visited URL path |
| method | VARCHAR(10) | NOT NULL | HTTP method |
| timestamp | DateTime | NOT NULL | Visit timestamp |

**Relationships:**
- Many-to-One with account_user

### 21. jobapp_contact
**Primary Key:** id (AutoField)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| first_name | VARCHAR(100) | NOT NULL | Contact first name |
| last_name | VARCHAR(100) | NOT NULL | Contact last name |
| email | VARCHAR(254) | NOT NULL | Contact email |
| subject | VARCHAR(200) | NOT NULL | Contact subject |
| message | TEXT | NOT NULL | Contact message |
| timestamp | DateTime | NOT NULL | Contact timestamp |

### 22. account_cv
**Primary Key:** id (AutoField)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique identifier |
| title | VARCHAR(100) | NOT NULL | CV title |
| pdf | VARCHAR(100) | NOT NULL | PDF file path |

## 🔗 Relationships Summary

### One-to-One Relationships
- `account_user` ↔ `jobapp_student`
- `account_user` ↔ `jobapp_teacher`
- `jobapp_interviewselection` ↔ `jobapp_interviewsession`

### One-to-Many Relationships
- `account_user` → `jobapp_job` (employer posts jobs)
- `account_user` → `jobapp_applicant` (user applies to jobs)
- `account_user` → `jobapp_bookmarkjob` (user bookmarks jobs)
- `account_user` → `jobapp_interviewsession` (user conducts interviews)
- `account_user` → `jobapp_uservisit` (user visits pages)
- `jobapp_category` → `jobapp_job` (category contains jobs)
- `jobapp_job` → `jobapp_applicant` (job has applicants)
- `jobapp_job` → `jobapp_bookmarkjob` (job is bookmarked)
- `jobapp_job` → `jobapp_interviewround` (job has interview rounds)
- `jobapp_course` → `jobapp_question` (course has questions)
- `jobapp_course` → `jobapp_result` (course has results)
- `jobapp_interviewround` → `jobapp_interviewselection` (round has selections)
- `jobapp_applicant` → `jobapp_interviewselection` (applicant is selected)
- `jobapp_student` → `jobapp_result` (student takes exams)

### Many-to-Many Relationships (through intermediate tables)
- `account_user` ↔ `account_user` (follow - through `account_follow`)
- `account_user` ↔ `account_user` (messages - through `account_message`)
- `account_user` ↔ `account_user` (connection requests - through `account_connectionrequest`)
- `account_user` ↔ `account_post` (likes - through `account_like`)
- `account_user` ↔ `account_post` (comments - through `account_comment`)

## 📈 Database Statistics

### Table Counts
- **Core Tables:** 3 (user, student, teacher)
- **Job Management:** 4 (category, job, applicant, bookmark)
- **Assessment:** 3 (course, question, result)
- **Interview:** 3 (round, selection, session)
- **Social:** 5 (post, like, comment, message, follow)
- **System:** 4 (visit, contact, cv, connection_request)

**Total Tables:** 22

### Key Relationships
- **User-centric:** Most tables connect back to the user system
- **Job-centric:** Job applications and interviews revolve around job postings
- **Assessment-centric:** Quiz system integrated with job applications
- **Social-centric:** Community features for networking

### Performance Considerations
- **Indexes:** Primary keys, foreign keys, and frequently queried fields
- **Constraints:** Unique constraints prevent duplicate relationships
- **Cascade Deletes:** Foreign key constraints maintain data integrity
- **Timestamps:** Audit trail for all major operations

---

**Database Schema Version:** 1.0
**Last Updated:** January 2025
**Django Version:** 4.2.27
**Supported Databases:** SQLite, MySQL
