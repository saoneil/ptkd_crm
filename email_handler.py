import email.message
import os
import time
import imaplib

host = os.environ.get('email_host_python')
username = os.environ.get('email_username')
password = os.environ.get('email_password')

def create_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, body=str):
    msg = email.message.Message()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = emails_to
    msg["Cc"] = emails_cc
    msg["Bcc"] = emails_bcc
    msg.set_payload(body)
    with imaplib.IMAP4_SSL(host) as c:
        c.login(user=username, password=password)
        c.append('DRAFTS', '',
                 imaplib.Time2Internaldate(time.time()),
                 str(msg).encode('utf-8'))
    
    return "Email Draft Generated"
def create_ptkd_receipt_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, file_tempate:str, receipt_data:list):
    msg = email.message.Message()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = emails_to
    msg["Cc"] = emails_cc
    msg["Bcc"] = emails_bcc

    body = ''
    ## template specific logic is below
    with open(file_tempate, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line = line + time.strftime("%Y/%m/%d")
            elif i == 5:
                line = line + emails_to
            elif i == 6:
                line = line + receipt_data[0]
            elif i == 8:
                line = line + receipt_data[1]
            elif i == 9:
                line = line + '$' + receipt_data[2] + "." + str(0) + str(0)
            elif i == 10:
                line = line + ("E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash")
            body = body + '\n' + line

    msg.set_payload(body)
    with imaplib.IMAP4_SSL(host) as c:
        c.login(user=username, password=password)
        c.append('DRAFTS', '',
                 imaplib.Time2Internaldate(time.time()),
                 str(msg).encode('utf-8'))

    print("Email Draft Generated")
def create_pkrt_receipt_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, file_tempate:str, receipt_data:list):
    msg = email.message.Message()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = emails_to
    msg["Cc"] = emails_cc
    msg["Bcc"] = emails_bcc

    body = ''
    ## template specific logic is below
    with open(file_tempate, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line = line + time.strftime("%Y/%m/%d")
            elif i == 5:
                line = line + emails_to
            elif i == 6:
                line = line + receipt_data[0]
            elif i == 8:
                line = line + receipt_data[1]
            elif i == 9:
                line = line + '$' + receipt_data[2] + "." + str(0) + str(0)
            elif i == 10:
                line = line + ("E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash")
            body = body + '\n' + line

    msg.set_payload(body)
    with imaplib.IMAP4_SSL(host) as c:
        c.login(user=username, password=password)
        c.append('DRAFTS', '',
                 imaplib.Time2Internaldate(time.time()),
                 str(msg).encode('utf-8'))

    print("Email Draft Generated")
