import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

def test_email():
    print(f"Testing email with USER: {settings.EMAIL_HOST_USER}")
    print(f"Using HOST: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    try:
        result = send_mail(
            'Test Email: SMTP Connection Verified',
            'Hello! This is a professional test email from your Job Portal System. Your SMTP settings are correctly configured.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER], # send to self
            fail_silently=False,
        )
        print(f"Success! Result: {result}")
    except Exception as e:
        print(f"FAILED to send email: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
