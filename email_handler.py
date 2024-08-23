import requests, json, os, time
import pandas as pd

# blog with info about azure
# https://medium.com/@manojkumardhakad/python-read-and-send-outlook-mail-using-oauth2-token-and-graph-api-53de606ecfa1
# https://stackoverflow.com/questions/73102294/aadsts9002331-application-is-configured-for-use-by-microsoft-account-users-only

url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
draft_url = "https://graph.microsoft.com/v1.0/me/messages"
payload = os.environ.get('azure_email_payload')
headers = {'Content-Type': 'application/x-www-form-urlencoded',}

response = requests.post(url, headers=headers, data=payload)
access_token = response.json().get("access_token")

if access_token:
    print("azure email authentication token acquired")
else:
    print("failed to acquire an authentication token")


def create_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, body=str):
    draft_payload = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body
        },
        "toRecipients": [{"emailAddress": {"address": email}} for email in emails_to],
        "ccRecipients": [{"emailAddress": {"address": email}} for email in emails_cc],
        "bccRecipients": [{"emailAddress": {"address": email}} for email in emails_bcc],
        # "replyTo": [{"emailAddress": {"address": email}} for email in email_from],
        # "flag": {"flagStatus": "flagged"},
        # "importance": "high",  # Options: "low", "normal", "high"
        # "inferenceClassification": "focused",  # Options: "focused", "other"
    }

    draft_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    draft_response = requests.post(draft_url, headers=draft_headers, data=json.dumps(draft_payload))

    if draft_response.status_code == 201:
        print(draft_response.status_code, "Draft email created successfully.")
    else:
        print(draft_response.status_code, "Failed to create draft email.")
def create_ptkd_receipt_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, file_tempate:str, receipt_data:list):
    body = ''
    with open(file_tempate, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line = line + time.strftime("%Y/%m/%d")
            elif i == 5:
                line = line + ", ".join(emails_to)
            elif i == 6:
                line = line + receipt_data[0]
            elif i == 8:
                line = line + receipt_data[1]
            elif i == 9:
                line = line + '$' + receipt_data[2] + "." + str(0) + str(0)
            elif i == 10:
                line = line + ("E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash")
            body = body + '\n' + line

    draft_payload = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body
        },
        "toRecipients": [{"emailAddress": {"address": email}} for email in emails_to],
        "ccRecipients": [{"emailAddress": {"address": email}} for email in emails_cc],
        "bccRecipients": [{"emailAddress": {"address": email}} for email in emails_bcc],
        # "replyTo": [{"emailAddress": {"address": email}} for email in email_from],
        # "flag": {"flagStatus": "flagged"},
        # "importance": "high",  # Options: "low", "normal", "high"
        # "inferenceClassification": "focused",  # Options: "focused", "other"
    }
    draft_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    draft_response = requests.post(draft_url, headers=draft_headers, data=json.dumps(draft_payload))

    if draft_response.status_code == 201:
        print(draft_response.status_code, "Draft email created successfully.")
    else:
        print(draft_response.status_code, "Failed to create draft email.")
def create_pkrt_receipt_email(subject:str, email_from:str, emails_to:list, emails_cc:list, emails_bcc:list, file_tempate:str, receipt_data:list):
    body = ''
    with open(file_tempate, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 4:
                line = line + time.strftime("%Y/%m/%d")
            elif i == 5:
                line = line + str(emails_to)
            elif i == 6:
                line = line + receipt_data[0]
            elif i == 8:
                line = line + receipt_data[1]
            elif i == 9:
                line = line + '$' + receipt_data[2] + "." + str(0) + str(0)
            elif i == 10:
                line = line + ("E-Transfer" if receipt_data[3] == 1 else "Cheque/Cash")
            body = body + '\n' + line
    
    draft_payload = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body
        },
        "toRecipients": [{"emailAddress": {"address": email}} for email in emails_to],
        "ccRecipients": [{"emailAddress": {"address": email}} for email in emails_cc],
        "bccRecipients": [{"emailAddress": {"address": email}} for email in emails_bcc],
        # "replyTo": [{"emailAddress": {"address": email}} for email in email_from],
        # "flag": {"flagStatus": "flagged"},
        # "importance": "high",  # Options: "low", "normal", "high"
        # "inferenceClassification": "focused",  # Options: "focused", "other"
    }
    draft_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    draft_response = requests.post(draft_url, headers=draft_headers, data=json.dumps(draft_payload))

    if draft_response.status_code == 201:
        print(draft_response.status_code, "Draft email created successfully.")
    else:
        print(draft_response.status_code, "Failed to create draft email.")





# create_ptkd_receipt_email(
#     subject = "Performance Taekwon-Do - Receipt",
#     email_from = ["saoneil@live.com"],
#     emails_to=["saoneil@live.com"],
#     emails_cc=["saoneil@live.com"], 
#     emails_bcc=["saoneil@live.com"],
#     file_tempate = "<path>\\receipt_template_ptkd.txt",
#     receipt_data = ["sean, sean", "aug 2024", "150", 1]
# )

# create_pkrt_receipt_email(
#     subject = "Performance Karate - Receipt",
#     email_from = ["saoneil@live.com"],
#     emails_to=["saoneil@live.com"],
#     emails_cc=["saoneil@live.com"], 
#     emails_bcc=["saoneil@live.com"],
#     file_tempate = "<path>\\receipt_template_pkrt.txt",
#     receipt_data = ["sean, sean", "aug 2024", "150", 1]
# )

# create_email(
#     subject="test subject", 
#     email_from = ["saoneil@live.com"],
#     emails_to=["saoneil@live.com"],
#     emails_cc=["saoneil@live.com"], 
#     emails_bcc=["saoneil@live.com"],
#     body="test body"
#     )

# data = {
#   "calories": [420, 380, 390],
#   "duration": [50, 40, 45]
# }
# #load data into a DataFrame object:
# df = pd.DataFrame(data)
# df_string = df.to_string(index=False)
# create_email(
#     subject="PMA Payroll",
#     email_from = ["saoneil@live.com"],
#     emails_to=["saoneil@live.com"],
#     emails_cc=["saoneil@live.com"], 
#     emails_bcc=["saoneil@live.com"],
#     body = df_string
#     )  