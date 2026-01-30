from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from datetime import datetime
import json
import os
from .models import *
from .forms import *
from .permission import user_is_employer, user_is_employee
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    from .resume_nlp import rankall, cvanalysis
    import pandas as pd
    import nltk
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass
except Exception as e:
    print(f"Resume analysis tools failed to load: {e}")
    rankall = None
    cvanalysis = None
    pd = None

@user_is_employer
def select_candidates_view(request, job_id):
    if request.user.is_staff:
        job = get_object_or_404(Job, id=job_id)
    else:
        job = get_object_or_404(Job, id=job_id, user=request.user.id)
    interview_round_2 = InterviewRound.objects.filter(job=job, round_type='round2').first()
    if not interview_round_2:
        interview_round_2 = InterviewRound.objects.create(job=job, round_type='round2')

    if request.method == 'POST':
        selected_applicant_ids = request.POST.getlist('selected_applicants')
        salary_offer_str = request.POST.get('salary_offer', '').strip()
        salary_offer = float(salary_offer_str) if salary_offer_str else None

        for applicant_id in selected_applicant_ids:
            applicant = get_object_or_404(Applicant, id=applicant_id, job=job)
            # Calculate total score
            total_score = 0
            # Add resume score logic here if needed
            # Add quiz score
            try:
                course = Course.objects.get(course_name=job.title)
                student = Student.objects.get(user=applicant.user)
                results = Result.objects.filter(exam=course, student=student)
                if results:
                    total_score += results.first().marks
            except:
                pass

            selection, created = InterviewSelection.objects.get_or_create(
                interview_round=interview_round_2,
                applicant=applicant,
                defaults={
                    'total_score': total_score,
                    'selected_for_next_round': True,
                    'salary_offer': salary_offer
                }
            )
            if not created:
                selection.selected_for_next_round = True
                selection.salary_offer = salary_offer
                selection.save()

            # Create interview session if it doesn't exist
            from django.utils.crypto import get_random_string
            session_id = get_random_string(10)
            session, created = InterviewSession.objects.get_or_create(
                interview_selection=selection,
                defaults={
                    'session_id': session_id,
                    'interviewer': request.user,  # Job poster is the interviewer
                    'scheduled_at': None,  # To be scheduled later
                }
            )

            # Send interview invitation email if session was just created
            if created:
                from .tasks import send_interview_invitation_email
                try:
                    send_interview_invitation_email.delay(session.id)
                except Exception as e:
                    print(f"Celery not available for interview invitation, sending synchronously: {e}")
                    send_interview_invitation_email(session.id)

            # Send email
            from .tasks import send_salary_offer_email
            try:
                send_salary_offer_email.delay(selection.id)
            except Exception as e:
                # If Celery is not available, send synchronously
                print(f"Celery not available, sending email synchronously: {e}")
                send_salary_offer_email(selection.id)

        print(f"DEBUG: Selected applicants: {selected_applicant_ids}")
        print(f"DEBUG: Salary offer: {salary_offer}")
        messages.success(request, 'Candidates selected and emails sent!')
        return redirect('jobapp:applicants', id=job_id)

    # Get all applicants with scores
    all_applicants = Applicant.objects.filter(job=job)
    applicant_data = []
    for applicant in all_applicants:
        total_score = 0
        try:
            course = Course.objects.get(course_name=job.title)
            student = Student.objects.get(user=applicant.user)
            results = Result.objects.filter(exam=course, student=student)
            if results:
                total_score += results.first().marks
        except:
            pass
        applicant_data.append({
            'applicant': applicant,
            'total_score': total_score
        })

    # Sort by score
    applicant_data.sort(key=lambda x: x['total_score'], reverse=True)

    context = {
        'job': job,
        'applicant_data': applicant_data,
        'interview_round_2': interview_round_2
    }
    return render(request, 'jobapp/select_candidates.html', context)




@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def apply_job_view(request, id):

    form = JobApplyForm(request.POST or None, request.FILES or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = Applicant.objects.filter(user=user, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                # Send email using Celery (Job Poster will get resume, Applicant will get confirmation)
                from .tasks import send_job_application_email, send_job_application_email_sync
                try:
                    send_job_application_email.delay(instance.id)
                except Exception as e:
                    # Fallback to sync if Celery is not running
                    print(f"Celery not available for application, sending synchronously: {e}")
                    send_job_application_email_sync(instance.id)

                messages.success(
                    request, 'You have successfully applied for this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:

        messages.error(request, 'You already applied for the Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
def dashboard_view(request,id=id):
    """
    """
    jobs = []
    savedjobs = []
    appliedjobs = []
    interview_sessions = []
    total_applicants = {}
    if request.user.role == 'employer':

        jobs = Job.objects.filter(user=request.user.id)
        for job in jobs:
            count = Applicant.objects.filter(job=job.id).count()
            total_applicants[job.id] = count

    if request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user.id)
        appliedjobs = Applicant.objects.filter(user=request.user.id)

        # Get interview sessions for the employee
        interview_sessions = InterviewSession.objects.filter(
            interview_selection__applicant__user=request.user
        ).order_by('-created_at')

    context = {

        'jobs': jobs,
        'savedjobs': savedjobs,
        'appliedjobs':appliedjobs,
        'interview_sessions': interview_sessions,
        'total_applicants': total_applicants,
        'id' :id
    }

    return render(request, 'jobapp/dashboard.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def employer_jobs_table_view(request):
    """
    Return the jobs table HTML for AJAX refresh
    """
    jobs = Job.objects.filter(user=request.user.id)
    total_applicants = {}
    for job in jobs:
        count = Applicant.objects.filter(job=job.id).count()
        total_applicants[job.id] = count

    context = {
        'jobs': jobs,
        'total_applicants': total_applicants,
    }

    return render(request, 'jobapp/employer_jobs_table.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def delete_job_view(request, id):
    if request.user.is_staff:
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Your Job Post was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def make_complete_job_view(request, id):
    if request.user.is_staff:
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:
        try:
            job.is_closed = True
            job.save()
            messages.success(request, 'Your Job was marked closed!')
        except:
            messages.success(request, 'Something went wrong !')
            
    return redirect('jobapp:dashboard')

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def publish_job_view(request, id):
    if request.user.is_staff:
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:
        try:
            job.is_published = True
            job.save()
            messages.success(request, 'Your Job was successfully published!')
        except:
            messages.success(request, 'Something went wrong !')
            
    return redirect('jobapp:dashboard')



@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def all_applicants_view(request, id):
    if request.user.is_staff:
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, user=request.user.id)
    print(job.category)
    category=job.category.name
    print(type(category),category)
    all_applicants = Applicant.objects.filter(job=id)
    applicantnames=[]
    applicantresults=[]
    resume_paths = []
    print(all_applicants )
    try:
        course = Course.objects.get(course_name=job.title)
        #print(applicant.user.get_full_name)
        for applicant in all_applicants:
            username=applicant.user.get_full_name()
            student = Student.objects.get(user=applicant.user)
            results = Result.objects.all().filter(exam=course).filter(student=student)
            for t in results:
                if t.exam ==course:
                    applicantresults.append(t.marks)
            applicantnames.append(username)
            # Use actual resume path if exists, else None
            if applicant.resume:
                resume_paths.append(applicant.resume.path)
            else:
                resume_paths.append(None)
            print(username)
    except Course.DoesNotExist:
        # If no course exists for this job title, skip quiz results
        for applicant in all_applicants:
            username=applicant.user.get_full_name()
            applicantnames.append(username)
            applicantresults.append(0)  # Default to 0 marks if no quiz
            # Use actual resume path if exists, else None
            if applicant.resume:
                resume_paths.append(applicant.resume.path)
            else:
                resume_paths.append(None)

    print(applicantnames)
    print(applicantresults)
    print(resume_paths)
    # Filter out applicants without resumes
    valid_indices = [i for i, path in enumerate(resume_paths) if path is not None]
    valid_names = [applicantnames[i] for i in valid_indices]
    valid_paths = [resume_paths[i] for i in valid_indices]
    valid_results = [applicantresults[i] for i in valid_indices]

    if valid_paths and rankall is not None:
        cvsresults= rankall(valid_paths, valid_names)
        print('cvsresults=',cvsresults)
        cvsresults1=cvsresults['Resumepath']
        # Handle case where category doesn't match predefined categories
        if category in cvsresults.columns:
            cvsresults2=cvsresults[[category]]
        else:
            # If category not found, use the first available category or default to zeros
            available_categories = [col for col in cvsresults.columns if col != 'Resumepath']
            if available_categories:
                cvsresults2=cvsresults[[available_categories[0]]]
            else:
                # Create a column of zeros if no categories available
                if pd is not None:
                    cvsresults2 = pd.DataFrame({category: [0] * len(cvsresults)}, index=cvsresults.index)
                else:
                    cvsresults2 = []
        print(cvsresults1,cvsresults2)
        results= []
        keys=['name','score','marks']
        names=cvsresults1.values
        score=cvsresults2.values
        for i in range(len(valid_names)):
            results.append({'name':names[i],'score':score[i][0],'marks':valid_results[i]})
    else:
        # No valid resumes or rankall not available, create empty results
        results = []
        cvsresults1 = []
        cvsresults2 = []

    # Get interview round 2 and sessions for the template
    interview_round_2 = InterviewRound.objects.filter(job=job, round_type='round2').first()
    interview_sessions = []
    if interview_round_2:
        interview_sessions = InterviewSession.objects.filter(
            interview_selection__interview_round=interview_round_2
        ).order_by('-scheduled_at')

    # Sort results by total score
    sorted_results = []
    for result in results:
        total_score = result.get('score', 0) + result.get('marks', 0)
        result['total_score'] = total_score
        # Check if applicant is selected for round 2
        try:
            applicant = Applicant.objects.get(user__get_full_name=result['name'], job=job)
            selection = InterviewSelection.objects.filter(
                interview_round__job=job,
                interview_round__round_type='round2',
                applicant=applicant
            ).first()
            result['selected'] = selection.selected_for_next_round if selection else False
        except:
            result['selected'] = False
        sorted_results.append(result)

    sorted_results.sort(key=lambda x: x['total_score'], reverse=True)

    context = {
        'job': job,
        'all_applicants': all_applicants,
        'cvsresults1': cvsresults1,
        'cvsresults2': cvsresults2,
        'category': category,
        'applicantresults': applicantresults,
        'results': results,
        'sorted_results': sorted_results,
        'interview_round_2': interview_round_2,
        'interview_sessions': interview_sessions
    }

    return render(request, 'jobapp/all-applicants.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def delete_bookmark_view(request, id):

    job = get_object_or_404(BookmarkJob, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Saved Job was successfully deleted!')

    return redirect('jobapp:dashboard')

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def applicant_details_view(request, user_id, job_id):

    applicant = get_object_or_404(User, id=user_id)
    job = get_object_or_404(Job, id=job_id)
    print(applicant.get_full_name())

    # Find the specific applicant's resume from Applicant model
    try:
        applicant_obj = Applicant.objects.get(user=applicant, job=job)
        if applicant_obj.resume:
            filepath = applicant_obj.resume.path
            if not os.path.exists(filepath):
                # Try alternative path in media root directly
                alt_filepath = os.path.join(settings.MEDIA_ROOT, os.path.basename(filepath))
                if os.path.exists(alt_filepath):
                    filepath = alt_filepath
                else:
                    filepath = None
        else:
            # No resume uploaded, handle gracefully
            filepath = None
    except Applicant.DoesNotExist:
        filepath = None

    if filepath and cvanalysis:
        resultpath=settings.STATIC_IMAGE+str(applicant.get_full_name())+'.png'
        print(resultpath)
        try:
            Resumepath,CV,Categories,Score= cvanalysis(filepath, resultpath)
        except Exception as e:
            print(f"Error in cvanalysis: {e}")
            Categories, Score = [], []

        # Construct the correct URL
        if os.path.exists(filepath):
            if filepath.startswith(settings.MEDIA_ROOT):
                relative_path = os.path.relpath(filepath, settings.MEDIA_ROOT)
                cv_url = settings.MEDIA_URL + relative_path.replace('\\', '/')
            else:
                cv_url = None
        else:
            cv_url = None

        context = {
            'applicant': applicant,
            'Categories' : Categories,
            'Score' : Score,
            'CV': cv_url,
            'imageurl':static('images/'+str(applicant.get_full_name())+'.png')
        }
    else:
        # No resume or analysis tool not available, provide default values
        cv_url = None
        if filepath and os.path.exists(filepath):
            if filepath.startswith(settings.MEDIA_ROOT):
                relative_path = os.path.relpath(filepath, settings.MEDIA_ROOT)
                cv_url = settings.MEDIA_URL + relative_path.replace('\\', '/')

        context = {
            'applicant': applicant,
            'Categories' : [],
            'Score' : [],
            'CV': cv_url,
            'imageurl': None
        }

    return render(request, 'jobapp/applicant-details.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def job_bookmark_view(request, id):

    form = JobBookmarkForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = BookmarkJob.objects.filter(user=request.user.id, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                messages.success(
                    request, 'You have successfully save this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:
        messages.error(request, 'You already saved this Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def job_edit_view(request, id=id):
    """
    Handle Job Update

    """
    if request.user.is_staff:
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, user=request.user.id)
    categories = Category.objects.all()
    form = JobEditForm(request.POST or None, instance=job)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # for save tags
        # form.save_m2m()
        messages.success(request, 'Your Job Post Was Successfully Updated!')
        return redirect(reverse("jobapp:single-job", kwargs={
            'id': instance.id
        }))
    context = {

        'form': form,
        'categories': categories
    }

    return render(request, 'jobapp/job-edit.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def student_dashboard_view(request):
    courses = Course.objects.all()
    dict = {
        'total_course': courses.count(),
        'total_question': Question.objects.all().count(),
        'courses': courses,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'total_course': dict['total_course'],
            'total_question': dict['total_question'],
        }
        return JsonResponse(data)

    return render(request, 'student/student_dashboard.html', context=dict)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def student_exam_view(request):
    courses = Course.objects.all()
    return render(request, 'student/student_exam.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def take_exam_view(request, pk):
    course = Course.objects.get(id=pk)
    total_questions = Question.objects.all().filter(course=course).count()
    questions = Question.objects.all().filter(course=course)
    total_marks = 0
    for q in questions:
        total_marks = total_marks + q.marks

    return render(request, 'student/take_exam.html',
                  {'course': course, 'total_questions': total_questions, 'total_marks': total_marks})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def start_exam_view(request, pk):
    course = Course.objects.get(id=pk)
    student = Student.objects.get(user_id=request.user.id)
    # Check if student has already taken the exam
    existing_result = Result.objects.filter(exam=course, student=student).exists()
    if existing_result:
        messages.error(request, 'You have already taken this exam. You cannot take it again.')
        return redirect('jobapp:view-result')
    questions = Question.objects.all().filter(course=course)
    if request.method == 'POST':
        pass
    response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions})
    response.set_cookie('course_id', course.id)
    return response


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def calculate_marks_view(request):

    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = Course.objects.get(id=course_id)

        total_marks = 0
        questions = Question.objects.all().filter(course=course)
        for i in range(len(questions)):

            selected_ans = request.COOKIES.get(str(i + 1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = Student.objects.get(user_id=request.user.id)
        print(student)
        result = Result()
        result.marks = total_marks
        result.exam = course
        result.student = student
        result.save()

        courses = Course.objects.all()

        return render(request, 'student/view_result.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def view_result_view(request):
    courses = Course.objects.all()
    return render(request, 'student/view_result.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
def check_marks_view(request, pk):
    course = Course.objects.get(id=pk)
    try:
        student = Student.objects.get(user_id=request.user.id)
        results = Result.objects.all().filter(exam=course).filter(student=student)
        return render(request, 'student/check_marks.html', {'results': results})
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('jobapp:student-dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def student_marks_view(request):
    courses = Course.objects.all()
    return render(request, 'student/student_marks.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_dashboard_view(request):
    dict = {

        'total_course': Course.objects.all().count(),
        'total_question': Question.objects.all().count(),
        'total_student': Student.objects.all().count()
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'total_course': dict['total_course'],
            'total_question': dict['total_question'],
            'total_student': dict['total_student'],
        }
        return JsonResponse(data)

    return render(request, 'teacher/teacher_dashboard.html', context=dict)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_exam_view(request):
    courses = Course.objects.all()
    total_questions = sum(course.question_number for course in courses)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        courses_data = list(courses.values('id', 'course_name', 'question_number', 'total_marks'))
        return JsonResponse({'courses': courses_data})

    return render(request, 'teacher/teacher_exam.html', {'courses': courses, 'total_questions': total_questions})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_add_exam_view(request):
    courseForm = CourseForm()
    if request.method == 'POST':
        courseForm = CourseForm(request.POST)
        if courseForm.is_valid():
            # Save the form data
            course = courseForm.save()
            messages.success(request, f'Exam "{course.course_name}" added successfully!')
            return redirect('jobapp:teacher-view-exam')
        else:
            print("Form is invalid:", courseForm.errors)
            messages.error(request, 'Please correct the errors below.')
    return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_view_exam_view(request):
    courses = Course.objects.all()
    return render(request, 'teacher/teacher_view_exam.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def delete_exam_view(request, pk):
    if request.method == 'POST':
        try:
            course = Course.objects.get(id=pk)
            course.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Exam deleted successfully!'})
            else:
                messages.success(request, 'Exam deleted successfully!')
                return HttpResponseRedirect('/teacher/teacher-view-exam')
        except Course.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Exam not found!'})
            else:
                messages.error(request, 'Exam not found!')
                return HttpResponseRedirect('/teacher/teacher-view-exam')
    return HttpResponseRedirect('/teacher/teacher-view-exam')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_question_view(request):
    return render(request, 'teacher/teacher_question.html')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_add_question_view(request):
    questionForm =QuestionForm()
    if request.method == 'POST':
        questionForm =QuestionForm(request.POST)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            course = Course.objects.get(id=request.POST.get('courseID'))
            question.course = course
            question.save()
        else:
            print("form is invalid")
        courses = Course.objects.all()
        return render(request, 'teacher/teacher_view_question.html', {'courses': courses})
    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def teacher_view_question_view(request):
    courses = Course.objects.all()
    return render(request, 'teacher/teacher_view_question.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def see_question_view(request, pk):
    questions = Question.objects.all().filter(course_id=pk)
    return render(request, 'teacher/see_question.html', {'questions': questions})


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def remove_question_view(request, pk):
    question = Question.objects.get(id=pk)
    question.delete()
    courses = Course.objects.all()
    return render(request, 'teacher/teacher_view_question.html', {'courses': courses})


@login_required(login_url=reverse_lazy('account:login'))
def interview_session_view(request, session_id):
    session = get_object_or_404(InterviewSession, session_id=session_id)

    # Check if user is the interviewer or interviewee
    if request.user != session.interviewer and request.user != session.interview_selection.applicant.user:
        messages.error(request, 'You do not have permission to access this session.')
        return redirect('jobapp:dashboard')

    if request.method == 'POST' and request.user == session.interviewer:
        session.completed = True
        session.feedback = request.POST.get('feedback')
        final_salary_str = request.POST.get('final_salary', '').strip()
        if final_salary_str:
            try:
                session.final_salary = float(final_salary_str)
            except ValueError:
                session.final_salary = None
        else:
            session.final_salary = None
        session.completed_at = datetime.now()
        session.save()

        # Send interview completion email
        from .tasks import send_interview_completion_email
        try:
            send_interview_completion_email.delay(session.id)
        except Exception as e:
            # If Celery is not available, send synchronously
            print(f"Celery not available, sending email synchronously: {e}")
            result = send_interview_completion_email(session.id)
            if result.startswith("Failed"):
                messages.error(request, 'Interview completed but email sending failed.')
            else:
                messages.success(request, 'Interview completed and email sent!')

        messages.success(request, 'Interview completed and email sent!')
        return redirect('jobapp:dashboard')

    context = {
        'session': session,
        'is_interviewer': request.user == session.interviewer
    }
    return render(request, 'jobapp/interview_session.html', context)


# Custom Admin Panel Views
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard_view(request):
    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applicants = Applicant.objects.count()
    total_categories = Category.objects.count()
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()
    total_questions = Question.objects.count()
    total_results = Result.objects.count()
    total_bookmarks = BookmarkJob.objects.count()
    published_jobs = Job.objects.filter(is_published=True).count()
    closed_jobs = Job.objects.filter(is_closed=True).count()

    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applicants': total_applicants,
        'total_categories': total_categories,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_questions': total_questions,
        'total_results': total_results,
        'total_bookmarks': total_bookmarks,
        'published_jobs': published_jobs,
        'closed_jobs': closed_jobs,
    }
    return render(request, 'jobapp/admin_dashboard.html', context)

@staff_member_required
def admin_users_view(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'jobapp/admin_users.html', context)

@staff_member_required
def admin_jobs_view(request):
    jobs = Job.objects.all()
    context = {'jobs': jobs}
    return render(request, 'jobapp/admin_jobs.html', context)

@staff_member_required
def admin_applicants_view(request):
    applicants = Applicant.objects.all()
    context = {'applicants': applicants}
    return render(request, 'jobapp/admin_applicants.html', context)

# Admin CRUD Views for Users
@staff_member_required
def admin_user_create_view(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.email} created successfully.')
            return redirect('jobapp:admin-users')
    else:
        form = AdminUserForm()
    return render(request, 'jobapp/admin_user_create.html', {'form': form})

@staff_member_required
def admin_user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.email} updated successfully.')
            return redirect('jobapp:admin-users')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'jobapp/admin_user_edit.html', {'form': form, 'user': user})

@staff_member_required
def admin_user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.email} deleted successfully.')
        return redirect('jobapp:admin-users')
    return render(request, 'jobapp/admin_user_delete.html', {'user': user})

# Admin CRUD Views for Jobs
@staff_member_required
def admin_job_create_view(request):
    if request.method == 'POST':
        form = AdminJobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Job "{job.title}" created successfully.')
            return redirect('jobapp:admin-jobs')
    else:
        form = AdminJobForm()
    return render(request, 'jobapp/admin_job_create.html', {'form': form})

@staff_member_required
def admin_job_edit_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = AdminJobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Job "{job.title}" updated successfully.')
            return redirect('jobapp:admin-jobs')
    else:
        form = AdminJobForm(instance=job)
    return render(request, 'jobapp/admin_job_edit.html', {'form': form, 'job': job})

@staff_member_required
def admin_job_delete_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, f'Job "{job.title}" deleted successfully.')
        return redirect('jobapp:admin-jobs')
    return render(request, 'jobapp/admin_job_delete.html', {'job': job})

# Admin CRUD Views for Applicants
@staff_member_required
def admin_applicant_create_view(request):
    if request.method == 'POST':
        form = AdminApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save()
            messages.success(request, f'Applicant for {applicant.job.title} created successfully.')
            return redirect('jobapp:admin-applicants')
    else:
        form = AdminApplicantForm()
    return render(request, 'jobapp/admin_applicant_create.html', {'form': form})

@staff_member_required
def admin_applicant_edit_view(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    if request.method == 'POST':
        form = AdminApplicantForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            applicant = form.save()
            messages.success(request, f'Applicant for {applicant.job.title} updated successfully.')
            return redirect('jobapp:admin-applicants')
    else:
        form = AdminApplicantForm(instance=applicant)
    return render(request, 'jobapp/admin_applicant_edit.html', {'form': form, 'applicant': applicant})

@staff_member_required
def admin_applicant_delete_view(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    if request.method == 'POST':
        applicant.delete()
        messages.success(request, f'Applicant for {applicant.job.title} deleted successfully.')
        return redirect('jobapp:admin-applicants')
    return render(request, 'jobapp/admin_applicant_delete.html', {'applicant': applicant})

# Admin CRUD Views for Jobs - Publish and Close
@staff_member_required
def admin_job_publish_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.is_published = True
        job.save()
        messages.success(request, f'Job "{job.title}" published successfully.')
        return redirect('jobapp:admin-jobs')

@staff_member_required
def admin_job_close_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.is_closed = True
        job.save()
        messages.success(request, f'Job "{job.title}" closed successfully.')
        return redirect('jobapp:admin-jobs')

# Admin CRUD Views for Categories
@staff_member_required
def admin_category_create_view(request):
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('jobapp:admin-categories')
    else:
        form = AdminCategoryForm()
    return render(request, 'jobapp/admin_category_create.html', {'form': form})

@staff_member_required
def admin_category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('jobapp:admin-categories')
    else:
        form = AdminCategoryForm(instance=category)
    return render(request, 'jobapp/admin_category_edit.html', {'form': form, 'category': category})

@staff_member_required
def admin_category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('jobapp:admin-categories')
    return render(request, 'jobapp/admin_category_delete.html', {'category': category})

# Admin CRUD Views for Categories - List View
@staff_member_required
def admin_categories_view(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'jobapp/admin_categories.html', context)

# Admin CRUD Views for Students
@staff_member_required
def admin_students_view(request):
    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'jobapp/admin_students.html', context)

@staff_member_required
def admin_student_create_view(request):
    if request.method == 'POST':
        form = AdminStudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.user.get_full_name()}" created successfully.')
            return redirect('jobapp:admin-students')
    else:
        form = AdminStudentForm()
    return render(request, 'jobapp/admin_student_create.html', {'form': form})

@staff_member_required
def admin_student_edit_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = AdminStudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.user.get_full_name()}" updated successfully.')
            return redirect('jobapp:admin-students')
    else:
        form = AdminStudentForm(instance=student)
    return render(request, 'jobapp/admin_student_edit.html', {'form': form, 'student': student})

@staff_member_required
def admin_student_delete_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, f'Student "{student.user.get_full_name()}" deleted successfully.')
        return redirect('jobapp:admin-students')
    return render(request, 'jobapp/admin_student_delete.html', {'student': student})

# Admin CRUD Views for Teachers
@staff_member_required
def admin_teachers_view(request):
    teachers = Teacher.objects.all()
    context = {'teachers': teachers}
    return render(request, 'jobapp/admin_teachers.html', context)

@staff_member_required
def admin_teacher_create_view(request):
    if request.method == 'POST':
        form = AdminTeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher "{teacher.user.get_full_name()}" created successfully.')
            return redirect('jobapp:admin-teachers')
    else:
        form = AdminTeacherForm()
    return render(request, 'jobapp/admin_teacher_create.html', {'form': form})

@staff_member_required
def admin_teacher_edit_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = AdminTeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher "{teacher.user.get_full_name()}" updated successfully.')
            return redirect('jobapp:admin-teachers')
    else:
        form = AdminTeacherForm(instance=teacher)
    return render(request, 'jobapp/admin_teacher_edit.html', {'form': form, 'teacher': teacher})

@staff_member_required
def admin_teacher_delete_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, f'Teacher "{teacher.user.get_full_name()}" deleted successfully.')
        return redirect('jobapp:admin-teachers')
    return render(request, 'jobapp/admin_teacher_delete.html', {'teacher': teacher})

# Admin CRUD Views for Courses
@staff_member_required
def admin_courses_view(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'jobapp/admin_courses.html', context)

@staff_member_required
def admin_course_create_view(request):
    if request.method == 'POST':
        form = AdminCourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.course_name}" created successfully.')
            return redirect('jobapp:admin-courses')
    else:
        form = AdminCourseForm()
    return render(request, 'jobapp/admin_course_create.html', {'form': form})

@staff_member_required
def admin_course_edit_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = AdminCourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.course_name}" updated successfully.')
            return redirect('jobapp:admin-courses')
    else:
        form = AdminCourseForm(instance=course)
    return render(request, 'jobapp/admin_course_edit.html', {'form': form, 'course': course})

@staff_member_required
def admin_course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, f'Course "{course.course_name}" deleted successfully.')
        return redirect('jobapp:admin-courses')
    return render(request, 'jobapp/admin_course_delete.html', {'course': course})

# Admin CRUD Views for Questions
@staff_member_required
def admin_questions_view(request):
    questions = Question.objects.all()
    context = {'questions': questions}
    return render(request, 'jobapp/admin_questions.html', context)

@staff_member_required
def admin_question_create_view(request):
    if request.method == 'POST':
        form = AdminQuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'Question for "{question.course.course_name}" created successfully.')
            return redirect('jobapp:admin-questions')
    else:
        form = AdminQuestionForm()
    return render(request, 'jobapp/admin_question_create.html', {'form': form})

@staff_member_required
def admin_question_edit_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = AdminQuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'Question for "{question.course.course_name}" updated successfully.')
            return redirect('jobapp:admin-questions')
    else:
        form = AdminQuestionForm(instance=question)
    return render(request, 'jobapp/admin_question_edit.html', {'form': form, 'question': question})

@staff_member_required
def admin_question_delete_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, f'Question for "{question.course.course_name}" deleted successfully.')
        return redirect('jobapp:admin-questions')
    return render(request, 'jobapp/admin_question_delete.html', {'question': question})

# Admin CRUD Views for Results
@staff_member_required
def admin_results_view(request):
    results = Result.objects.all()
    context = {'results': results}
    return render(request, 'jobapp/admin_results.html', context)

@staff_member_required
def admin_result_create_view(request):
    if request.method == 'POST':
        form = AdminResultForm(request.POST)
        if form.is_valid():
            result = form.save()
            messages.success(request, f'Result for "{result.student.user.get_full_name()}" created successfully.')
            return redirect('jobapp:admin-results')
    else:
        form = AdminResultForm()
    return render(request, 'jobapp/admin_result_create.html', {'form': form})

@staff_member_required
def admin_result_edit_view(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        form = AdminResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save()
            messages.success(request, f'Result for "{result.student.user.get_full_name()}" updated successfully.')
            return redirect('jobapp:admin-results')
    else:
        form = AdminResultForm(instance=result)
    return render(request, 'jobapp/admin_result_edit.html', {'form': form, 'result': result})

@staff_member_required
def admin_result_delete_view(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, f'Result for "{result.student.user.get_full_name()}" deleted successfully.')
        return redirect('jobapp:admin-results')
    return render(request, 'jobapp/admin_result_delete.html', {'result': result})

# Admin CRUD Views for BookmarkJobs
@staff_member_required
def admin_bookmarks_view(request):
    bookmarks = BookmarkJob.objects.all()
    context = {'bookmarks': bookmarks}
    return render(request, 'jobapp/admin_bookmarks.html', context)

@staff_member_required
def admin_bookmark_create_view(request):
    if request.method == 'POST':
        form = AdminBookmarkForm(request.POST)
        if form.is_valid():
            bookmark = form.save()
            messages.success(request, f'Bookmark for "{bookmark.user.get_full_name()}" created successfully.')
            return redirect('jobapp:admin-bookmarks')
    else:
        form = AdminBookmarkForm()
    return render(request, 'jobapp/admin_bookmark_create.html', {'form': form})

@staff_member_required
def admin_bookmark_edit_view(request, pk):
    bookmark = get_object_or_404(BookmarkJob, pk=pk)
    if request.method == 'POST':
        form = AdminBookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            bookmark = form.save()
            messages.success(request, f'Bookmark for "{bookmark.user.get_full_name()}" updated successfully.')
            return redirect('jobapp:admin-bookmarks')
    else:
        form = AdminBookmarkForm(instance=bookmark)
    return render(request, 'jobapp/admin_bookmark_edit.html', {'form': form, 'bookmark': bookmark})

@staff_member_required
def admin_bookmark_delete_view(request, pk):
    bookmark = get_object_or_404(BookmarkJob, pk=pk)
    if request.method == 'POST':
        bookmark.delete()
        messages.success(request, f'Bookmark for "{bookmark.user.get_full_name()}" deleted successfully.')
        return redirect('jobapp:admin-bookmarks')
    return render(request, 'jobapp/admin_bookmark_delete.html', {'bookmark': bookmark})


def home_view(request):
    total_candidates = User.objects.filter(role='employee').count()
    total_jobs = Job.objects.filter(is_published=True).count()
    total_completed_jobs = Job.objects.filter(is_closed=True).count()
    total_companies = Job.objects.filter(is_published=True).values('company_name').distinct().count() or User.objects.filter(role='employer').count()
    
    published_jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    paginator = Paginator(published_jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        job_lists = []
        for job in page_obj:
            job_lists.append({
                'id': job.id,
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'job_type': job.job_type,
            })
        return JsonResponse({
            'job_lists': job_lists,
            'current_page_no': page_obj.number,
            'no_of_page': paginator.num_pages,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'prev_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        })

    context = {
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'total_completed_jobs': total_completed_jobs,
        'total_companies': total_companies,
        'page_obj': page_obj,
    }
    return render(request, 'jobapp/index.html', context)


def job_list_View(request):
    category_name = request.GET.get('category')
    if category_name:
        jobs = Job.objects.filter(category__name__icontains=category_name, is_published=True).order_by('-timestamp')
    else:
        jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category_name': category_name,
    }
    return render(request, 'jobapp/job_list.html', context)


def single_job_view(request, id):
    job = get_object_or_404(Job, id=id)
    context = {
        'job': job,
    }
    return render(request, 'jobapp/single_job.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def create_job_View(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            messages.success(request, 'Job created successfully!')
            return redirect('jobapp:single-job', id=job.id)
    else:
        form = JobForm()
    context = {
        'form': form,
    }
    return render(request, 'jobapp/create_job.html', context)


def about_us_view(request):
    total_candidates = User.objects.filter(role='employee').count()
    total_jobs = Job.objects.filter(is_published=True).count()
    total_companies = Job.objects.filter(is_published=True).values('company_name').distinct().count() or User.objects.filter(role='employer').count()
    context = {
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }
    return render(request, 'jobapp/about.html', context)

def contact_us_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')

        if first_name and last_name and email and subject and message_content:
            # Save to database
            contact = Contact.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=message_content
            )

            # Try to send email
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                full_name = f"{first_name} {last_name}"
                email_subject = f"Contact Form Submission: {subject}"
                email_message = f"New message from {full_name} ({email}):\n\n{message_content}"
                
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL], # Send to admin
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending contact email: {e}")

            messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
            return redirect('jobapp:contact')
        else:
            messages.error(request, "Please fill in all the required fields.")

    return render(request, 'jobapp/contact.html')

def search_result_view(request):

    query = request.GET.get('q')
    jobs = Job.objects.filter(title__icontains=query, is_published=True)
    context = {
        'jobs': jobs,
        'query': query,
    }
    return render(request, 'jobapp/search_results.html', context)

@staff_member_required
def admin_user_visits_view(request):
    visits = UserVisit.objects.all().order_by('-timestamp')
    paginator = Paginator(visits, 25)  # Show 25 visits per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'jobapp/admin_user_visits.html', context)

def company_about_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'About NayNat',
        'page_type': 'about'
    })

def career_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'Careers at NayNat',
        'page_type': 'career'
    })

def blog_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'Latest Insights & Updates',
        'page_type': 'blog'
    })

def resources_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'Resources & Tools',
        'page_type': 'resources'
    })

def privacy_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'Privacy Policy',
        'page_type': 'privacy'
    })

def terms_view(request):
    return render(request, 'jobapp/company_info.html', {
        'page_title': 'Terms of Service',
        'page_type': 'terms'
    })
