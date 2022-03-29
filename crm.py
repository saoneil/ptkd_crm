from tkinter import *
import tkinter as tk
from tkinter import ttk
import pyodbc
import pandas as pd
from datetime import datetime
import mysql.connector
import imaplib
import time
import email.message
from mail_reader import mail_reader_func
import os


window_width = 1000
window_height = 750

treeplacex = 220
treeplacey = 5

def get_connection_connector():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="BootsAlmighty",
        database="ptkd_students")
    return conn

# def get_connection_pyodbc():
#     cnxn = pyodbc.connect(
#         'DRIVER={MySQL ODBC 8.0 ANSI Driver};'
#         'UID=root;Password=BootsAlmighty;'
#         'Server=localhost;Database=ptkd_students;'
#         'Port=3306;String Types=Unicode')
#     return cnxn

def get_connection_pyodbc():
    cnxn = pyodbc.connect(
        DRIVER=os.environ.get('mysql_driver_python'),
        UID=os.environ.get('mysql_user'),
        Password=os.environ.get('mysql_pass'),
        Server=os.environ.get('mysql_host'),
        Database='ptkd_students',
        Port='3306')
    return cnxn

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        nb = ttk.Notebook(root, width=window_width, height=window_height)
        nb.grid(row=0, column=0)
        tab1 = ttk.Frame(nb)
        nb.add(tab1, text='PTKD Students')
        tab2 = ttk.Frame(nb)
        nb.add(tab2, text='PTKD Financial Reporting')
        tab3 = ttk.Frame(nb)
        nb.add(tab3, text='Team NS')
        
        
        ############      #        #######          ###
             #           # #       #      #           #
             #          #   #      #      #           # 
             #         #######     #   ###            #
             #        #       #    #      #           #
             #       #         #   #  #####         #####
             
        row_label = tk.StringVar()
        time_label = tk.StringVar()
        row_label.set("# of records: " + str(0))
        time_label.set("refresh time: " + str(datetime.now().strftime("%H:%M:%S")))
        rl = ttk.Label(tab1, textvariable=row_label).place(x=910, y=430)
        tl = ttk.Label(tab1, textvariable=time_label).place(x=880, y=448)
        dblabel = tk.Label(tab1, text="db status")
        dblabel.place(x=135, y=215)
        self.dblabel_counter = 1
        self.mailsearch_counter = 1
        
        #################
        ### Functions ###
        #################
        def update_numrecords_time(rows,time):
            row_label.set("# of records: " + str(rows))
            time_label.set("refresh time: " + str(time))
        def refresh_status_saved():
            dblabel.configure(text="db saved ["+ str(self.dblabel_counter) +"]")
            self.dblabel_counter += 1
        def refresh_search_saved():
            mailsearch_label.configure(text="search counter [" + str(self.mailsearch_counter) + "]")
            self.mailsearch_counter += 1
        def save_ptkd_students_db():
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()
            sql_query = "SELECT * FROM ptkd_students.ptkd_students;"
            retval = pd.read_sql(sql_query, cnxn)
            retval.to_csv(r'C:\Users\saone\Documents\Python Stuff\prod\crm_files\db_backup.csv')
            dblabel.after(1000, refresh_status_saved())           
        def view_all_active_students():
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()
            sql_query = "call ptkd_all_active_students();"
            retval = pd.read_sql(sql_query, cnxn)
            retval_rows = retval.to_numpy().tolist()
            
            columns = ('student_id', 'first_name', 'last_name', 'payment_good_till' 'dob', 'current_rank', 'active', 'email1', 'trial_student', 'comment')
            tree = ttk.Treeview(tab1, columns=columns, show='headings', height = 20)

            tree["column"] = list(retval.columns)
            tree["show"] =  "headings"

            for column in list(retval.columns):
                tree.heading(column, text=column)
                tree.column(column, width=38, minwidth=70)
            
            tree.heading('student_id', text="ID")
            tree.column('student_id', width=30, minwidth=30)
            tree.heading('first_name', text="first_name")
            tree.column('first_name', width=110, minwidth=113)
            tree.heading('last_name', text="last_name")
            tree.column('last_name', width=110, minwidth=113)
            tree.heading('payment_good_till', text="payment_good_till")
            tree.column('payment_good_till', width=120, minwidth=120)
            tree.heading('dob', text="DOB")
            tree.column('dob', width=100, minwidth=100)
            tree.heading('current_rank', text="rank")
            tree.column('current_rank', width=80, minwidth=80)
            tree.heading('active', text="active")
            tree.column('active', width=40, minwidth=40)
            tree.heading('email1', text="email1")
            tree.column('email1', width=215, minwidth=215)
            tree.heading('trial_student', text="trial_student")
            tree.column('trial_student', width=50, minwidth=75)
            tree.heading('comment', text="comment")
            tree.column('comment', width=50, minwidth=500)
            
            for row in retval_rows:
                tree.insert("", "end", values=row)

            tree.place(x=treeplacex, y=treeplacey)
            vert_scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
            horz_scrollbar = ttk.Scrollbar(tab1, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=horz_scrollbar.set)
            vert_scrollbar.place(x=985, y=5, height=418)
            horz_scrollbar.place(x=220, y=427, width=500)
            update_numrecords_time(len(retval_rows), datetime.now().strftime("%H:%M:%S"))
            cursor.close()
            cnxn.close()
        def view_all_trial_students():
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()
            sql_query = "call ptkd_all_trial_students();"
            retval = pd.read_sql(sql_query, cnxn)
            retval_rows = retval.to_numpy().tolist()
            
            columns = ('student_id', 'first_name', 'last_name', 'active', 'email1', 'trial_student')
            tree = ttk.Treeview(tab1, columns=columns, show='headings', height = 20)

            tree["column"] = list(retval.columns)
            tree["show"] =  "headings"
            
            tree.heading('student_id', text="ID")
            tree.column('student_id', width=40, minwidth=40)
            tree.heading('first_name', text="first_name")
            tree.column('first_name', width=110, minwidth=110)
            tree.heading('last_name', text="last_name")
            tree.column('last_name', width=110, minwidth=110)
            tree.heading('active', text="active")
            tree.column('active', width=40, minwidth=40)
            tree.heading('email1', text="email1")
            tree.column('email1', width=175, minwidth=175)
            tree.heading('trial_student', text="trial")
            tree.column('trial_student', width=40, minwidth=40)
            tree.heading('comment', text="comment")
            tree.column('comment', width=250, minwidth=400)
            
            for row in retval_rows:
                tree.insert("", "end", values=row)

            tree.place(x=treeplacex, y=treeplacey)
            vert_scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
            horz_scrollbar = ttk.Scrollbar(tab1, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=horz_scrollbar.set)
            vert_scrollbar.place(x=985, y=5, height=418)
            horz_scrollbar.place(x=220, y=427, width=500)
            update_numrecords_time(len(retval_rows), datetime.now().strftime("%H:%M:%S"))
            cursor.close()
            cnxn.close()
        def view_testing_list():
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()
            sql_query = "call ptkd_testing_list();"
            retval = pd.read_sql(sql_query, cnxn)
            retval_rows = retval.to_numpy().tolist()
            
            columns = ('student_id', 'first_name', 'last_name', 'current_rank', 'gup_dan', 
                       'yellow_stripe_testdate', 'yellow_belt_testdate', 'green_stripe_testdate', 'green_belt_testdate', 'blue_stripe_testdate', 'blue_belt_testdate',
                       'red_stripe_testdate', 'red_belt_testdate', 'black_stripe_testdate', '1st_dan_testdate')
            tree = ttk.Treeview(tab1, columns=columns, show='headings', height = 20)

            tree["column"] = list(retval.columns)
            tree["show"] =  "headings"
            
            for column in list(retval.columns):
                tree.heading(column, text=column)
                tree.column(column, width=38, minwidth=75)
            
            tree.heading('yellow_stripe_testdate', text="YS")
            tree.heading('yellow_belt_testdate', text="YB")
            tree.heading('green_stripe_testdate', text="GS")
            tree.heading('green_belt_testdate', text="GB")
            tree.heading('blue_stripe_testdate', text="BS")
            tree.heading('blue_belt_testdate', text="BB")
            tree.heading('red_stripe_testdate', text="RS")
            tree.heading('red_belt_testdate', text="RB")
            tree.heading('black_stripe_testdate', text="BKS")
            tree.heading('1st_dan_testdate', text="1st")
            
            tree.heading('student_id', text="ID")
            tree.column('student_id', width=30, minwidth = 30)
            tree.heading('first_name', text="first_name")
            tree.column('first_name', width=110, minwidth = 113)
            tree.heading('last_name', text="last_name")
            tree.column('last_name', width=110, minwidth = 113)
            tree.heading('current_rank', text="rank")
            tree.column('current_rank', width=80, minwidth = 80)
            tree.heading('gup_dan', text="gup/dan")
            tree.column('gup_dan', width=60, minwidth = 60)
            
            for row in retval_rows:
                tree.insert("", "end", values=row)

            tree.place(x=treeplacex, y=treeplacey)
            vert_scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
            horz_scrollbar = ttk.Scrollbar(tab1, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=horz_scrollbar.set)
            vert_scrollbar.place(x=985, y=5, height=418)
            horz_scrollbar.place(x=220, y=427, width=500)
            update_numrecords_time(len(retval_rows), datetime.now().strftime("%H:%M:%S"))
            cursor.close()
            cnxn.close()
        def payments_in_arrears():
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()
            sql_query = "call ptkd_payments_in_arrears();"
            retval = pd.read_sql(sql_query, cnxn)
            retval_rows = retval.to_numpy().tolist()
            
            columns = ('student_id', 'first_name', 'last_name', 'email1', 'email2', 'payment_good_till', 'pay_rate', 'comment')
            tree = ttk.Treeview(tab1, columns=columns, show='headings', height = 20)

            tree["column"] = list(retval.columns)
            tree["show"] =  "headings"
            
            tree.heading('student_id', text="ID")
            tree.column('student_id', width=30, minwidth = 30)
            tree.heading('first_name', text="first_name")
            tree.column('first_name', width=110, minwidth = 110)
            tree.heading('last_name', text="last_name")
            tree.column('last_name', width=110, minwidth = 110)
            tree.heading('email1', text="email1")
            tree.column('email1', width=150, minwidth = 200)
            tree.heading('email2', text="email2")
            tree.column('email2', width=60, minwidth = 150)
            tree.heading('payment_good_till', text="pymtgoodtill")
            tree.column('payment_good_till', width=75, minwidth = 75)
            tree.heading('pay_rate', text="payrate")
            tree.column('pay_rate', width=50, minwidth = 50)
            tree.heading('comment', text="comment")
            tree.column('comment', width=180, minwidth = 400)
            
            for row in retval_rows:
                tree.insert("", "end", values=row)

            tree.place(x=treeplacex, y=treeplacey)
            vert_scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
            horz_scrollbar = ttk.Scrollbar(tab1, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=horz_scrollbar.set)
            vert_scrollbar.place(x=985, y=5, height=418)
            horz_scrollbar.place(x=220, y=427, width=500)
            update_numrecords_time(len(retval_rows), datetime.now().strftime("%H:%M:%S"))
            cursor.close()
            cnxn.close()
        def add_student_to_db():
            first_name = section2_entry1.get()
            last_name = section2_entry2.get()
            email = section2_entry3.get()
            phone = section2_entry4.get()
            dob = section2_entry5.get()
            params = (first_name, last_name, email, phone, dob)
            sqlstring = "ptkd_add_new_student"    
            conn = get_connection_connector()
            cursor = conn.cursor()
            cursor.callproc(sqlstring, params)
            conn.commit()
            cursor.close()
            section2_entry1.delete(0, END)
            section2_entry2.delete(0, END)
            section2_entry3.delete(0, END)
            section2_entry4.delete(0, END)
            section2_entry5.delete(0, END)
        def add_payment_to_db():
            id1 = section3_entry1.get()
            id2 = section3_entry2.get()
            id3 = section3_entry3.get()
            id4 = section3_entry4.get()
            goodtill = section3_entry5.get()
            total = section3_entry7.get()
            payrate = section3_entry6.get()
            daterange = section3_entry8.get()
            id_list = [id1, id2, id3, id4]   
            conn = get_connection_connector()
            cursor_conn = conn.cursor()
            cnxn = get_connection_pyodbc()
            cursor_cnxn = cnxn.cursor()
            imap_names = []
            imap_emails = []
            for i in range(id_list.index('')):
                sqlstring_db = "ptkd_add_payment"
                params_db = (id_list[i], goodtill, payrate)
                cursor_conn.callproc(sqlstring_db, params_db)

                s_id = id_list[i]
                name_sql = "SELECT first_name FROM ptkd_students WHERE student_id ="+str(id_list[i])
                email_sql = "SELECT email1 FROM ptkd_students WHERE student_id ="+str(id_list[i])
                retval_names = pd.read_sql(name_sql, cnxn)
                retval_emails = pd.read_sql(email_sql, cnxn)
                imap_names.append(retval_names["first_name"][0])
                imap_emails.append(retval_emails["email1"][0])
                imap_emails = list(dict.fromkeys(imap_emails))
                names_final = ", ".join(imap_names)
                emails_final = "; ".join(imap_emails)
            msg = email.message.Message()
            msg.set_unixfrom('pymotw')
            msg["Subject"] = "Performance Taekwon-Do - Receipt"
            msg["From"] = "saoneil@live.com"
            msg["To"] = emails_final
            msg["Bcc"] = "performance_taekwondo@hotmail.com"
            finalstring = ''
            with open('C:\\Users\\saone\\Documents\\Python Stuff\\prod\\crm\\receipt.txt', 'r') as f:
                for i, line in enumerate(f):
                    line = line.rstrip('\n')
                    if i == 4:
                        line = line + time.strftime("%Y/%m/%d")
                    elif i == 5:
                        line = line + emails_final
                    elif i == 6:
                        line = line + names_final
                    elif i == 8:
                        line = line + daterange
                    elif i == 9:
                        line = line + '$' + total + '.' + str(0) + str(0)
                    finalstring = finalstring + '\n' + line
                #print(finalstring)
            msg.set_payload(finalstring)
            with imaplib.IMAP4_SSL(host) as c:
                c.login(username, password)
                c.append('DRAFTS', '',
                    imaplib.Time2Internaldate(time.time()),
                    str(msg).encode('utf-8'))

            section3_entry1.delete(0, END)
            section3_entry2.delete(0, END)
            section3_entry3.delete(0, END)
            section3_entry4.delete(0, END)
            section3_entry5.delete(0, END)
            section3_entry6.delete(0, END)
            section3_entry7.delete(0, END)
            section3_entry8.delete(0, END)

            conn.commit()
            cnxn.commit()
            cursor_conn.close()
            cursor_cnxn.close()
        def search_grid():
            first_name_search = section1_entry1.get()
            last_name_search = section1_entry2.get()
            cnxn = get_connection_pyodbc()
            cursor = cnxn.cursor()

            sql_nums = "SELECT count(*) as total FROM ptkd_students WHERE active=1;"
            sql_query = "call ptkd_all_active_students();"

            retval = pd.read_sql(sql_query, cnxn)
            retval_rows = retval.to_numpy().tolist()

            retval["first_name"] = retval["first_name"].str.lower()
            retval["last_name"] = retval["last_name"].str.lower()
            searched_fname_df = retval[retval["first_name"].str.contains(first_name_search)]
            searched_lname_df = retval[retval["last_name"].str.contains(last_name_search)]
            def return_df():
                if len(searched_fname_df.index) != len(retval.index) and len(searched_lname_df.index) != len(retval.index):
                    return pd.concat([searched_fname_df, searched_lname_df], ignore_index=True)
                elif len(searched_fname_df.index) != len(retval.index) and len(searched_lname_df.index) == len(retval.index):
                    return searched_fname_df
                elif len(searched_fname_df.index) == len(retval.index) and len(searched_lname_df.index) != len(retval.index):
                    return searched_lname_df
                else:
                    return retval

            return_df = return_df()
            return_df_rows = return_df.to_numpy().tolist()
            
            columns = ('student_id', 'first_name', 'last_name', 'payment_good_till', 'dob', 'current_rank', 'active', 'email1', 'trial_student')
            tree = ttk.Treeview(tab1, columns=columns, show='headings', height = 20)

            tree["column"] = list(return_df.columns)
            tree["show"] =  "headings"
            
            tree.heading('student_id', text="ID")
            tree.column('student_id', width=40)
            tree.heading('first_name', text="first_name")
            tree.column('first_name', width=110)
            tree.heading('last_name', text="last_name")
            tree.column('last_name', width=110)
            tree.heading('payment_good_till', text="payment_good_till")
            tree.column('payment_good_till', width=110)
            tree.heading('dob', text="DOB")
            tree.column('dob', width=100)
            tree.heading('current_rank', text="rank")
            tree.column('current_rank', width=80)
            tree.heading('active', text="active")
            tree.column('active', width=40)
            tree.heading('email1', text="email1")
            tree.column('email1', width=215)
            tree.heading('trial_student', text="trial_student")
            tree.column('trial_student', width=70)
            
            for row in return_df_rows:
                tree.insert("", "end", values=row)

            tree.place(x=220, y=5)
            scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.place(x=985, y=5, height=418)
            update_numrecords_time(len(return_df_rows), datetime.now().strftime("%H:%M:%S"))

            cursor.close()
            cnxn.close()
        def make_active_inactive():
            studentid_1 = section4_entry1.get()
            studentid_2 = section4_entry2.get()
            studentid_3 = section4_entry3.get()
            studentid_4 = section4_entry4.get()
            id_list = [studentid_1, studentid_2, studentid_3, studentid_4]
            conn = get_connection_connector()
            cursor = conn.cursor()
            for i in range(id_list.index('')):
                sqlstring = "ptkd_make_student_active_inactive"
                params_seq = (id_list[i],)
                cursor.callproc(sqlstring, params_seq)
            conn.commit()
            cursor.close()
            section4_entry1.delete(0, END)
            section4_entry2.delete(0, END)
            section4_entry3.delete(0, END)
            section4_entry4.delete(0, END)


        #################
        ### SECTION 1 ###
        #################
        section1_label1 = ttk.Label(tab1, text="Buttons For Viewing \n Student Database").grid(row = 1, column=1, sticky=W, pady=(30, 15), padx=30)
        section1_button1 = ttk.Button(tab1, text="View All Active Students", command = view_all_active_students)
        section1_button2 = ttk.Button(tab1, text="View All Trial Students", command = view_all_trial_students)
        section1_button3 = ttk.Button(tab1, text="View Testing Dates", command = view_testing_list)
        section1_button4 = ttk.Button(tab1, text="View Payments In Arrears", command = payments_in_arrears)
        section1_button5 = tk.Button(tab1, text="Backup Database", command = save_ptkd_students_db)
        section1_button6 = ttk.Button(tab1, text="Search Grid", command = search_grid)
        section1_entry1 = tk.Entry(tab1, width=15)
        section1_entry2 = tk.Entry(tab1, width=15)
        section2_label2 = ttk.Label(tab1, text=" First Name: ").grid(row=8, column=1, sticky=W, pady=(0,5), padx=(15,5))
        section2_label3 = ttk.Label(tab1, text=" Last Name: ").grid(row=9, column=1, sticky=W, pady=(0,5), padx=(15,5))

        section1_button1.grid(row=2, column=1, sticky = W, pady=(0,7), padx=(30,0))
        section1_button2.grid(row=3, column=1, sticky = W, pady=(0,7), padx=(30,0))
        section1_button3.grid(row=4, column=1, sticky = W, pady=(0,7), padx=(30,0))
        section1_button4.grid(row=5, column=1, sticky = W, pady=(0,7), padx=(30,0))
        section1_button5.grid(row=6, column=1, sticky = W, pady=(0,35), padx=(30,0))
        section1_button6.grid(row=7, column=1, sticky = W, pady=(0,7), padx=(30,0))
        section1_entry1.grid(row=8, column=1, sticky=W, pady=(0,7), padx=(90,0))
        section1_entry2.grid(row=9, column=1, sticky=W, pady=(0,7), padx=(90,0))

        #################
        ### SECTION 2 ###
        #################
        section2_button1 = ttk.Button(tab1, text="Add Student To Database", command = add_student_to_db)
        section2_label1 = ttk.Label(tab1, text=" First Name: ").grid(row=11, column=1, sticky=W, pady=(0,5), padx=(15,5))
        section2_label2 = ttk.Label(tab1, text=" Last Name: ").grid(row=12, column=1, sticky=W, pady=(0,5), padx=(15,5))
        section3_label3 = ttk.Label(tab1, text="          Email: ").grid(row=13, column=1, sticky=W, pady=(0,5), padx=(15,5))
        section4_label4 = ttk.Label(tab1, text="         Phone: ").grid(row=14, column=1, sticky=W, pady=(0,5), padx=(15,5))
        section2_label5 = ttk.Label(tab1, text="            DOB: ").grid(row=15, column=1, sticky=W, pady=(0,5), padx=(15,5))
        
        section2_button1.grid(row=10, column=1, sticky=W, pady=(150, 15), padx=(40,50))
        section2_entry1 = tk.Entry(tab1, width=20)
        section2_entry1.grid(row=11, column=1, sticky=W, padx=(80,5))
        section2_entry2 = tk.Entry(tab1, width=20)
        section2_entry2.grid(row=12, column=1, sticky=W, padx=(80,5))
        section2_entry3 = tk.Entry(tab1, width=20)
        section2_entry3.grid(row=13, column=1, sticky=W, padx=(80,5))
        section2_entry4 = tk.Entry(tab1, width=20)
        section2_entry4.grid(row=14, column=1, sticky=W, padx=(80,5))
        section2_entry5 = tk.Entry(tab1, width=20)
        section2_entry5.grid(row=15, column=1, sticky=W, padx=(80,5))
        
        #################
        ### SECTION 3 ###
        #################
        section3_button1 = ttk.Button(tab1, text="Add Payment to Database", command = add_payment_to_db)
        section3_label1 = ttk.Label(tab1, text="Student ID:").grid(row=11, column=2, sticky=W, pady=(0,5), padx=(15,5))
        section3_label2 = ttk.Label(tab1, text="   Good Till:").grid(row=15, column=2, sticky=W, pady=(0,5), padx=(15,5))
        section3_label3 = ttk.Label(tab1, text="    Pay Rate:").grid(row=16, column=2, sticky=W, pady=(0,5), padx=(15,5))
        section3_label4 = ttk.Label(tab1, text="          Total:").grid(row=17, column=2, sticky=W, pady=(0,5), padx=(15,5))
        section3_label5 = ttk.Label(tab1, text="Date Range:").grid(row=18, column=2, sticky=W, pady=(0,5), padx=(15,5))

        section3_button1.grid(row=10, column=2, sticky=E, pady=(150,15), padx=(50,50))
        section3_entry1 = ttk.Entry(tab1, width=8)
        section3_entry1.grid(row=11, column=2, sticky=W, padx=(80,50))
        section3_entry2 = ttk.Entry(tab1, width=8)
        section3_entry2.grid(row=12, column=2, sticky=W, padx=(80,50))
        section3_entry3 = ttk.Entry(tab1, width=8)
        section3_entry3.grid(row=13, column=2, sticky=W, padx=(80,50))
        section3_entry4 = ttk.Entry(tab1, width=8)
        section3_entry4.grid(row=14, column=2, sticky=W, padx=(80,50))
        section3_entry5 = ttk.Entry(tab1, width=15)
        section3_entry5.grid(row=15, column=2, sticky=W, padx=(80,50))
        section3_entry6 = ttk.Entry(tab1, width=15)
        section3_entry6.grid(row=16, column=2, sticky=W, padx=(80,50))
        section3_entry7 = ttk.Entry(tab1, width=15)
        section3_entry7.grid(row=17, column=2, sticky=W, padx=(80,50))
        section3_entry8 = ttk.Entry(tab1, width=15)
        section3_entry8.grid(row=18, column=2, sticky=W, padx=(80,50))

        #################
        ### SECTION 4 ###
        #################
        section4_button1 = ttk.Button(tab1, text="Make Student(s) Active/Inactive", command = make_active_inactive)
        section4_label1 = ttk.Label(tab1, text="Student ID:").grid(row=11, column=3, sticky=W, pady=(0,5), padx=(15,5))

        section4_button1.grid(row=10, column=3, sticky=E, pady=(150,15), padx=(50,50))
        section4_entry1 = ttk.Entry(tab1, width=8)
        section4_entry1.grid(row=11, column=3, sticky=W, padx=(80,50))
        section4_entry2 = ttk.Entry(tab1, width=8)
        section4_entry2.grid(row=12, column=3, sticky=W, padx=(80,50))
        section4_entry3 = ttk.Entry(tab1, width=8)
        section4_entry3.grid(row=13, column=3, sticky=W, padx=(80,50))
        section4_entry4 = ttk.Entry(tab1, width=8)
        section4_entry4.grid(row=14, column=3, sticky=W, padx=(80,50))
    







        ############      #        #######         ######
             #           # #       #      #       #      #
             #          #   #      #      #            # 
             #         # ### #     #  ####         # 
             #        #       #    #      #       #      
             #       #         #   #  #####       #######
        


        #################
        ### SECTION 1 ###
        #################
        quotes = "\""
        def get_report():
            mail_reader_string_start = str(period_entry_start.get())
            mail_reader_string_end = str(period_entry_end.get())
            datestring = ''
            if mail_reader_string_end == '':
                datestring_mail = 'ALL SINCE "' + mail_reader_string_start + '"'
                return_string = mail_reader_func(datestring_mail, '')
                result_string.set(return_string)
                #print(return_string)


            period_entry_start.delete(0, END)
            period_entry_start.insert(0, '1-Jan-2022')
            period_entry_end.delete(0, END)

            refresh_search_saved()


        desc_label = ttk.Label(tab2, text = "Type a time period below and click \"Get Report\" for a summary \nof the received tuition fees, gear expenditure and credits/other.")
        desc_label.grid(row=1, column=1, padx=(15,45), pady=(30,10))

        prompt_label_start = ttk.Label(tab2, text= "Enter the time period (e.g. 1-Jan-2022)  ||  Start: ")
        prompt_label_start.grid(row=2, column=1, padx=(15,15), pady=(10,10), sticky='W')

        prompt_label_end = ttk.Label(tab2, text= "End: ")
        prompt_label_end.grid(row=3, column=1, padx=(237,15), pady=(10,10), sticky='W')

        period_entry_start = ttk.Entry(tab2, width=15)
        period_entry_start.grid(row=2, column=1, padx=(225,0))
        period_entry_start.insert(0, '1-Jan-2022')

        period_entry_end = ttk.Entry(tab2, width=15)
        period_entry_end.grid(row=3, column=1, padx=(225,0))
        period_entry_end.insert(0, '')

        total_fees_button = ttk.Button(tab2, text="Get Report", command = get_report)
        total_fees_button.grid(row=4, column=1, padx=(15,15), pady=(15,15), sticky='W')

        result_string = StringVar()
        result_string.set("Total Fees w/ Receipts: \nTotal Gear Fees w/ Receipts: \nTotal Testing/Credits Collected:")
        result_label = ttk.Label(tab2, textvariable=result_string, font = 'Verdana 10 bold')
        result_label.grid(row=5, column=1, padx=(15,15), pady=(15,15), sticky='W')

        mailsearch_label = tk.Label(tab2, text="search counter:")
        mailsearch_label.place(x=95, y=165)






















if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('default')
    root.title("Performance Taekwon-Do")
    root.minsize(width=window_width, height=window_height)
    root.resizable(width=False, height=False)
    MainApplication(root)
    root.mainloop()





