import os
import django
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_email():
    print("--- Starting Email Diagnostic ---")
    print(f"Using Host: {settings.EMAIL_HOST}")
    print(f"Using User: {settings.EMAIL_HOST_USER}")
    
    recipient = settings.EMAIL_HOST_USER 
    
    try:
        print(f"Attempting to send a test signal to {recipient}...")
        send_mail(
            subject="System Diagnostic: Email Test",
            message="If you see this, your Journal Email Engine is working perfectly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False, 
        )
        print("SUCCESS! The email was accepted by Google's servers.")
        print("Check your SPAM folder if it doesn't appear in Inbox.")
    except Exception as e:
        print("FAILED! Error detected:")
        print(str(e))
        print("\nCHECKLIST:")
        print("1. Is EMAIL_HOST_USER your real Gmail in .env?")
        print("2. Is the App Password correct in .env?")

if __name__ == "__main__":
    test_email()
