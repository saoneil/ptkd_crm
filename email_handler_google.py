import os, time, base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

# Load or generate token
def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                print("Token refresh failed. Removing token.json and retrying...")
                os.remove('token.json')
                return get_gmail_service()
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# Gmail API client
service = get_gmail_service()

def create_email(subject: str, email_from: str, emails_to: list, emails_cc: list, emails_bcc: list, body: str):
    message = MIMEText(body)
    # Filter out None values and empty lists
    emails_to = [email for email in emails_to if email] if emails_to else []
    emails_cc = [email for email in emails_cc if email] if emails_cc else []
    emails_bcc = [email for email in emails_bcc if email] if emails_bcc else []
    
    message['to'] = ', '.join(emails_to) if emails_to else ''
    message['cc'] = ', '.join(emails_cc) if emails_cc else ''
    message['bcc'] = ', '.join(emails_bcc) if emails_bcc else ''
    message['from'] = email_from
    message['subject'] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {'message': {'raw': encoded_message}}

    try:
        service.users().drafts().create(userId='me', body=draft_body).execute()
        print("Draft email created successfully.")
    except Exception as e:
        print("Failed to create draft email.")
        print(e)

def create_html_email(subject: str, email_from: str, emails_to: list, emails_cc: list, emails_bcc: list, body: str):
    """Create HTML email for draft messages (Draft to All, Draft to Karate, Draft to Wait-list)"""
    message = MIMEText(body, 'html')
    # Filter out None values and empty lists
    emails_to = [email for email in emails_to if email] if emails_to else []
    emails_cc = [email for email in emails_cc if email] if emails_cc else []
    emails_bcc = [email for email in emails_bcc if email] if emails_bcc else []
    
    message['to'] = ', '.join(emails_to) if emails_to else ''
    message['cc'] = ', '.join(emails_cc) if emails_cc else ''
    message['bcc'] = ', '.join(emails_bcc) if emails_bcc else ''
    message['from'] = email_from
    message['subject'] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {'message': {'raw': encoded_message}}

    try:
        service.users().drafts().create(userId='me', body=draft_body).execute()
        print("HTML draft email created successfully.")
    except Exception as e:
        print("Failed to create HTML draft email.")
        print(e)

def create_ptkd_receipt_email(subject: str, email_from: str, emails_to: list, emails_cc: list, emails_bcc: list, file_template: str, receipt_data: list):
    body = ''
    with open(file_template, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line += time.strftime("%Y/%m/%d")
            elif i == 5:
                line += ", ".join(emails_to)
            elif i == 6:
                line += receipt_data[0]
            elif i == 8:
                line += receipt_data[1]
            elif i == 9:
                line += '$' + receipt_data[2] + ".00"
            elif i == 10:
                line += "E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash"
            body += '\n' + line
    # create_email(subject, email_from, emails_to, emails_cc, emails_bcc, body)
    create_email(subject, email_from, emails_to, emails_cc, None, body)

def create_pkrt_receipt_email(subject: str, email_from: str, emails_to: list, emails_cc: list, emails_bcc: list, file_template: str, receipt_data: list):
    body = ''
    with open(file_template, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line += time.strftime("%Y/%m/%d")
            elif i == 5:
                line += ", ".join(emails_to)
            elif i == 6:
                line += receipt_data[0]
            elif i == 8:
                line += receipt_data[1]
            elif i == 9:
                line += '$' + receipt_data[2] + ".00"
            elif i == 10:
                line += "E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash"
            body += '\n' + line
    # create_email(subject, email_from, emails_to, emails_cc, emails_bcc, body)
    create_email(subject, email_from, emails_to, emails_cc, None, body)
