from tkinter import *
import pandas as pd
import imaplib
import time
import email.message
import mysql.connector
import os
import pyodbc
import datetime

host = os.environ.get('email_host_python')
username = os.environ.get('email_username')
password = os.environ.get('email_password')

def get_connection_connector():
    conn = mysql.connector.connect(
        host=os.environ.get('mysql_host'),
        user=os.environ.get('mysql_user'),
        password=os.environ.get('mysql_pass'),
        database="ptkd_students")
    return conn
def get_connection_pyodbc():
    cnxn = pyodbc.connect(
        DRIVER=os.environ.get('mysql_driver_python'),
        UID=os.environ.get('mysql_user'),
        Password=os.environ.get('mysql_pass'),
        Server=os.environ.get('mysql_host'),
        Database='ptkd_students',
        Port='3306')
    return cnxn
def get_previous_month_name():
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_month - datetime.timedelta(days=1)
    previous_month_name = last_day_of_previous_month.strftime("%B")
    return previous_month_name

previous_month = get_previous_month_name()
cnxn = get_connection_pyodbc()
cursor_cnxn = cnxn.cursor()

retval = pd.read_sql("""
                    select
                    email1 as "email_addresses"
                    from ptkd_students
                    where active = 1
                    and email1 is not null and email1 != "" and email1 != " "
                    and month(payment_good_till) = month(date_sub(now(), interval 2 month))
                    group by email1;
                    """, 
                    cnxn)
df_list = retval['email_addresses'].tolist()
email_list = "; ".join(df_list)

msg = email.message.Message()
msg.set_unixfrom('pymotw')
msg["Subject"] = f"Performance MA - Club Fees, {previous_month}"
msg["From"] = "saoneil@live.com"
msg["Bcc"] = email_list
#msg["Cc"] = "tkd.smacrury@gmail.com; yoosin1995@hotmail.com"
# finalstring = ''
# with open('C:\\Users\\saone\\Documents\\Python Stuff\\ptkd_crm\\email_all.txt', 'r') as f:
#     for line in f:
#         finalstring = finalstring + line

finalstring = f"""Hello,

I'm sending this message to students are currently outstanding for {previous_month} onward. If you could transfer these to me at your earliest convenience, that would be great.

Any questions, let me know.


Thanks,
________
Sean O'Neil
"""
msg.set_payload(finalstring)

with imaplib.IMAP4_SSL(host) as c:
    c.login(username, password)
    c.append('DRAFTS', '',
        imaplib.Time2Internaldate(time.time()),
        str(msg).encode('utf-8'))

cnxn.commit()
cursor_cnxn.close()