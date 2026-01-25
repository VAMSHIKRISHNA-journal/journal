import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def raw_email_check():
    host = "smtp.gmail.com"
    port = 587
    user = os.getenv('EMAIL_HOST_USER')
    password = os.getenv('EMAIL_HOST_PASSWORD')
    
    print(f"Connecting to {host}...")
    try:
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(1) # This will show the raw SMTP conversation
        server.starttls()
        print(f"Logging in as {user}...")
        server.login(user, password)
        
        subject = "FINAL TEST: Deep Diagnostic"
        body = "If this reaches you, the pipe is 100% clear."
        msg = f"Subject: {subject}\n\n{body}"
        
        print("Sending message...")
        server.sendmail(user, [user], msg)
        server.quit()
        print("\n--- Diagnostic Complete ---")
        print("Google ACCEPTED the email.")
        print("Please check: vamshikrishna8330@gmail.com")
        print("Check 'All Mail', 'Spam', and 'Promotions'.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    raw_email_check()
