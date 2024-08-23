import os
import smtplib
from email.message import EmailMessage

PORT = 587  
EMAIL_SERVER = "smtp-mail.outlook.com"

sender_email = os.environ.get('email_username')
password_email = os.environ.get('email_password')

def send_email():
    msg = EmailMessage()
    msg["Subject"] = "test subject"
    msg["From"] = "saoneil@live.com"
    msg["To"] = "performance_taekwondo@hotmail.com"
    # msg["BCC"] = ""

    msg.set_content(f"""test body""")

    with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(from_addr=sender_email, to_addrs="performance_taekwondo@hotmail.com", msg=msg.as_string())

send_email()