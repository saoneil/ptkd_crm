from tkinter import *
import pandas as pd
import imaplib
import time
import email.message
import mysql.connector
import os
import pyodbc

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


cnxn = get_connection_pyodbc()
cursor_cnxn = cnxn.cursor()

retval = pd.read_sql("""
                    SELECT email1 as "email_addresses"
                    FROM ptkd_students 
                    where active = 1
                    and current_rank not like "%dan"
                    and (email1 is not null and email1 != " ")
                    union all
                    SELECT email2 as "email_addresses" 
                    FROM ptkd_students 
                    where active = 1
                    and current_rank not like "%dan"
                    and (email2 is not null and email2 != " ")
                    union all
                    SELECT email3 as "email_addresses" 
                    FROM ptkd_students 
                    where active = 1
                    and current_rank not like "%dan"
                    and (email3 is not null and email3 != " ")
                    ;
                    """, 
                    cnxn)
df_list = retval['email_addresses'].tolist()
email_list = "; ".join(df_list)

msg = email.message.Message()
msg.set_unixfrom('pymotw')
msg["Subject"] = "Performance MA - Color Belts"
msg["From"] = "saoneil@live.com"
msg["Bcc"] = email_list
msg["Cc"] = "tkd.smacrury@gmail.com; yoosin1995@hotmail.com"
finalstring = ''
with open('C:\\Users\\saone\\Documents\\Python Stuff\\ptkd_crm\\email_all.txt', 'r') as f:
    for line in f:

        finalstring = finalstring + line

msg.set_payload(finalstring)

with imaplib.IMAP4_SSL(host) as c:
    c.login(username, password)
    c.append('DRAFTS', '',
        imaplib.Time2Internaldate(time.time()),
        str(msg).encode('utf-8'))

cnxn.commit()
cursor_cnxn.close()