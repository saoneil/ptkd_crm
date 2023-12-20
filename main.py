import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox, simpledialog
import numpy as np
from datetime import datetime, timedelta
import db, email_handler


window_width = 1275
window_height = 775

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Performance Martial Arts - Management")
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(False, False)

        self.data = {}
        self.data2 = {}
        self.data3 = {}
        self.df = pd.DataFrame(self.data)
        self.df2 = pd.DataFrame(self.data2)
        self.df3 = pd.DataFrame(self.data3)

        self.nb = ttk.Notebook(self, width=window_width, height=window_height)
        self.nb.grid(row=0, column=0)

        # variables needed in the other methods/functions
        self.message_box = None
        self.right_click_menu = tk.Menu(self, tearoff=0)
        #self.right_click_menu.add_command(label="Record Payment", command=self.record_payment_right_click)
        self.right_click_menu.add_command(label="Send Email", command=self.send_email_right_click)
        self.right_click_menu.add_command(label="Toggle 'Trial Student'", command=self.toggle_trial_right_click)
        self.right_click_menu.add_command(label="Toggle 'Active Student'", command=self.toggle_active_right_click)
        self.right_click_menu.add_command(label="Add Profile Comment", command=self.profile_comment_right_click)
        self.tab_frames = []
        self.entry_widgets_search_tab1 = {}
        self.entry_widgets_new_student = {}
        self.entry_widget_cancel_rental = {}
        self.entry_widget_add_teaching_hours = {}
        self.entry_widget_add_expense = {}
        self.entry_widgets_existing_student = {}
        self.entry_widgets_testing_results = {}
        self.entry_widgets_add_payment = {}
        self.tax_var = tk.IntVar()
        self.club_var = tk.IntVar(value=0)
        self.method_var = tk.IntVar(value=1)
        self.existing_student_dropdown_value = tk.StringVar()
        self.import_rental_hours_value = tk.StringVar()
        self.student_id = ""

        self.create_tabs()
        self.create_frames()
        self.create_labels_buttons_entries()

        self.my_tree = ttk.Treeview(self.right_frame_tab1)
        self.my_tree_admin = ttk.Treeview(self.right_frame_tab4)
        self.my_tree_testing = ttk.Treeview(self.top_right_frame_tab3)

        self.refresh_datagrid(self.my_tree, self.df, self.right_frame_tab1)
        self.refresh_datagrid(self.my_tree_admin, self.df2, self.right_frame_tab4)
        self.refresh_datagrid(self.my_tree_testing, self.df3, self.top_right_frame_tab3)

    ## DB Operations ##
    ## tab 1 ##
    def view_all_students_command(self):
        df = db.sp_all_active_students()
        print(df)
        self.refresh_datagrid(self.my_tree, df, self.right_frame_tab1)
    def view_trial_students_command(self):
        df = db.sp_all_trial_students()
        print(df)
        self.refresh_datagrid(self.my_tree, df, self.right_frame_tab1)
    def view_waitlist_students_command(self):
        df = db.sp_all_waitlist_students()
        print(df)
        self.refresh_datagrid(self.my_tree, df, self.right_frame_tab1)
    def view_outstanding_payments(self):
        df = db.sp_outstanding_payments()
        print(df)
        self.refresh_datagrid(self.my_tree, df, self.right_frame_tab1)
    def search_grid_tab1_command(self):
        for field, entry_widget in self.entry_widgets_search_tab1.items():
            data = entry_widget.get()
            if field == "First Name:":
                first_name = data
            elif field == "Last Name:":
                last_name = data
            elif field == "Email:":
                email = data
        df = db.search_grid_tab1(first_name, last_name, email)
        self.refresh_datagrid(self.my_tree, df, self.right_frame_tab1)
    def draft_email_all_students(self):
        df = db.sp_all_emails()
        email_list = df["emails"].to_list()
        email_list_formatted = "; ".join(email_list)
        email_handler.create_email(
            subject = "Performance MA - Announcement",
            email_from = "saoneil@live.com",
            emails_to = None,
            emails_cc = "; ".join(["tkd.smacrury@gmail.com", "yoosin1995@hotmail.com"]),
            emails_bcc = email_list_formatted,
            body = """Hello Students/Parents, \n\n\n\n\n\n-------------------\nSean O'Neil\n+1-902-452-7326\nsaoneil@live.com"""
        )
    def draft_email_karate_students(self):
        df = db.sp_karate_emails()
        email_list = df["emails"].to_list()
        email_list_formatted = "; ".join(email_list)
        email_handler.create_email(
            subject = "Performance Karate - ",
            email_from = "saoneil@live.com",
            emails_to = None,
            emails_cc = "; ".join(["tkd.smacrury@gmail.com", "yoosin1995@hotmail.com"]),
            emails_bcc = email_list_formatted,
            body = """Hello Karate Students/Parents, \n\n\n\n\n\n-------------------\nSean O'Neil\n+1-902-452-7326\nsaoneil@live.com"""
        )
    def draft_email_waitlist_students(self):
        df = db.sp_waitlist_emails()
        email_list = df["emails"].to_list()
        email_list_formatted = "; ".join(email_list)
        email_handler.create_email(
            subject = "Performance MA - Invitation to Classes",
            email_from = "saoneil@live.com",
            emails_to = None,
            emails_cc = "; ".join(["tkd.smacrury@gmail.com"]),
            emails_bcc = email_list_formatted,
            body = """Hello,\n\nThis email is being sent to those who I added to my wait list for martial arts classes. I would like to invite you to attend your first class on a trial basis on <date>\n\n\n\n-------------------\nSean O'Neil\n+1-902-452-7326\nsaoneil@live.com"""
        )    
    def commit_payment_to_db(self):
        student_id_list = []
        for field, entry_widget in self.entry_widgets_add_payment.items():
            data = entry_widget.get()
            if (field == "ID1" or field == "ID2" or field == "ID3"):
                if not(data == ""):
                    student_id_list.append(data)
            elif field == "date_till":
                date_till = data
            elif field == "pay_rate":
                pay_rate = data
            elif field == "total":
                total = data
            elif field == "calc_tax":
                calc_tax = data
            elif field == "club":
                club = data
            elif field == "txn_note":
                txn_note = data
            elif field == "etransfer":
                etransfer = data

            try:
                entry_widget.delete(0, 'end')
            except:
                pass

        for id in student_id_list:
            db.sp_commit_payment_to_db(id, date_till, pay_rate, total, calc_tax, club, txn_note)
        
        payer_address, students_first_names = db.get_email_address_for_payment(", ".join(student_id_list))
        student_ids_formatted = ", ".join(student_id_list)
        receipt_data = [students_first_names, txn_note, total, etransfer]
        
        db.sp_insert_club_payment(student_ids_formatted, total, calc_tax, etransfer, txn_note, payer_address, club)

        if club == 0:
            email_handler.create_ptkd_receipt_email(
                subject = "Performance Taekwon-Do - Receipt",
                email_from = "saoneil@live.com",
                emails_to = "; ".join([payer_address]),
                emails_cc = None,
                emails_bcc = "; ".join(["performance_taekwondo@hotmail.com"]),
                file_tempate = "C:\\Users\\saone\\Documents\\PMA\\zflask_app_files\\receipt_template_ptkd.txt",
                receipt_data = receipt_data
            )
        elif club == 1:
                email_handler.create_pkrt_receipt_email(
                subject = "Performance Karate - Receipt",
                email_from = "saoneil@live.com",
                emails_to = "; ".join([payer_address]),
                emails_cc = None,
                emails_bcc = "; ".join(["performance_taekwondo@hotmail.com"]),
                file_tempate = "C:\\Users\\saone\\Documents\\PMA\\zflask_app_files\\receipt_template_pkrt.txt",
                receipt_data = receipt_data
            )
    def save_db_objects(self):
        db.save_db_objects()
        print('DB Back-Ups Created')
    ## tab 2 ##
    def all_students_list_command(self):
        id_list, name_list, combined_list = db.sp_all_students_list()

        dropdown_list = combined_list
        return dropdown_list
    def commit_changes_new_student_command(self):
        for field, entry_widget in self.entry_widgets_new_student.items():
            data = entry_widget.get()
            if field == "First Name:":
                first_name = data
            elif field == "Last Name:":
                last_name = data
            elif field == "Email 1:":
                email1 = data
            elif field == "Email 2:":
                email2 = data
            elif field == "Email 3:":
                email3 = data
            elif field == "Phone 1:":
                phone1 = data
            elif field == "Phone 2:":
                phone2 = data
            elif field == "Phone 3:":
                phone3 = data
            elif field == "Pay Rate:":
                pay_rate = data
            elif field == "Start Date (yyyy-mm-dd):":
                start_date = data
            elif field == "DOB (yyyy-mm-dd):":
                dob = data
            elif field == "DOB-approx:":
                dob_approx = data
            elif field == "Does Karate:":
                does_karate = data
            elif field == "Current Rank:":
                current_rank = data
            try:
                if field == "Start Date (yyyy-mm-dd):":
                    pass
                elif field == "DOB-approx:":
                    pass
                elif field == "Does Karate":
                    pass
                elif field == "Current Rank:":
                    pass
                else:
                    entry_widget.delete(0, 'end')
            except:
                pass
        db.sp_commit_new_student(first_name, last_name, email1, email2, email3, phone1, phone2, phone3, pay_rate, start_date, dob, dob_approx, does_karate, current_rank)
        print("Student Added to DB")
    def existing_student_selection_tab2_command(self, event=None):
        selected_value = self.existing_student_dropdown_value.get()
        self.student_id = selected_value[0:(selected_value.index("-")-1)]
        df = db.sp_view_student_by_id(self.student_id)
        if selected_value:
            student_info = {
                            "First Name:": f"{df.loc[0,'first_name']}",
                            "Last Name:": f"{df.loc[0,'last_name']}",
                            "DOB (yyyy-mm-dd):": f"{df.loc[0,'dob']}",
                            "DOB-approx:": f"{df.loc[0,'dob_approx']}",
                            "Start Date (yyyy-mm-dd):": f"{df.loc[0,'start_date']}",
                            "Active:": f"{df.loc[0,'active']}",
                            "Trial Student:": f"{df.loc[0,'trial_student']}",
                            "Wait List:": f"{df.loc[0,'wait_list']}",
                            "Current Rank:": f"{df.loc[0,'current_rank']}", 
                            "Does Karate:": f"{df.loc[0,'does_karate']}", 
                            "Local Comp Interest:": f"{df.loc[0,'local_competition_interest']}", 
                            "Nat Comp Interest:": f"{df.loc[0,'national_competition_interest']}", 
                            "Intl Comp Interest:": f"{df.loc[0,'international_competition_interest']}", 
                            "Karate Prov Team:": f"{df.loc[0,'karate_prov_team']}", 
                            "Signed Waiver:": f"{df.loc[0,'signed_waiver']}", 
                            "Profile Comment:": f"{df.loc[0,'profile_comment']}", 
                            "Email 1:": f"{df.loc[0,'email1']}", 
                            "Email 2:": f"{df.loc[0,'email2']}", 
                            "Email 3:": f"{df.loc[0,'email3']}", 
                            "Phone 1:": f"{df.loc[0,'phone1']}", 
                            "Phone 2:": f"{df.loc[0,'phone2']}", 
                            "Phone 3:": f"{df.loc[0,'phone3']}", 
                            "YS Test Date:": f"{df.loc[0,'yellow_stripe_testdate']}", 
                            "YB Test Date:": f"{df.loc[0,'yellow_belt_testdate']}", 
                            "GS Test Date:": f"{df.loc[0,'green_stripe_testdate']}", 
                            "GB Test Date:": f"{df.loc[0,'green_belt_testdate']}", 
                            "BS Test Date:": f"{df.loc[0,'blue_stripe_testdate']}", 
                            "BB Test Date:": f"{df.loc[0,'blue_belt_testdate']}", 
                            "RS Test Date:": f"{df.loc[0,'red_stripe_testdate']}", 
                            "RB Test Date:": f"{df.loc[0,'red_belt_testdate']}", 
                            "BKS Test Date:": f"{df.loc[0,'black_stripe_testdate']}",
                            "1st Dan Test Date:": f"{df.loc[0,'1st_dan_testdate']}", 
                        }

            # Update entry widgets in top_right_frame_tab2
            for field, value in student_info.items():
                if field in self.entry_widgets_existing_student:
                    self.entry_widgets_existing_student[field].delete(0, "end")
                    self.entry_widgets_existing_student[field].insert(0, value)
        else:
            # Clear entry widgets if no student is selected
            for entry_widget in self.entry_widgets_existing_student.values():
                entry_widget.delete(0, "end")
    def commit_changes_existing_student_command(self):
        for field, entry_widget in self.entry_widgets_existing_student.items():
            data = entry_widget.get()
            if field == "First Name:":
                first_name = data
            elif field == "Last Name:":
                last_name = data
            elif field == "DOB (yyyy-mm-dd):":
                if data == "None":
                    dob = "NULL"
                else:
                    dob = f"'{data}'"
            elif field == "DOB-approx:":
                dob_approx = data
            elif field == "Start Date (yyyy-mm-dd):":
                if data == "None":
                    start_date = "Null"
                else:
                    start_date = f"'{data}'"
            elif field == "Active:":
                active = data
            elif field == "Trial Student:":
                trial_student = data
            elif field == "Wait List:":
                wait_list = data
            elif field == "Current Rank:":
                current_rank = data
            elif field == "Does Karate:":
                does_karate = data
            elif field == "Local Comp Interest:":
                local_comp_interest = data
            elif field == "Nat Comp Interest:":
                nat_comp_interest = data
            elif field == "Intl Comp Interest:":
                intl_comp_interest = data                            
            elif field == "Karate Prov Team:":
                karate_prov_team = data
            elif field == "Signed Waiver:":
                signed_waiver = data
            elif field == "Profile Comment:":
                profile_comment = data
            elif field == "Email 1:":
                email1 = data
            elif field == "Email 2:":
                email2 = data
            elif field == "Email 3:":
                email3 = data
            elif field == "Phone 1:":
                phone1 = data
            elif field == "Phone 2:":
                phone2 = data
            elif field == "Phone 3:":
                phone3 = data
            elif field == "YS Test Date:":
                if data == "None":
                    ys_testdate = "NULL"
                else:
                    ys_testdate = f"'{data}'"
            elif field == "YB Test Date:":
                if data == "None":
                    yb_testdate = "NULL"
                else:
                    yb_testdate = f"'{data}'"
            elif field == "GS Test Date:":
                if data == "None":
                    gs_testdate = "NULL"
                else:
                    gs_testdate = f"'{data}'"
            elif field == "GB Test Date:":
                if data == "None":
                    gb_testdate = "NULL"
                else:
                    gb_testdate = f"'{data}'"
            elif field == "BS Test Date:":
                if data == "None":
                    bs_testdate = "NULL"
                else:
                    bs_testdate = f"'{data}'"
            elif field == "BB Test Date:":
                if data == "None":
                    bb_testdate = "NULL"
                else:
                    bb_testdate = f"'{data}'"
            elif field == "RS Test Date:":
                if data == "None":
                    rs_testdate = "NULL"
                else:
                    rs_testdate = f"'{data}'"
            elif field == "RB Test Date:":
                if data == "None":
                    rb_testdate = "NULL"
                else:
                    rb_testdate = f"'{data}'"
            elif field == "BKS Test Date:":
                if data == "None":
                    bks_testdate = "NULL"
                else:
                    bks_testdate = f"'{data}'"
            elif field == "1st Dan Test Date:":
                if data == "None":
                    first_dan_testdate = "NULL"
                else:
                    first_dan_testdate = f"'{data}'"

            try:
                entry_widget.delete(0, 'end')
            except:
                pass
        df = db.sp_commit_changes_existing_student(self.student_id, first_name, last_name, dob, dob_approx, start_date, active, trial_student, wait_list, current_rank, does_karate, local_comp_interest, nat_comp_interest, intl_comp_interest, karate_prov_team, signed_waiver, profile_comment, email1, email2, email3, phone1, phone2, phone3, ys_testdate, yb_testdate, gs_testdate, gb_testdate, bs_testdate, bb_testdate, rs_testdate, rb_testdate, bks_testdate, first_dan_testdate)
        print("Changes to Existing Student Complete")
    ## tab 3 ##
    def commit_testing_command(self):
        id_list = []
        for field, entry_widget in self.entry_widgets_testing_results.items():
            data = entry_widget.get()
            if field == "Date of Testing:":
                testing_date = data
            else:
                id_list.append(data)
        id_list_filtered = [item for item in id_list if item != ""]
        for id in id_list_filtered:
            db.sp_commit_testing_results(id, testing_date)
    def display_testing_grid(self):
        df3 = db.sp_display_testing_grid()
        print(df3)
        self.refresh_datagrid(self.my_tree_testing, df3, self.top_right_frame_tab3)
    ## tab 4 ##
    def view_eom_transfer(self):
        df = db.sp_view_eom_transfer()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_current_rental_hours(self):
        df = db.sp_view_current_rental_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_current_teaching_hours(self):
        df = db.sp_view_current_teaching_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def import_rental_month(self):
        data = self.import_rental_hours_value.get()
        print(data)
        db.sp_import_rental_month(data)
        print("Import Rental Hours Complete")
    def cancel_rental_date(self):
        for field, entry_widget in self.entry_widget_cancel_rental.items():
            data = entry_widget.get()
            if field == "Cancel":
                cancel_date = data
            elif field == "Reason":
                cancel_reason = data

            try:
                entry_widget.delete(0, 'end')
            except:
                pass
        db.sp_cancel_rental_date(cancel_date, cancel_reason)
        print("Rental Date Cancelled")
    def add_teaching_hours(self):
        for field, entry_widget in self.entry_widget_add_teaching_hours.items():
            data = entry_widget.get()
            if field == "Date (y-m-d):":
                teaching_date = data
            elif field == "Teacher ID:":
                instructor_id = data
            elif field == "Hours:":
                number_hours = data
            try:
                entry_widget.delete(0, 'end')
            except:
                pass
        db.sp_import_teaching_hours(teaching_date, instructor_id, number_hours)
        print("Teaching hours imported")   
    def view_instructors(self):
        df = db.sp_view_instructors()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def pay_instructors(self):
        df = db.sp_paid_instructors_email()
        db.sp_pay_instructors()
        print("Payments Updated in DB")
        df = df.dropna()
        print(df)

        df_string = df.to_string(index=False)
        
        email_handler.create_email(
            subject="PMA Payroll",
            email_from="saoneil@live.com",
            emails_to="yoosin1995@hotmail.com",
            emails_cc=None,
            emails_bcc=None,
            body = df_string
            )  
    def add_admin_expense(self):
        for field, entry_widget in self.entry_widget_add_expense.items():
            data = entry_widget.get()
            if field == "Date (y-m-d):":
                expense_date = data
            elif field == "Desc:":
                expense_desc = data
            elif field == "Amount:":
                expense_amount = data
            elif field == "Tax:":
                expense_tax = data
            elif field == "Method:":
                expense_method = data
            elif field == "Club (PTKD/PKRT):":
                expense_club = data
            try:
                entry_widget.delete(0, 'end')
            except:
                pass
        db.sp_import_expense(expense_date, expense_desc, expense_amount, expense_tax, expense_method, expense_club)
        print("Expense Imported")
    def view_all_inc(self):
        df = db.sp_all_income()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_all_exp(self):
        df = db.sp_all_expenses()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_all_teaching_hours(self):
        df = db.sp_all_teaching_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_all_rental_hours(self):
        df = db.sp_all_rental_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)
    def view_projections(self):
        df = db.sp_projections()
        print(df)
        self.refresh_datagrid(self.my_tree_admin, df, self.right_frame_tab4)


    ## tkinter app stuff ##
    def create_tabs(self):
        tab1 = ttk.Frame(self.nb)
        self.nb.add(tab1, text='PMA General')
        self.tab_frames.append(tab1)

        tab1.grid_rowconfigure(0, weight=1)
        tab1.grid_columnconfigure(0, weight=1)
        tab1.grid_columnconfigure(1, weight=10)

        tab2 = ttk.Frame(self.nb)
        self.nb.add(tab2, text='PMA Students')
        self.tab_frames.append(tab2)

        tab2.grid_rowconfigure(0, weight=1)
        tab2.grid_columnconfigure(0, weight=1)
        tab2.grid_columnconfigure(1, weight=1)

        tab3 = ttk.Frame(self.nb)
        self.nb.add(tab3, text='PMA Testing')
        self.tab_frames.append(tab3)

        tab3.grid_rowconfigure(0, weight=1)
        tab3.grid_columnconfigure(0, weight=1)
        tab3.grid_columnconfigure(1, weight=11)

        tab4 = ttk.Frame(self.nb)
        self.nb.add(tab4, text='PMA Admin')
        self.tab_frames.append(tab4)

        tab4.grid_rowconfigure(0, weight=1)
        tab4.grid_columnconfigure(0, weight=1)
        tab4.grid_columnconfigure(1, weight=15)
    def create_frames(self):
        ## tab1 ##
        self.left_frame_tab1 = tk.Frame(self.tab_frames[0])
        self.left_frame_tab1.grid(row=0, column=0, sticky="nsew")

        self.right_frame_tab1 = tk.Frame(self.tab_frames[0])
        self.right_frame_tab1.grid(row=0, column=1, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)


        ## tab2 ##
        self.top_left_frame_tab2 = tk.Frame(self.tab_frames[1])
        self.top_left_frame_tab2.grid(row=0, column=0, sticky="nsew")

        self.top_right_frame_tab2 = tk.Frame(self.tab_frames[1])
        self.top_right_frame_tab2.grid(row=0, column=1, sticky="nsew")

        self.bottom_left_frame_tab2 = tk.Frame(self.tab_frames[1])
        self.bottom_left_frame_tab2.grid(row=1, column=0, sticky='nsew')

        self.bottom_right_frame_tab2 = tk.Frame(self.tab_frames[1])
        self.bottom_right_frame_tab2.grid(row=1, column=1, sticky='nsew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        ## tab3 ##
        self.top_left_frame_tab3 = tk.Frame(self.tab_frames[2])
        self.top_left_frame_tab3.grid(row=0, column=0, sticky="nsew")

        self.top_right_frame_tab3 = tk.Frame(self.tab_frames[2])
        self.top_right_frame_tab3.grid(row=0, column=1, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        ## tab4 ##
        self.left_frame_tab4 = tk.Frame(self.tab_frames[3])
        self.left_frame_tab4.grid(row=0, column=0, sticky="nsew")

        self.right_frame_tab4 = tk.Frame(self.tab_frames[3])
        self.right_frame_tab4.grid(row=0, column=1, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
    def refresh_datagrid(self, treeview:ttk.Treeview, df:pd.DataFrame, tab:tk.Frame):
        treeview.delete(*treeview.get_children())
        treeview['show'] = 'headings'

        x_scrollbar = ttk.Scrollbar(tab, orient="horizontal")
        y_scrollbar = ttk.Scrollbar(tab, orient="vertical")
        x_scrollbar.configure(command=treeview.xview)
        y_scrollbar.configure(command=treeview.yview)

        treeview.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        columns = tuple(df.columns.tolist())
        df_rows = df.to_numpy().tolist()
        #treeview.configure(columns=columns)
        treeview['columns'] = columns

        column_sort_order = {column: False for column in columns}

        def sort_treeview(column):
            nonlocal column_sort_order
            column_sort_order[column] = not column_sort_order[column]
            df.sort_values(by=column, ascending=column_sort_order[column], inplace=True)
            self.populate_treeview(treeview, df)

        for column in columns:
            treeview.heading(column, text=column, anchor='w', command=lambda c=column: sort_treeview(c))
            treeview.column(column, stretch=False, minwidth=25, width=100)

        for row in df_rows:
            treeview.insert("", "end", values=row)

        treeview.place(x=1, y=30, width=880, height=650)
        x_scrollbar.place(x=0, y=675, width=880, height=20, anchor='nw')
        y_scrollbar.place(x=880, y=30, width=20, height=650, anchor='nw')

        if tab == self.right_frame_tab1:
            treeview.bind("<Button-3>", self.show_right_click_menu)
    def show_right_click_menu(self, event:tk.Event):
        # Set my_tree based on the event widget
        self.my_tree = event.widget
        self.right_click_menu.post(event.x_root, event.y_root)
    def record_payment_right_click(self):
        selected_items = self.my_tree.selection()
        if selected_items:
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            messagebox.showinfo("Record Payment", f"Recording payment for selected records: {selected_items}\nData: {records_data}")
        else:
            messagebox.showwarning("No Selection", "Please select records to record payment.")
    def send_email_right_click(self):
        student_id_list = []
        email_list = []
        selected_items = self.my_tree.selection()
        if selected_items:
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            for record in records_data:
                student_id_list.append(record[0])

            for id in student_id_list:
                df = db.sp_view_student_by_id(id)
                email_list.append(df.loc[0,'email1'])
                email_list.append(df.loc[0,'email2'])
                email_list.append(df.loc[0,'email3'])

            cleaned_email_list = "; ".join(list(set(list(filter(lambda x: x is not None, email_list)))))
            print(cleaned_email_list)

            email_handler.create_email(
                subject="PMA - ", 
                email_from="saoneil@live.com",
                emails_to=None,
                emails_cc="; ".join(["tkd.smacrury@gmail.com"]),
                emails_bcc=cleaned_email_list,
                body=""
                )

            messagebox.showinfo("Send Email", f"Email draft generated, check drafts folder.")
        else:
            messagebox.showwarning("No Selection", "Please select records to send email.")
    def toggle_trial_right_click(self):
        student_id_list = []
        selected_items = self.my_tree.selection()
        if selected_items:
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            for record in records_data:
                student_id_list.append(record[0])

            for id in student_id_list:
                print(id + " - toggle trial_student value")
                db.sp_toggle_trial_or_active(id, 'trial_student')

            messagebox.showinfo("Toggle Trial", "Toggled 'Trial Student' field for StudentID = " + str(student_id_list))
        else:
            messagebox.showwarning("No Selection", "Please select records to toggle trial flag.")
    def toggle_active_right_click(self):
        student_id_list = []
        selected_items = self.my_tree.selection()
        if selected_items:
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            for record in records_data:
                student_id_list.append(record[0])

            for id in student_id_list:
                print(id + " - toggle trial_student value")
                db.sp_toggle_trial_or_active(id, 'active')

            messagebox.showinfo("Toggle Active", "Toggled 'Active' field for StudentID = " + str(student_id_list))
        else:
            messagebox.showwarning("No Selection", "Please select records to toggle active.")
    def profile_comment_right_click(self):
        student_id_list = []
        selected_items = self.my_tree.selection()
        if selected_items:
            profile_comment = tk.simpledialog.askstring("Input", "Enter your profile comment:")
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            for record in records_data:
                student_id_list.append(record[0])

            for id in student_id_list:
                print(id + " - add profile comment")
                db.sp_add_profile_comment(id, profile_comment)

            messagebox.showinfo("Add Comment", f"Comment: {profile_comment}" + '\n' + "Added for StudentID = " + str(student_id_list))
        else:
            messagebox.showwarning("No Selection", "Please select records to add comment to profile.")
    def populate_treeview(self, treeview:ttk.Treeview, dataframe:pd.DataFrame):
        treeview.delete(*treeview.get_children())

        for row in dataframe.itertuples(index=False, name=None):
            treeview.insert("", "end", values=row)
    def create_labels_buttons_entries(self):
        def tab1(self):
            datagrid_label = tk.Label(self.right_frame_tab1, text="Result Datagrid", font="verdana 15 bold")
            datagrid_label.pack()

            definition_label = tk.Label(self.left_frame_tab1, text="Control Panel", font='verdana 15 bold')
            definition_label.grid(row=1, column=1, columnspan=2, pady=(0,15))

            section_one = [
            ("View All Students:", "All Students", 2, self.view_all_students_command, (0, 5)),
            ("View Trial Students:", "Trial Students", 3, self.view_trial_students_command, (0, 5)),
            ("View Wait List:", "Wait List", 4, self.view_waitlist_students_command, (0, 5)),
            ("Outstanding Payments:", "Outstanding Fees", 5, self.view_outstanding_payments, (0, 25)),
            ("Database Search:", "Search", 6, self.search_grid_tab1_command, (0, 10)),
            ("First Name:", None, 7, None, None),
            ("Last Name:", None, 8, None, None),
            ("Email:", None, 9, None, (0,25)),
            ("Email All Students:", "Draft to All", 10, self.draft_email_all_students, (0, 5)),
            ("Email Karate Students:", "Draft to Karate", 11, self.draft_email_karate_students, (0, 5)),
            ("Email Wait List:", "Draft to Wait-list", 12,self.draft_email_waitlist_students, (0, 25))
            ]
            for label_text, button_text, row, command, pady in section_one:
                label = tk.Label(self.left_frame_tab1, text=label_text)
                label.grid(row=row, column=1, sticky='ne', pady=pady)

                if button_text:
                    button = tk.Button(self.left_frame_tab1, text=button_text, command=command)
                    button.grid(row=row, column=2, sticky='nw', pady=pady)
                else:
                    entry = tk.Entry(self.left_frame_tab1, width=10)
                    entry.grid(row=row, column=2, sticky='nw', pady=pady)

                    self.entry_widgets_search_tab1[label_text] = entry

            section_two = [
                (None, "Add Payment to Database", None, 13, self.commit_payment_to_db, (0, 10)),
                ("Student ID:", None, "ID1", 14, None, (0, 0)),
                ("ID:", None, "ID2", 15, None, (0, 0)),
                ("ID:", None, "ID3", 16, None, (0, 0)),
                ("Good 'Til (y-m-d):", None, "date_till", 17, None, (0, 0)),
                ("Pay Rate:", None, "pay_rate", 18, None, (0, 0)),
                ("Total:", None, "total", 19, None, (0, 0)),
                ("Calc. Tax:", None, "calc_tax", 20, None, (0, 0)),
                ("PKRT:", None, "club", 21, None, (0, 0)),
                ("E-transfer:", None, "etransfer", 22, None, (0, 0)),
                ("Txn Note:", None, "txn_note", 23, None, (0, 0)),
            ]
            for label_text, button_text, entry_text, row, command, pady in section_two:
                if label_text:
                    label = tk.Label(self.left_frame_tab1, text=label_text)
                    label.grid(row=row, column=1, sticky='ne', pady=pady)
                if button_text:
                    button = tk.Button(self.left_frame_tab1, text=button_text, command=command)
                    button.grid(row=row, column=1, sticky='ne', pady=pady, columnspan=2)
                if entry_text:
                    if entry_text == "calc_tax":
                        tickbox = tk.Checkbutton(self.left_frame_tab1, text="", variable=self.tax_var, onvalue=1, offvalue=0)
                        tickbox.grid(row=row, column=2, sticky='nw', pady=pady)

                        self.entry_widgets_add_payment[entry_text] = self.tax_var
                    elif entry_text == "club":
                        tickbox = tk.Checkbutton(self.left_frame_tab1, text="", variable=self.club_var, onvalue=1, offvalue=0)
                        tickbox.grid(row=row, column=2, sticky='nw', pady=pady)

                        self.entry_widgets_add_payment[entry_text] = self.club_var
                    elif entry_text == "etransfer":
                        tickbox = tk.Checkbutton(self.left_frame_tab1, text="", variable=self.method_var, onvalue=1, offvalue=0)
                        tickbox.grid(row=row, column=2, sticky='nw', pady=pady)

                        self.entry_widgets_add_payment[entry_text] = self.method_var
                    else:
                        entry = tk.Entry(self.left_frame_tab1, width=15)
                        entry.grid(row=row, column=2, sticky='nw', pady=pady)

                        self.entry_widgets_add_payment[entry_text] = entry

            backup_button = tk.Button(self.left_frame_tab1, text="Backup DB Objects", font="verdana 10 bold", command=self.save_db_objects)
            backup_button.grid(row=24, column=1, columnspan=2, pady=(25,0))
        def tab2(self):
            ## new student section
            new_student_label = tk.Label(self.top_left_frame_tab2, text="New Student Registration", font="verdana 15 bold")
            new_student_label.grid(row=1, column=1, columnspan=2, pady=(30,15))

            new_student_fields = [
            "First Name:",
            "Last Name:",
            "Email 1:",
            "Email 2:",
            "Email 3:",
            "Phone 1:",
            "Phone 2:",
            "Phone 3:",
            "Pay Rate:",
            "Start Date (yyyy-mm-dd):",
            "DOB (yyyy-mm-dd):",
            "DOB-approx:",
            "Does Karate:",
            "Current Rank:",
            ]
            for i, field in enumerate(new_student_fields, start=2):
                label = tk.Label(self.top_left_frame_tab2, text=field)
                label.grid(row=i, column=1, sticky='e', pady=(0,5))

                entry = tk.Entry(self.top_left_frame_tab2)
                entry.grid(row=i, column=2)

                # Store the entry widget in the dictionary with the field as the key
                self.entry_widgets_new_student[field] = entry

            self.entry_widgets_new_student["Start Date (yyyy-mm-dd):"].insert(0, datetime.today().strftime("%Y-%m-%d"))
            self.entry_widgets_new_student["DOB-approx:"].insert(0, 0)
            self.entry_widgets_new_student["Does Karate:"].insert(0, 0)
            self.entry_widgets_new_student["Current Rank:"].insert(0, "White Belt")

            commit_new_student = tk.Button(self.top_left_frame_tab2, text="Commit New Student to DB", command=self.commit_changes_new_student_command)
            commit_new_student.grid(row=i + 1, column=1, columnspan=2)
            
            ## current student section
            existing_student_label = tk.Label(self.top_right_frame_tab2, text = "Modify Existing Student", font="verdana 15 bold")
            existing_student_label.grid(row=0, column=0, columnspan=6, sticky='w', pady=(30,15))

            existing_student_label = tk.Label(self.top_right_frame_tab2, text="Edit Existing Student:")
            existing_student_label.grid(row=1, column=1, sticky='e', pady=(0,30))

            existing_student_dropdown = ttk.Combobox(self.top_right_frame_tab2, textvariable=self.existing_student_dropdown_value)
            existing_student_dropdown['values'] = self.all_students_list_command()
            existing_student_dropdown.grid(row=1, column=2, pady=(0,30))
            existing_student_dropdown.bind('<<ComboboxSelected>>', self.existing_student_selection_tab2_command)


            current_student_label_info = [
            ("First Name:", 2, 1),
            ("Last Name:", 3, 1),
            ("DOB (yyyy-mm-dd):", 4, 1),
            ("DOB-approx:", 5, 1),
            ("Start Date (yyyy-mm-dd):", 6, 1),
            ("Active:", 7, 1),
            ("Trial Student:", 8, 1),
            ("Wait List:", 9, 1),
            ("Current Rank:", 10, 1),
            ("Does Karate:", 11, 1),
            ("Local Comp Interest:", 12, 1),
            ("Nat Comp Interest:", 13, 1),
            ("Intl Comp Interest:", 14, 1),
            ("Karate Prov Team:", 15, 1),
            ("Signed Waiver:", 16, 1),
            ("Profile Comment:", 17, 1),

            ("Email 1:", 2, 3),
            ("Email 2:", 3, 3),
            ("Email 3:", 4, 3),
            ("Phone 1:", 5, 3),
            ("Phone 2:", 6, 3),
            ("Phone 3:", 7, 3),

            ("YS Test Date:", 2, 5),
            ("YB Test Date:", 3, 5),
            ("GS Test Date:", 4, 5),
            ("GB Test Date:", 5, 5),
            ("BS Test Date:", 6, 5),
            ("BB Test Date:", 7, 5),
            ("RS Test Date:", 8, 5),
            ("RB Test Date:", 9, 5),
            ("BKS Test Date:", 10, 5),
            ("1st Dan Test Date:", 11, 5)
            ]
            for (text, row, col) in current_student_label_info:
                label = tk.Label(self.top_right_frame_tab2, text=text)
                label.grid(row=row, column=col, sticky='e', pady=(0,5))

                if text == "Profile Comment:":
                    entry = tk.Entry(self.top_right_frame_tab2, width=90)
                    entry.grid(row=row, column=col+1, padx=(0, 10), columnspan=6)
                else:
                    entry = tk.Entry(self.top_right_frame_tab2)
                    entry.grid(row=row, column=col+1, padx=(0, 10))

                self.entry_widgets_existing_student[text] = entry

            button_existing = tk.Button(self.top_right_frame_tab2, text="Commit Changes to DB for Existing Student", command=self.commit_changes_existing_student_command)
            button_existing.grid(row=18, column=1, columnspan=6, sticky='n')
        def tab3(self):
            testing_update_label = tk.Label(self.top_left_frame_tab3, text="Log Testing Results", font="verdana 15 bold")
            testing_update_label.grid(row=1, column=1, columnspan=2, sticky='w', pady=(15,15), padx=(10,10))

            datagrid_label = tk.Label(self.top_right_frame_tab3, text="Result Datagrid", font="verdana 15 bold")
            datagrid_label.pack()

            testing_fields = [
            ("Date of Testing:", 3, 1, (0,5), 'e'),
            ("ID 1:", 4, 1, (0,5), 'e'),
            ("ID 2:", 5, 1, (0,5), 'e'),
            ("ID 3:", 6, 1, (0,5), 'e'),
            ("ID 4:", 7, 1, (0,5), 'e'),
            ("ID 5:", 8, 1, (0,5), 'e'),
            ("ID 6:", 9, 1, (0,5), 'e'),
            ("ID 7:", 10, 1, (0,5), 'e'),
            ("ID 8:", 11, 1, (0,5), 'e'),
            ("ID 9:", 12, 1, (0,5), 'e'),
            ("ID 10:", 13, 1, (0,5), 'e'),
            ("ID 11:", 14, 1, (0,5), 'e'),
            ("ID 12:", 15, 1, (0,5), 'e'),
            ("ID 13:", 16, 1, (0,5), 'e'),
            ("ID 14:", 17, 1, (0,5), 'e'),
            ("ID 15:", 18, 1, (0,5), 'e'),
            ("ID 16:", 19, 1, (0,5), 'e'),
            ("ID 17:", 20, 1, (0,5), 'e'),
            ("ID 18:", 21, 1, (0,5), 'e'),
            ("ID 19:", 22, 1, (0,5), 'e'),
            ("ID 20:", 23, 1, (0,5), 'e'),
            ]
            for (field, row, col, pady, sticky) in testing_fields:
                label = tk.Label(self.top_left_frame_tab3, text=field)
                label.grid(row=row+1, column=col, sticky=sticky, pady=pady)

                entry = tk.Entry(self.top_left_frame_tab3)
                entry.grid(row=row+1, column=col+1, sticky='w')

                # Store the entry widget in the dictionary with the field as the key
                self.entry_widgets_testing_results[field] = entry

            self.entry_widgets_testing_results["Date of Testing:"].insert(0, datetime.today().strftime("%Y-%m-%d"))

            testing_update_button = tk.Button(self.top_left_frame_tab3, text="Commit Testing to DB", command=self.commit_testing_command)
            testing_update_button.grid(row=25, column=1, columnspan=2, pady=(15,15))

            testing_data_button = tk.Button(self.top_left_frame_tab3, text="Display Testing Data", command=self.display_testing_grid)
            testing_data_button.grid(row=26, column=1, columnspan=2, pady=(0,15))
        def tab4(self):
            datagrid_label = tk.Label(self.right_frame_tab4, text="Result Datagrid", font="verdana 15 bold")
            datagrid_label.pack()

            definition_label = tk.Label(self.left_frame_tab4, text="Control Panel", font='verdana 15 bold')
            definition_label.grid(row=1, column=1, columnspan=2, pady=(0,15))


            section_one = [
                ("EOM Transfer:", "Transfer", self.view_eom_transfer, 2, 'ne', (0,3)),
                ("Monthly Rentals:", "Rental Hours", self.view_current_rental_hours, 3, 'ne', (0,3)),
                ("Monthly Teaching:", "Teaching Hours", self.view_current_teaching_hours, 4, 'ne', (0,3))
            ]
            for label_text, button_text, command, row, sticky, pady in section_one:
                label = tk.Label(self.left_frame_tab4, text=label_text)
                label.grid(row=row, column=1, sticky=sticky, pady=pady)

                button = tk.Button(self.left_frame_tab4, text=button_text, height=1, command=command)
                button.grid(row=row, column=2, sticky='nw', pady=pady)

                if label_text == "Monthly Teaching:":
                    button = tk.Button(self.left_frame_tab4, text="Pay Instructors", height=1, command=self.pay_instructors)
                    button.grid(row=row, column=3, sticky='nw', pady=pady)


            import_rental_hours_dropdown = ttk.Combobox(self.left_frame_tab4, textvariable=self.import_rental_hours_value, width=15)
            import_rental_hours_dropdown['values'] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            import_rental_hours_dropdown.grid(row=5, column=2, sticky='ne', pady=(20,10))


            section_two = [
                ("Import Rental Hrs:", None, "Load", self.import_rental_month, 5, (15,3)),
                ("Rental Date:", "Cancel", None, None, 6, (0,3)),
                ("Cancel Reason:", "Reason", "Cancel Rental", self.cancel_rental_date, 7, (0,3))
            ]
            for label_text, entry_text, button_text, command, row, pady in section_two:
                if label_text:
                    label = tk.Label(self.left_frame_tab4, text=label_text)
                    label.grid(row=row, column=1, sticky='ne', pady=pady)
                if entry_text:
                    entry = tk.Entry(self.left_frame_tab4, text=entry_text, width=15)
                    entry.grid(row=row, column=2, sticky='nw', pady=pady)

                    self.entry_widget_cancel_rental[entry_text] = entry
                if button_text:
                    button = tk.Button(self.left_frame_tab4, text=button_text, command=command)
                    button.grid(row=row, column=3, sticky='nw', pady=pady)


            section_three = [
                ("Add Teaching Hours", 8, 1, 'nw', (20,0)),
                ("Date (y-m-d):", 9, 2, 'ne', (5,0)),
                ("Teacher ID:", 10, 2, 'ne', (0,0)),
                ("Hours:", 11, 2, 'ne', (0,0)),
            ]
            for label_text, row, col, sticky, pady in section_three:
                if label_text == "Add Teaching Hours":
                    label = tk.Label(self.left_frame_tab4, text=label_text, font="verdana 7 bold")
                    label.grid(row=row, column=col, sticky=sticky, pady=pady)

                    button = tk.Button(self.left_frame_tab4, text="Enter Record", command=self.add_teaching_hours)
                    button.grid(row=9, column=col, sticky='nw', rowspan=2)

                    button = tk.Button(self.left_frame_tab4, text="View Instructors", command=self.view_instructors)
                    button.grid(row=10, column=col, sticky='nw', rowspan=2)
                else:
                    label = tk.Label(self.left_frame_tab4, text=label_text)
                    label.grid(row=row, column=col, sticky=sticky, pady=pady)

                    entry = tk.Entry(self.left_frame_tab4, width=15)
                    entry.grid(row=row, column=3, sticky='nw', pady=pady)

                    self.entry_widget_add_teaching_hours[label_text] = entry


            section_four = [
                ("Add Expense", 12, 1, 'nw', (20,0)),
                ("Date (y-m-d):", 13, 2, 'ne', (0,0)),
                ("Desc:", 14, 2, 'ne', (0,0)),
                ("Amount:", 15, 2, 'ne', (0,0)),
                ("Tax:", 16, 2, 'ne', (0,0)),
                # ("Total:", 17, 2, 'ne', (0,0)),
                ("Method:", 18, 2, 'ne', (0,0)),
                # ("Comment:", 19, 2, 'ne', (0,0)),
                ("Club (PTKD/PKRT):", 20, 2, 'ne', (0,0))
            ]
            for label_text, row, col, sticky, pady in section_four:
                if label_text == "Add Expense":
                    label = tk.Label(self.left_frame_tab4, text=label_text, font="verdana 7 bold")
                    label.grid(row=row, column=col, sticky=sticky, pady=pady)

                    button = tk.Button(self.left_frame_tab4, text="Enter Record", command=self.add_admin_expense)
                    button.grid(row=row+1, column=col, sticky='nw', rowspan=2)
                else:
                    label = tk.Label(self.left_frame_tab4, text=label_text)
                    label.grid(row=row, column=col, sticky=sticky, pady=pady)

                    entry = tk.Entry(self.left_frame_tab4, width=15)
                    entry.grid(row=row, column=3, sticky='nw', pady=pady)

                    self.entry_widget_add_expense[label_text] = entry


            section_five = [
                ("Financials:", 21, 1, None, 'nw', (50,0)),
                ("All Income", 21, 2, self.view_all_inc, 'nw', (50,0)),
                ("All Expenses", 21, 3, self.view_all_exp, 'nw', (50,0)),
                ("All Teaching Hours", 22, 2, self.view_all_teaching_hours, 'nw', (0,0)),
                ("All Rental Hours", 22, 3, self.view_all_rental_hours, 'nw', (0,0)),
                ("Projections:", 23, 1, None, 'nw', (10,0)),
                ("12 Month", 23, 2, self.view_projections, 'nw', (10,0))
            ]
            for text, row, col, command, sticky, pady in section_five:
                if (text == "Financials:" or text == "Projections:"):
                    label = tk.Label(self.left_frame_tab4, text = text, font="verdana 8 bold")
                    label.grid(row=row, column=col, sticky=sticky, pady=pady)
                else:
                    button = tk.Button(self.left_frame_tab4, text=text, width=14, command=command)
                    button.grid(row=row, column=col, sticky=sticky, pady=pady)


        tab1(self)
        tab2(self)
        tab3(self)
        tab4(self)

        
if __name__ == "__main__":
    app = MyApp()
    ttk.Style().theme_use('default')
    app.mainloop()