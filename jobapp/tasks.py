from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Job, Applicant, InterviewSelection
import os
import logging

logger = logging.getLogger(__name__)

def send_job_application_email_sync(applicant_id):
    """
    Synchronous email sending fallback when Celery/Redis is not available
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        job = applicant.job
        user = applicant.user

        logger.info(f"Sending sync emails for applicant {applicant_id}")

        # Email to job poster
        subject_poster = f'New Job Application: {job.title}'
        message_poster = f'''
Dear {job.user.get_full_name()},

You have received a new job application for "{job.title}".

Applicant Details:
- Name: {user.get_full_name()}
- Email: {user.email}
- Applied on: {applicant.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please find the attached resume for review.

Best regards,
Job Portal Team
'''

        # Email to applicant (confirmation)
        subject_applicant = f'Application Submitted: {job.title}'
        message_applicant = f'''
Dear {user.get_full_name()},

Your application for "{job.title}" at {job.company_name} has been successfully submitted.

Job Details:
- Company: {job.company_name}
- Location: {job.location}
- Applied on: {applicant.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

The employer will review your application and contact you if selected.

Best regards,
Job Portal Team
'''

        # 1. Send confirmation email to applicant
        send_mail(
            subject=subject_applicant,
            message=message_applicant,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # 2. Send email to job poster (with attachment if possible)
        email_poster = EmailMessage(
            subject=subject_poster,
            body=message_poster,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[job.user.email],
        )

        if applicant.resume and os.path.exists(applicant.resume.path):
            email_poster.attach_file(applicant.resume.path)
        
        email_poster.send()

        return f"Sync emails sent successfully for application {applicant_id}"

    except Exception as e:
        logger.error(f"Sync email sending failed: {str(e)}")
        return f"Failed to send sync email for application {applicant_id}: {str(e)}"


@shared_task
def send_job_application_email(applicant_id):
    """
    Celery task to send emails after job application
    Sends to both Job Poster (with resume) and Applicant (confirmation)
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        job = applicant.job
        user = applicant.user

        logger.info(f"Celery: Sending application emails for ID {applicant_id}")

        # 1. Email to Job Poster
        subject_poster = f'New Job Application: {job.title}'
        message_poster = f'''
Dear {job.user.get_full_name()},

You have received a new job application for "{job.title}".

Applicant Details:
- Name: {user.get_full_name()}
- Email: {user.email}
- Applied on: {applicant.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please find the attached resume for review.

Best regards,
Job Portal Team
'''
        email_poster = EmailMessage(
            subject=subject_poster,
            body=message_poster,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[job.user.email],
        )

        # Attach resume if it exists
        if applicant.resume and os.path.exists(applicant.resume.path):
            email_poster.attach_file(applicant.resume.path)

        email_poster.send()

        # 2. Confirmation Email to Applicant
        subject_applicant = f'Application Submitted: {job.title}'
        message_applicant = f'''
Dear {user.get_full_name()},

Your application for "{job.title}" at {job.company_name} has been successfully submitted.

Job Details:
- Company: {job.company_name}
- Location: {job.location}
- Applied on: {applicant.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

The employer will review your application and contact you if selected.

Best regards,
Job Portal Team
'''
        send_mail(
            subject=subject_applicant,
            message=message_applicant,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Celery emails sent successfully for application {applicant_id}"

    except Exception as e:
        logger.error(f"Celery application email failed: {str(e)}")
        return f"Failed to send Celery email for application {applicant_id}: {str(e)}"


@shared_task
def send_salary_offer_email(selection_id):
    """
    Send salary offer email to selected candidate
    """
    try:
        selection = InterviewSelection.objects.get(id=selection_id)
        applicant = selection.applicant
        job = applicant.job
        user = applicant.user

        logger.info(f"Celery: Sending salary offer to {user.email}")

        subject = f'Salary Offer: {job.title} at {job.company_name}'
        
        salary_val = f"${selection.salary_offer}" if selection.salary_offer else "To be discussed"
        
        message = f'''
Dear {user.get_full_name()},

Congratulations! You have been selected for the position of "{job.title}" at {job.company_name}.

Job Details:
- Company: {job.company_name}
- Location: {job.location}
- Salary Offer: {salary_val}

Please confirm your acceptance by contacting us at your earliest convenience.

Best regards,
{job.user.get_full_name()}
Job Portal Team
'''

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.send()

        # Mark email as sent
        selection.email_sent = True
        selection.save()

        return f"Salary offer email sent successfully to {user.email}"

    except Exception as e:
        logger.error(f"Salary offer email failed: {str(e)}")
        return f"Failed to send salary offer email for selection {selection_id}: {str(e)}"


@shared_task
def send_interview_invitation_email(session_id):
    """
    Send interview invitation email to both candidate and interviewer
    """
    try:
        from .models import InterviewSession
        session = InterviewSession.objects.get(id=session_id)
        selection = session.interview_selection
        applicant = selection.applicant
        job = applicant.job
        user = applicant.user
        interviewer = session.interviewer

        logger.info(f"Celery: Sending interview invitation to {user.email} and {interviewer.email}")

        # Prepare template context
        context = {
            'user_name': user.get_full_name(),
            'job_title': job.title,
            'company_name': job.company_name,
            'interviewer_name': interviewer.get_full_name(),
            'session_url': f"{settings.SITE_DOMAIN}/interview-session/{session.session_id}/"
        }

        # Render HTML and generate plain text fallback
        html_content = render_to_string('emails/interview_invitation.html', context)
        text_content = strip_tags(html_content)

        # Create and send email to Candidate
        subject = f'Interview Invitation: {job.title} at {job.company_name}'
        email_candidate = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email_candidate.attach_alternative(html_content, "text/html")
        email_candidate.send()

        # Create and send email to Interviewer
        subject_interviewer = f'Interview Scheduled: {user.get_full_name()} for {job.title}'
        message_interviewer = f'''
Dear {interviewer.get_full_name()},

You have scheduled an interview with {user.get_full_name()} for the position of "{job.title}".

Interview Details:
- Candidate: {user.get_full_name()}
- Job: {job.title}
- Session URL: {settings.SITE_DOMAIN}/interview-session/{session.session_id}/

Please be ready at the scheduled time.

Best regards,
Job Portal Team
'''
        send_mail(
            subject=subject_interviewer,
            message=message_interviewer,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[interviewer.email],
            fail_silently=False,
        )

        return f"Interview invitation emails sent successfully"

    except Exception as e:
        logger.error(f"Interview invitation email failed: {str(e)}")
        return f"Failed to send interview invitation email: {str(e)}"


@shared_task
def send_interview_completion_email(session_id):
    """
    Send interview completion email to candidate with feedback and salary offer
    """
    try:
        from .models import InterviewSession
        session = InterviewSession.objects.get(id=session_id)
        selection = session.interview_selection
        applicant = selection.applicant
        job = applicant.job
        user = applicant.user

        logger.info(f"Celery: Sending interview completion to {user.email}")

        subject = f'Interview Results: {job.title} at {job.company_name}'
        
        # Format salary displays
        final_salary_display = f"${session.final_salary}" if session.final_salary else "To be discussed"
        
        # Prepare template context
        context = {
            'user_name': user.get_full_name(),
            'job_title': job.title,
            'company_name': job.company_name,
            'interviewer_name': session.interviewer.get_full_name(),
            'completed_date': session.completed_at.strftime('%Y-%m-%d %H:%M:%S') if session.completed_at else 'Recently',
            'feedback': session.feedback,
            'final_salary': final_salary_display
        }

        # Render HTML and generate plain text fallback
        html_content = render_to_string('emails/interview_completion.html', context)
        text_content = strip_tags(html_content)

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return f"Interview completion email sent successfully to {user.email}"

    except Exception as e:
        logger.error(f"Interview completion email failed: {str(e)}")
        return f"Failed to send interview completion email: {str(e)}"
