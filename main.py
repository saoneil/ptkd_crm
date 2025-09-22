import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinter import simpledialog
import numpy as np
from datetime import datetime, timedelta
import db, email_handler_google


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
        self.data4 = {}
        self.df = pd.DataFrame(self.data)
        self.df2 = pd.DataFrame(self.data2)
        self.df3 = pd.DataFrame(self.data3)
        self.df4 = pd.DataFrame(self.data4)

        self.nb = ttk.Notebook(self, width=window_width, height=window_height)
        self.nb.grid(row=0, column=0)

        # variables needed in the other methods/functions
        self.message_box = None
        self.right_click_menu = tk.Menu(self, tearoff=0)
        #self.right_click_menu.add_command(label="Record Payment", command=self.record_payment_right_click)
        self.right_click_menu.add_command(label="Send Email", command=self.send_email_right_click)
        self.right_click_menu.add_command(label="Toggle 'Trial Student'", command=self.toggle_trial_right_click)
        self.right_click_menu.add_command(label="Toggle 'Active Student'", command=self.toggle_active_right_click)
        self.right_click_menu.add_command(label="Toggle 'Wait List'", command=self.toggle_waitlist_right_click)
        self.right_click_menu.add_command(label="Add Profile Comment", command=self.profile_comment_right_click)
        self.tab_frames = []
        self.entry_widgets_search_tab1 = {}
        self.entry_widgets_search_equipment = {}
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
        self.my_tree_equipment = ttk.Treeview(self.right_frame_tab5)
        self.my_tree_testing = ttk.Treeview(self.top_right_frame_tab3)

        self.refresh_datagrid(self.my_tree, self.df, self.right_frame_tab1)
        self.refresh_datagrid(self.my_tree_admin, self.df2, self.right_frame_tab4)
        self.refresh_datagrid(self.my_tree_equipment, self.df4, self.right_frame_tab5)
        self.refresh_datagrid(self.my_tree_testing, self.df3, self.top_right_frame_tab3)
        
        # Add context menu for PMA Equipment tab
        self.setup_equipment_context_menu()

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
        
        # Split email list into batches of 100
        batch_size = 100
        email_batches = [email_list[i:i + batch_size] for i in range(0, len(email_list), batch_size)]
        
        # Create multiple email drafts if needed
        for i, batch in enumerate(email_batches):
            batch_number = i + 1
            total_batches = len(email_batches)
            
            # Create subject with batch info if multiple batches
            subject = "Performance MA - Announcement"
            
            email_handler_google.create_html_email(
                subject = subject,
                email_from = "saoneil@live.com",
                emails_to = [],  # Empty list instead of [None]
                emails_cc = [],
                emails_bcc = batch,
                body = f"""<p>Hello Students/Parents,</p>
                
                <p><br><br><br><br></p>
                
                <div style="color: #666666; font-size: 12px; margin-top: 20px;">
                    <p style="margin: 5px 0; font-family: Arial, sans-serif;">
                        ___________________<br>
                        <strong>Sean O'Neil</strong><br>
                        +1-902-452-7326<br>
                        <a href="mailto:saoneil@live.com" style="color: #666666; text-decoration: none;">saoneil@live.com</a>
                    </p>
                </div>"""
            )
        
        # Show confirmation message
        if total_batches > 1:
            messagebox.showinfo("Email Drafts Created", 
                f"Created {total_batches} email drafts due to Gmail's 100 recipient limit.\n"
                f"Total recipients: {len(email_list)}\n"
                f"Batch 1: {len(email_batches[0])} recipients\n"
                f"Batch 2: {len(email_batches[1])} recipients" if total_batches > 1 else "")
        else:
            messagebox.showinfo("Email Draft Created", 
                f"Created 1 email draft with {len(email_list)} recipients.")
    def draft_email_karate_students(self):
        df = db.sp_karate_emails()
        print(df['emails'].to_string(index=False))
        email_list = df["emails"].to_list()
        # email_list_formatted = "; ".join(email_list)
        email_handler_google.create_html_email(
            subject = "Performance Karate - Announcement",
            email_from = "saoneil@live.com",
            emails_to = [],
            emails_cc = [],
            emails_bcc = email_list,
            body = """<p>Hello Karate Students/Parents,</p>
            
            <p><br><br><br><br></p>
            
            <div style="color: #666666; font-size: 12px; margin-top: 20px;">
                <p style="margin: 5px 0; font-family: Arial, sans-serif;">
                    ___________________<br>
                    <strong>Sean O'Neil</strong><br>
                    +1-902-452-7326<br>
                    <a href="mailto:saoneil@live.com" style="color: #666666; text-decoration: none;">saoneil@live.com</a>
                </p>
            </div>"""
        )
    def draft_email_waitlist_students(self):
        df = db.sp_waitlist_emails()
        email_list = df["emails"].to_list()
        # email_list_formatted = "; ".join(email_list)
        email_handler_google.create_html_email(
            subject = "Performance MA - Invitation to Classes",
            email_from = "saoneil@live.com",
            emails_to = [],
            emails_cc = [],
            emails_bcc = email_list,
            body = """<p>Hello,</p>
            
            <p>This email is being sent to those who I added to my wait list for martial arts classes. I would like to invite you to attend your first class on a trial basis on <strong>&lt;date&gt;</strong></p>
            
            <p><br><br></p>
            
            <div style="color: #666666; font-size: 12px; margin-top: 20px;">
                <p style="margin: 5px 0; font-family: Arial, sans-serif;">
                    ___________________<br>
                    <strong>Sean O'Neil</strong><br>
                    +1-902-452-7326<br>
                    <a href="mailto:saoneil@live.com" style="color: #666666; text-decoration: none;">saoneil@live.com</a>
                </p>
            </div>"""
        )    
    def commit_payment_to_db(self):
        student_id_list = []
        for field, entry_widget in self.entry_widgets_add_payment.items():
            data = entry_widget.get()
            if (field == "ID1" or field == "ID2" or field == "ID3" or field == "ID4"):
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
        payer_address_string = ', '.join(payer_address)
        student_ids_formatted = ", ".join(student_id_list)
        receipt_data = [students_first_names, txn_note, total, etransfer]
        
        db.sp_insert_club_payment(student_ids_formatted, total, calc_tax, etransfer, txn_note, payer_address_string, club)

        if club == 0:
            email_handler_google.create_ptkd_receipt_email(
                subject = "Performance Taekwon-Do - Receipt",
                email_from = "saoneil@live.com",
                emails_to = payer_address,
                emails_cc = [],
                emails_bcc = ["performance_taekwondo@hotmail.com"],
                file_template = "C:\\Users\\saone\\Documents\\PMA\\zflask_app_files\\receipt_template_ptkd.txt",
                receipt_data = receipt_data
            )
        elif club == 1:
                email_handler_google.create_pkrt_receipt_email(
                subject = "Performance Karate - Receipt",
                email_from = "saoneil@live.com",
                emails_to = payer_address,
                emails_cc = [],
                emails_bcc = ["performance_taekwondo@hotmail.com"],
                file_template = "C:\\Users\\saone\\Documents\\PMA\\zflask_app_files\\receipt_template_pkrt.txt",
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
                if data == "":
                    pay_rate = 0
                else:
                    pay_rate = data
            elif field == "Start Date (yyyy-mm-dd):":
                start_date = data
            elif field == "DOB (yyyy-mm-dd):":
                if data == "":
                    dob = "NULL"
                else:
                    dob = f"'{data}'"
            elif field == "DOB-approx:":
                dob_approx = data
            elif field == "Does Karate:":
                if data == "":
                    does_karate = 0
                else:
                    does_karate = data
            elif field == "Current Rank:":
                current_rank = data
            try:
                if field == "Start Date (yyyy-mm-dd):":
                    pass
                elif field == "DOB-approx:":
                    pass
                elif field == "Does Karate:":
                    pass
                elif field == "Current Rank:":
                    pass
                else:
                    entry_widget.delete(0, 'end')
            except:
                pass
        print(type(pay_rate))
        print(start_date)
        print(type(dob))
        print(dob_approx)
        print(does_karate)
        print(current_rank)
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
        
        email_handler_google.create_email(
            subject="PMA Payroll",
            email_from="saoneil@live.com",
            emails_to=[],
            emails_cc=[],
            emails_bcc=[],
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
    ## tab 5 - PMA Equipment methods ##
    def view_students_equipment(self):
        df = db.sp_view_active_students()
        print(df)
        self.refresh_datagrid_equipment(self.my_tree_equipment, df, self.right_frame_tab5)
    def search_grid_equipment_command(self):
        for field, entry_widget in self.entry_widgets_search_equipment.items():
            data = entry_widget.get()
            if field == "First Name:":
                first_name = data
            elif field == "Last Name:":
                last_name = data
            elif field == "Email:":
                email = data
        df = db.search_grid_tab1(first_name, last_name, email)
        self.refresh_datagrid_equipment(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_equipment_list_equipment(self):
        df = db.sp_view_club_equipment()
        print(df)
        self.refresh_datagrid_equipment(self.my_tree_equipment, df, self.right_frame_tab5)
        # Clear context menu flag for non-transaction views
        self.current_equipment_view = None
    def view_stock_quantities_equipment(self):
        df = db.sp_club_equipment_remaining_stock()
        
        # Convert numeric columns to integers
        for column in df.columns:
            if df[column].dtype in ['float64', 'float32', 'int64', 'int32']:
                # Convert to int, handling NaN values by filling with 0 first
                df[column] = df[column].fillna(0).astype(int)
        
        print(df)
        self.refresh_datagrid_equipment(self.my_tree_equipment, df, self.right_frame_tab5)
        # Clear context menu flag for non-transaction views
        self.current_equipment_view = None
    def view_transactions_equipment(self):
        df = db.sp_view_club_equipment_transactions()
        
        # Create a copy to track original null values before conversion
        original_df = df.copy()
        
        # Convert numeric columns to integers, excluding timestamp columns
        for column in df.columns:
            if df[column].dtype in ['float64', 'float32', 'int64', 'int32']:
                # Skip timestamp columns (pay_date, paydate, date, etc.)
                if not any(timestamp_keyword in column.lower() for timestamp_keyword in ['date', 'time', 'timestamp']):
                    # Convert to int, handling NaN values by filling with 0 first
                    df[column] = df[column].fillna(0).astype(int)
        
        print(df)
        self.refresh_datagrid_with_coloring(self.my_tree_equipment, df, self.right_frame_tab5, original_df)
        # Store the dataframe for context menu access
        self.current_transactions_df = df
        # Set flag to enable context menu for transactions
        self.current_equipment_view = 'transactions'
    def received_and_paid_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Received & Paid - Equipment Payment")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student entry with dynamic filtering
        tk.Label(main_frame, text="Student:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        student_var = tk.StringVar()
        student_entry = tk.Entry(main_frame, textvariable=student_var, width=33)
        student_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Create listbox for student selection
        student_listbox = tk.Listbox(main_frame, height=6, width=33)
        student_listbox.grid(row=0, column=1, sticky='w', pady=(30, 10))
        student_listbox.grid_remove()  # Hide initially
        
        # Store student data for filtering
        self.student_data = []
        # Store equipment data for ID lookup
        self.equipment_data = []
        
        # Equipment dropdown
        tk.Label(main_frame, text="Equipment:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        equipment_var = tk.StringVar()
        equipment_dropdown = ttk.Combobox(main_frame, textvariable=equipment_var, state="readonly", width=30)
        equipment_dropdown.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Quantity entry
        tk.Label(main_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(main_frame, textvariable=quantity_var, width=33)
        quantity_entry.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Amount entry
        tk.Label(main_frame, text="Amount($):").grid(row=3, column=0, sticky='w', pady=(0, 10))
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(main_frame, textvariable=amount_var, width=33)
        amount_entry.grid(row=3, column=1, sticky='w', pady=(0, 10))
        
        # Load data into dropdowns
        try:
            students_df = db.get_all_students_for_dropdown()
            # Store student data with ID for backend use
            self.student_data = [{'id': row['id'], 'name': row['name']} for _, row in students_df.iterrows()]
            # Set initial values (just names for display)
            student_names = [student['name'] for student in self.student_data]
            # Populate the listbox initially
            for student_name in student_names:
                student_listbox.insert(tk.END, student_name)
            
            equipment_df = db.get_all_equipment_for_dropdown()
            # Store equipment data with ID for backend use
            self.equipment_data = [{'id': row['id'], 'description': row['item_description']} for _, row in equipment_df.iterrows()]
            # Set initial values (just descriptions for display)
            equipment_descriptions = [equipment['description'] for equipment in self.equipment_data]
            equipment_dropdown['values'] = equipment_descriptions
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            dialog.destroy()
            return
        
        # Add filtering functionality to student entry
        def filter_students():
            # Get the current text in the entry
            typed_text = student_var.get().lower()
            
            # Clear the listbox
            student_listbox.delete(0, tk.END)
            
            # Filter students based on typed text
            if typed_text:
                filtered_students = [student['name'] for student in self.student_data 
                                   if typed_text in student['name'].lower()]
            else:
                filtered_students = [student['name'] for student in self.student_data]
            
            # Add filtered students to listbox
            for student_name in filtered_students:
                student_listbox.insert(tk.END, student_name)
            
            # Show listbox if there are results
            if filtered_students:
                student_listbox.grid()
                # Auto-select if only one match
                if len(filtered_students) == 1:
                    student_listbox.selection_set(0)
            else:
                student_listbox.grid_remove()
        
        def on_student_select(event=None):
            # When a student is selected from listbox
            selection = student_listbox.curselection()
            if selection:
                selected_name = student_listbox.get(selection[0])
                student_var.set(selected_name)
                student_listbox.grid_remove()
        
        def on_student_click(event):
            # Single-click selection
            on_student_select()
        
        def on_student_key_press(event):
            # Handle keyboard navigation
            if event.keysym == 'Return':
                on_student_select()
            elif event.keysym == 'Escape':
                student_listbox.grid_remove()
            elif event.keysym == 'Tab':
                # Auto-select if only one match
                if student_listbox.size() == 1:
                    on_student_select()
            elif event.keysym in ['Up', 'Down']:
                # Allow normal listbox navigation
                pass
            else:
                # For other keys, let the entry handle them
                return
        
        def on_student_focus_in(event):
            # Show all students when entry gets focus
            filter_students()
        
        def on_student_focus_out(event):
            # Hide listbox when entry loses focus (with delay)
            dialog.after(150, lambda: student_listbox.grid_remove())
        
        # Bind events
        student_entry.bind('<KeyRelease>', lambda e: filter_students())
        student_entry.bind('<KeyPress>', on_student_key_press)
        student_entry.bind('<FocusIn>', on_student_focus_in)
        student_entry.bind('<FocusOut>', on_student_focus_out)
        student_listbox.bind('<Button-1>', on_student_click)
        student_listbox.bind('<Double-Button-1>', on_student_select)
        student_listbox.bind('<Return>', on_student_select)
        student_listbox.bind('<KeyPress>', on_student_key_press)
        
        # Validation and submission function
        def validate_and_submit():
            # Validate student selection
            if not student_var.get():
                tk.messagebox.showerror("Validation Error", "Please select a student.")
                return
            
            # Validate equipment selection
            if not equipment_var.get():
                tk.messagebox.showerror("Validation Error", "Please select equipment.")
                return
            
            # Validate quantity
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid quantity (positive integer).")
                return
            
            # Validate amount
            try:
                amount = float(amount_var.get())
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid amount (number >= 0).")
                return
            
            # Extract IDs from dropdown selections
            # Find student ID by matching the selected name
            selected_student_name = student_var.get()
            student_id = None
            for student in self.student_data:
                if student['name'] == selected_student_name:
                    student_id = student['id']
                    break
            
            if student_id is None:
                tk.messagebox.showerror("Validation Error", "Selected student not found.")
                return
            
            # Find equipment ID by matching the selected description
            selected_equipment_description = equipment_var.get()
            equipment_id = None
            for equipment in self.equipment_data:
                if equipment['description'] == selected_equipment_description:
                    equipment_id = equipment['id']
                    break
            
            if equipment_id is None:
                tk.messagebox.showerror("Validation Error", "Selected equipment not found.")
                return
            
            # Get current date
            from datetime import datetime
            paydate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Call the stored procedure
                db.sp_insert_club_equipment_payment(student_id, equipment_id, quantity, amount, 1, paydate)
                tk.messagebox.showinfo("Success", "Payment recorded successfully!")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to record payment: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def received_not_paid_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Received, Not Paid - Equipment Payment")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student entry with dynamic filtering
        tk.Label(main_frame, text="Student:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        student_var = tk.StringVar()
        student_entry = tk.Entry(main_frame, textvariable=student_var, width=33)
        student_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Create listbox for student selection
        student_listbox = tk.Listbox(main_frame, height=6, width=33)
        student_listbox.grid(row=0, column=1, sticky='w', pady=(30, 10))
        student_listbox.grid_remove()  # Hide initially
        
        # Store student data for filtering
        self.student_data = []
        # Store equipment data for ID lookup
        self.equipment_data = []
        
        # Equipment dropdown
        tk.Label(main_frame, text="Equipment:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        equipment_var = tk.StringVar()
        equipment_dropdown = ttk.Combobox(main_frame, textvariable=equipment_var, state="readonly", width=30)
        equipment_dropdown.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Quantity entry
        tk.Label(main_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(main_frame, textvariable=quantity_var, width=33)
        quantity_entry.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Amount entry (defaults to 0 for "Not Paid")
        tk.Label(main_frame, text="Amount($):").grid(row=3, column=0, sticky='w', pady=(0, 10))
        amount_var = tk.StringVar(value="0")
        amount_entry = tk.Entry(main_frame, textvariable=amount_var, width=33)
        amount_entry.grid(row=3, column=1, sticky='w', pady=(0, 10))
        
        # Load data into dropdowns
        try:
            students_df = db.get_all_students_for_dropdown()
            # Store student data with ID for backend use
            self.student_data = [{'id': row['id'], 'name': row['name']} for _, row in students_df.iterrows()]
            # Set initial values (just names for display)
            student_names = [student['name'] for student in self.student_data]
            # Populate the listbox initially
            for student_name in student_names:
                student_listbox.insert(tk.END, student_name)
            
            equipment_df = db.get_all_equipment_for_dropdown()
            # Store equipment data with ID for backend use
            self.equipment_data = [{'id': row['id'], 'description': row['item_description']} for _, row in equipment_df.iterrows()]
            # Set initial values (just descriptions for display)
            equipment_descriptions = [equipment['description'] for equipment in self.equipment_data]
            equipment_dropdown['values'] = equipment_descriptions
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            dialog.destroy()
            return
        
        # Add filtering functionality to student entry
        def filter_students():
            # Get the current text in the entry
            typed_text = student_var.get().lower()
            
            # Clear the listbox
            student_listbox.delete(0, tk.END)
            
            # Filter students based on typed text
            if typed_text:
                filtered_students = [student['name'] for student in self.student_data 
                                   if typed_text in student['name'].lower()]
            else:
                filtered_students = [student['name'] for student in self.student_data]
            
            # Add filtered students to listbox
            for student_name in filtered_students:
                student_listbox.insert(tk.END, student_name)
            
            # Show listbox if there are results
            if filtered_students:
                student_listbox.grid()
                # Auto-select if only one match
                if len(filtered_students) == 1:
                    student_listbox.selection_set(0)
            else:
                student_listbox.grid_remove()
        
        def on_student_select(event=None):
            # When a student is selected from listbox
            selection = student_listbox.curselection()
            if selection:
                selected_name = student_listbox.get(selection[0])
                student_var.set(selected_name)
                student_listbox.grid_remove()
        
        def on_student_click(event):
            # Single-click selection
            on_student_select()
        
        def on_student_key_press(event):
            # Handle keyboard navigation
            if event.keysym == 'Return':
                on_student_select()
            elif event.keysym == 'Escape':
                student_listbox.grid_remove()
            elif event.keysym == 'Tab':
                # Auto-select if only one match
                if student_listbox.size() == 1:
                    on_student_select()
            elif event.keysym in ['Up', 'Down']:
                # Allow normal listbox navigation
                pass
            else:
                # For other keys, let the entry handle them
                return
        
        def on_student_focus_in(event):
            # Show all students when entry gets focus
            filter_students()
        
        def on_student_focus_out(event):
            # Hide listbox when entry loses focus (with delay)
            dialog.after(150, lambda: student_listbox.grid_remove())
        
        # Bind events
        student_entry.bind('<KeyRelease>', lambda e: filter_students())
        student_entry.bind('<KeyPress>', on_student_key_press)
        student_entry.bind('<FocusIn>', on_student_focus_in)
        student_entry.bind('<FocusOut>', on_student_focus_out)
        student_listbox.bind('<Button-1>', on_student_click)
        student_listbox.bind('<Double-Button-1>', on_student_select)
        student_listbox.bind('<Return>', on_student_select)
        student_listbox.bind('<KeyPress>', on_student_key_press)
        
        # Validation and submission function
        def validate_and_submit():
            # Validate student selection
            if not student_var.get():
                tk.messagebox.showerror("Validation Error", "Please select a student.")
                return
            
            # Validate equipment selection
            if not equipment_var.get():
                tk.messagebox.showerror("Validation Error", "Please select equipment.")
                return
            
            # Validate quantity
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid quantity (positive integer).")
                return
            
            # Validate amount (should be 0 for "Not Paid")
            try:
                amount = float(amount_var.get())
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid amount (number >= 0).")
                return
            
            # Extract IDs from dropdown selections
            # Find student ID by matching the selected name
            selected_student_name = student_var.get()
            student_id = None
            for student in self.student_data:
                if student['name'] == selected_student_name:
                    student_id = student['id']
                    break
            
            if student_id is None:
                tk.messagebox.showerror("Validation Error", "Selected student not found.")
                return
            
            # Find equipment ID by matching the selected description
            selected_equipment_description = equipment_var.get()
            equipment_id = None
            for equipment in self.equipment_data:
                if equipment['description'] == selected_equipment_description:
                    equipment_id = equipment['id']
                    break
            
            if equipment_id is None:
                tk.messagebox.showerror("Validation Error", "Selected equipment not found.")
                return
            
            try:
                # Call the stored procedure with paid_bool=0 and paydate=null
                db.sp_insert_club_equipment_payment(student_id, equipment_id, quantity, amount, 0, None)
                tk.messagebox.showinfo("Success", "Equipment received (not paid) recorded successfully!")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to record equipment: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def paid_not_received_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Paid, Not Received - Equipment Payment")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student entry with dynamic filtering
        tk.Label(main_frame, text="Student:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        student_var = tk.StringVar()
        student_entry = tk.Entry(main_frame, textvariable=student_var, width=33)
        student_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Create listbox for student selection
        student_listbox = tk.Listbox(main_frame, height=6, width=33)
        student_listbox.grid(row=0, column=1, sticky='w', pady=(30, 10))
        student_listbox.grid_remove()  # Hide initially
        
        # Store student data for filtering
        self.student_data = []
        # Store equipment data for ID lookup
        self.equipment_data = []
        
        # Equipment dropdown (optional)
        tk.Label(main_frame, text="Equipment (optional):").grid(row=1, column=0, sticky='w', pady=(0, 10))
        equipment_var = tk.StringVar()
        equipment_dropdown = ttk.Combobox(main_frame, textvariable=equipment_var, state="readonly", width=30)
        equipment_dropdown.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Quantity entry
        tk.Label(main_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(main_frame, textvariable=quantity_var, width=33)
        quantity_entry.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Amount entry (defaults to 50 for "Paid, Not Received")
        tk.Label(main_frame, text="Amount($):").grid(row=3, column=0, sticky='w', pady=(0, 10))
        amount_var = tk.StringVar(value="50")
        amount_entry = tk.Entry(main_frame, textvariable=amount_var, width=33)
        amount_entry.grid(row=3, column=1, sticky='w', pady=(0, 10))
        
        # Load data into dropdowns
        try:
            students_df = db.get_all_students_for_dropdown()
            # Store student data with ID for backend use
            self.student_data = [{'id': row['id'], 'name': row['name']} for _, row in students_df.iterrows()]
            # Set initial values (just names for display)
            student_names = [student['name'] for student in self.student_data]
            # Populate the listbox initially
            for student_name in student_names:
                student_listbox.insert(tk.END, student_name)
            
            equipment_df = db.get_all_equipment_for_dropdown()
            # Store equipment data with ID for backend use
            self.equipment_data = [{'id': row['id'], 'description': row['item_description']} for _, row in equipment_df.iterrows()]
            # Set initial values (just descriptions for display)
            equipment_descriptions = [equipment['description'] for equipment in self.equipment_data]
            equipment_dropdown['values'] = equipment_descriptions
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            dialog.destroy()
            return
        
        # Add filtering functionality to student entry
        def filter_students():
            # Get the current text in the entry
            typed_text = student_var.get().lower()
            
            # Clear the listbox
            student_listbox.delete(0, tk.END)
            
            # Filter students based on typed text
            if typed_text:
                filtered_students = [student['name'] for student in self.student_data 
                                   if typed_text in student['name'].lower()]
            else:
                filtered_students = [student['name'] for student in self.student_data]
            
            # Add filtered students to listbox
            for student_name in filtered_students:
                student_listbox.insert(tk.END, student_name)
            
            # Show listbox if there are results
            if filtered_students:
                student_listbox.grid()
                # Auto-select if only one match
                if len(filtered_students) == 1:
                    student_listbox.selection_set(0)
            else:
                student_listbox.grid_remove()
        
        def on_student_select(event=None):
            # When a student is selected from listbox
            selection = student_listbox.curselection()
            if selection:
                selected_name = student_listbox.get(selection[0])
                student_var.set(selected_name)
                student_listbox.grid_remove()
        
        def on_student_click(event):
            # Single-click selection
            on_student_select()
        
        def on_student_key_press(event):
            # Handle keyboard navigation
            if event.keysym == 'Return':
                on_student_select()
            elif event.keysym == 'Escape':
                student_listbox.grid_remove()
            elif event.keysym == 'Tab':
                # Auto-select if only one match
                if student_listbox.size() == 1:
                    on_student_select()
            elif event.keysym in ['Up', 'Down']:
                # Allow normal listbox navigation
                pass
            else:
                # For other keys, let the entry handle them
                return
        
        def on_student_focus_in(event):
            # Show all students when entry gets focus
            filter_students()
        
        def on_student_focus_out(event):
            # Hide listbox when entry loses focus (with delay)
            dialog.after(150, lambda: student_listbox.grid_remove())
        
        # Bind events
        student_entry.bind('<KeyRelease>', lambda e: filter_students())
        student_entry.bind('<KeyPress>', on_student_key_press)
        student_entry.bind('<FocusIn>', on_student_focus_in)
        student_entry.bind('<FocusOut>', on_student_focus_out)
        student_listbox.bind('<Button-1>', on_student_click)
        student_listbox.bind('<Double-Button-1>', on_student_select)
        student_listbox.bind('<Return>', on_student_select)
        student_listbox.bind('<KeyPress>', on_student_key_press)
        
        # Validation and submission function
        def validate_and_submit():
            # Validate student selection
            if not student_var.get():
                tk.messagebox.showerror("Validation Error", "Please select a student.")
                return
            
            # Equipment selection is optional for "Paid, Not Received"
            # No validation needed - will pass null if not selected
            
            # Validate quantity
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid quantity (positive integer).")
                return
            
            # Validate amount (defaults to 50 for "Paid, Not Received")
            try:
                amount = float(amount_var.get())
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid amount (number >= 0).")
                return
            
            # Extract IDs from dropdown selections
            # Find student ID by matching the selected name
            selected_student_name = student_var.get()
            student_id = None
            for student in self.student_data:
                if student['name'] == selected_student_name:
                    student_id = student['id']
                    break
            
            if student_id is None:
                tk.messagebox.showerror("Validation Error", "Selected student not found.")
                return
            
            # Find equipment ID by matching the selected description (optional)
            selected_equipment_description = equipment_var.get()
            equipment_id = None
            if selected_equipment_description:  # Only look up if equipment is selected
                for equipment in self.equipment_data:
                    if equipment['description'] == selected_equipment_description:
                        equipment_id = equipment['id']
                        break
            
            try:
                # Call the stored procedure with paid_bool=1 and paydate=now()
                from datetime import datetime
                paydate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Pass null for equipment_id if no equipment selected
                if equipment_id is None:
                    db.sp_insert_club_equipment_payment(student_id, None, quantity, amount, 1, paydate)
                else:
                    db.sp_insert_club_equipment_payment(student_id, equipment_id, quantity, amount, 1, paydate)
                tk.messagebox.showinfo("Success", "Equipment payment (not received) recorded successfully!")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to record payment: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def belt_testing_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Belt, Testing - Equipment Payment")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student entry with dynamic filtering
        tk.Label(main_frame, text="Student:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        student_var = tk.StringVar()
        student_entry = tk.Entry(main_frame, textvariable=student_var, width=33)
        student_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Create listbox for student selection
        student_listbox = tk.Listbox(main_frame, height=6, width=33)
        student_listbox.grid(row=0, column=1, sticky='w', pady=(30, 10))
        student_listbox.grid_remove()  # Hide initially
        
        # Store student data for filtering
        self.student_data = []
        # Store equipment data for ID lookup
        self.equipment_data = []
        
        # Equipment dropdown (belt items only)
        tk.Label(main_frame, text="Belt Equipment:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        equipment_var = tk.StringVar()
        equipment_dropdown = ttk.Combobox(main_frame, textvariable=equipment_var, state="readonly", width=30)
        equipment_dropdown.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Quantity entry
        tk.Label(main_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(main_frame, textvariable=quantity_var, width=33)
        quantity_entry.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Amount entry (defaults to 0 for "Belt, Testing")
        tk.Label(main_frame, text="Amount($):").grid(row=3, column=0, sticky='w', pady=(0, 10))
        amount_var = tk.StringVar(value="0")
        amount_entry = tk.Entry(main_frame, textvariable=amount_var, width=33)
        amount_entry.grid(row=3, column=1, sticky='w', pady=(0, 10))
        
        # Load data into dropdowns
        try:
            students_df = db.get_all_students_for_dropdown()
            # Store student data with ID for backend use
            self.student_data = [{'id': row['id'], 'name': row['name']} for _, row in students_df.iterrows()]
            # Set initial values (just names for display)
            student_names = [student['name'] for student in self.student_data]
            # Populate the listbox initially
            for student_name in student_names:
                student_listbox.insert(tk.END, student_name)
            
            # Load belt equipment only
            equipment_df = db.get_belt_equipment_for_dropdown()
            # Store equipment data with ID for backend use
            self.equipment_data = [{'id': row['id'], 'description': row['item_description']} for _, row in equipment_df.iterrows()]
            # Set initial values (just descriptions for display)
            equipment_descriptions = [equipment['description'] for equipment in self.equipment_data]
            equipment_dropdown['values'] = equipment_descriptions
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            dialog.destroy()
            return
        
        # Add filtering functionality to student entry
        def filter_students():
            # Get the current text in the entry
            typed_text = student_var.get().lower()
            
            # Clear the listbox
            student_listbox.delete(0, tk.END)
            
            # Filter students based on typed text
            if typed_text:
                filtered_students = [student['name'] for student in self.student_data 
                                   if typed_text in student['name'].lower()]
            else:
                filtered_students = [student['name'] for student in self.student_data]
            
            # Add filtered students to listbox
            for student_name in filtered_students:
                student_listbox.insert(tk.END, student_name)
            
            # Show listbox if there are results
            if filtered_students:
                student_listbox.grid()
                # Auto-select if only one match
                if len(filtered_students) == 1:
                    student_listbox.selection_set(0)
            else:
                student_listbox.grid_remove()
        
        def on_student_select(event=None):
            # When a student is selected from listbox
            selection = student_listbox.curselection()
            if selection:
                selected_name = student_listbox.get(selection[0])
                student_var.set(selected_name)
                student_listbox.grid_remove()
        
        def on_student_click(event):
            # Single-click selection
            on_student_select()
        
        def on_student_key_press(event):
            # Handle keyboard navigation
            if event.keysym == 'Return':
                on_student_select()
            elif event.keysym == 'Escape':
                student_listbox.grid_remove()
            elif event.keysym == 'Tab':
                # Auto-select if only one match
                if student_listbox.size() == 1:
                    on_student_select()
            elif event.keysym in ['Up', 'Down']:
                # Allow normal listbox navigation
                pass
            else:
                # For other keys, let the entry handle them
                return
        
        def on_student_focus_in(event):
            # Show all students when entry gets focus
            filter_students()
        
        def on_student_focus_out(event):
            # Hide listbox when entry loses focus (with delay)
            dialog.after(150, lambda: student_listbox.grid_remove())
        
        # Bind events
        student_entry.bind('<KeyRelease>', lambda e: filter_students())
        student_entry.bind('<KeyPress>', on_student_key_press)
        student_entry.bind('<FocusIn>', on_student_focus_in)
        student_entry.bind('<FocusOut>', on_student_focus_out)
        student_listbox.bind('<Button-1>', on_student_click)
        student_listbox.bind('<Double-Button-1>', on_student_select)
        student_listbox.bind('<Return>', on_student_select)
        student_listbox.bind('<KeyPress>', on_student_key_press)
        
        # Validation and submission function
        def validate_and_submit():
            # Validate student selection
            if not student_var.get():
                tk.messagebox.showerror("Validation Error", "Please select a student.")
                return
            
            # Validate equipment selection
            if not equipment_var.get():
                tk.messagebox.showerror("Validation Error", "Please select belt equipment.")
                return
            
            # Validate quantity
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid quantity (positive integer).")
                return
            
            # Validate amount (defaults to 0 for "Belt, Testing")
            try:
                amount = float(amount_var.get())
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid amount (number >= 0).")
                return
            
            # Extract IDs from dropdown selections
            # Find student ID by matching the selected name
            selected_student_name = student_var.get()
            student_id = None
            for student in self.student_data:
                if student['name'] == selected_student_name:
                    student_id = student['id']
                    break
            
            if student_id is None:
                tk.messagebox.showerror("Validation Error", "Selected student not found.")
                return
            
            # Find equipment ID by matching the selected description
            selected_equipment_description = equipment_var.get()
            equipment_id = None
            for equipment in self.equipment_data:
                if equipment['description'] == selected_equipment_description:
                    equipment_id = equipment['id']
                    break
            
            if equipment_id is None:
                tk.messagebox.showerror("Validation Error", "Selected belt equipment not found.")
                return
            
            try:
                # Call the stored procedure with paid_bool=1 and paydate=now()
                from datetime import datetime
                paydate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.sp_insert_club_equipment_payment(student_id, equipment_id, quantity, amount, 1, paydate)
                tk.messagebox.showinfo("Success", "Belt testing payment recorded successfully!")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to record payment: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def setup_equipment_context_menu(self):
        # Create context menu for equipment treeview
        self.equipment_context_menu = tk.Menu(self, tearoff=0)
        self.equipment_context_menu.add_command(label="Add Payment", command=self.add_payment_dialog)
        self.equipment_context_menu.add_command(label="Add Item", command=self.add_item_dialog)
        
        # Bind right-click event to treeview
        self.my_tree_equipment.bind("<Button-3>", self.show_equipment_context_menu)
    def show_equipment_context_menu(self, event):
        # Only show context menu if we're in the transactions view
        if hasattr(self, 'current_equipment_view') and self.current_equipment_view == 'transactions':
            # Get the item under the cursor
            item = self.my_tree_equipment.identify_row(event.y)
            if item:
                # Select the item and show context menu
                self.my_tree_equipment.selection_set(item)
                self.selected_transaction_id = self.get_transaction_id_from_selection()
                if self.selected_transaction_id:
                    self.equipment_context_menu.post(event.x_root, event.y_root)
    def get_transaction_id_from_selection(self):
        # Get the selected item
        selection = self.my_tree_equipment.selection()
        if not selection:
            return None
        
        # Get the values from the selected row
        item = selection[0]
        values = self.my_tree_equipment.item(item, 'values')
        
        # For transactions view, the ID is now in the first column (index 0)
        # The transactions view shows: id, name, item_id, qty, amount_paid, pay_date
        if len(values) > 0:
            try:
                # Get the ID from the first column
                return int(values[0])
            except (ValueError, IndexError):
                return None
        return None
    def add_payment_dialog(self):
        if not hasattr(self, 'selected_transaction_id') or not self.selected_transaction_id:
            tk.messagebox.showerror("Error", "No transaction selected.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Add Payment")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Amount entry
        tk.Label(main_frame, text="Amount($):").grid(row=0, column=0, sticky='w', pady=(0, 10))
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(main_frame, textvariable=amount_var, width=20)
        amount_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Validation and submission function
        def validate_and_submit():
            try:
                amount = float(amount_var.get())
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
            except ValueError:
                tk.messagebox.showerror("Validation Error", "Please enter a valid amount (number >= 0).")
                return
            
            try:
                # Update the transaction with payment
                db.update_transaction_payment(self.selected_transaction_id, amount)
                tk.messagebox.showinfo("Success", "Payment added successfully!")
                dialog.destroy()
                # Refresh the transactions view
                self.view_transactions_equipment()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to add payment: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def add_item_dialog(self):
        if not hasattr(self, 'selected_transaction_id') or not self.selected_transaction_id:
            tk.messagebox.showerror("Error", "No transaction selected.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Add Item")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog.transient(self)
        dialog.grab_set()
        
        # Calculate center position
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Equipment dropdown
        tk.Label(main_frame, text="Equipment:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        equipment_var = tk.StringVar()
        equipment_dropdown = ttk.Combobox(main_frame, textvariable=equipment_var, state="readonly", width=30)
        equipment_dropdown.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Store equipment data for ID lookup
        self.equipment_data = []
        
        # Load equipment data
        try:
            equipment_df = db.get_all_equipment_for_dropdown()
            # Store equipment data with ID for backend use
            self.equipment_data = [{'id': row['id'], 'description': row['item_description']} for _, row in equipment_df.iterrows()]
            # Set initial values (just descriptions for display)
            equipment_descriptions = [equipment['description'] for equipment in self.equipment_data]
            equipment_dropdown['values'] = equipment_descriptions
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load equipment data: {str(e)}")
            dialog.destroy()
            return
        
        # Validation and submission function
        def validate_and_submit():
            if not equipment_var.get():
                tk.messagebox.showerror("Validation Error", "Please select equipment.")
                return
            
            # Find equipment ID by matching the selected description
            selected_equipment_description = equipment_var.get()
            equipment_id = None
            for equipment in self.equipment_data:
                if equipment['description'] == selected_equipment_description:
                    equipment_id = equipment['id']
                    break
            
            if equipment_id is None:
                tk.messagebox.showerror("Validation Error", "Selected equipment not found.")
                return
            
            try:
                # Update the transaction with item
                db.update_transaction_item(self.selected_transaction_id, equipment_id)
                tk.messagebox.showinfo("Success", "Item added successfully!")
                dialog.destroy()
                # Refresh the transactions view
                self.view_transactions_equipment()
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Failed to add item: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        # Confirm button
        confirm_button = tk.Button(button_frame, text="Confirm", command=validate_and_submit, width=10)
        confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10)
        cancel_button.pack(side=tk.LEFT)
    def view_instructors_equipment(self):
        df = db.sp_view_instructors()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_all_inc_equipment(self):
        df = db.sp_all_income()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_all_exp_equipment(self):
        df = db.sp_all_expenses()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_all_teaching_hours_equipment(self):
        df = db.sp_all_teaching_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_all_rental_hours_equipment(self):
        df = db.sp_all_rental_hours()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_projections_equipment(self):
        df = db.sp_projections()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)
    def view_summary_equipment(self):
        df = db.sp_club_equipment_data_v2()
        print(df)
        self.refresh_datagrid(self.my_tree_equipment, df, self.right_frame_tab5)


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

        tab5 = ttk.Frame(self.nb)
        self.nb.add(tab5, text='PMA Equipment')
        self.tab_frames.append(tab5)

        tab5.grid_rowconfigure(0, weight=1)
        tab5.grid_columnconfigure(0, weight=1)
        tab5.grid_columnconfigure(1, weight=5)
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

        ## tab5 ##
        self.left_frame_tab5 = tk.Frame(self.tab_frames[4])
        self.left_frame_tab5.grid(row=0, column=0, sticky="nsew")

        self.right_frame_tab5 = tk.Frame(self.tab_frames[4])
        self.right_frame_tab5.grid(row=0, column=1, sticky="nsew")

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

        # Use populate_treeview for initial population to ensure auto-resize
        self.populate_treeview(treeview, df)

        treeview.place(x=1, y=30, width=880, height=650)
        x_scrollbar.place(x=0, y=675, width=880, height=20, anchor='nw')
        y_scrollbar.place(x=880, y=30, width=20, height=650, anchor='nw')

        if tab == self.right_frame_tab1:
            treeview.bind("<Button-3>", self.show_right_click_menu)
    def refresh_datagrid_with_coloring(self, treeview:ttk.Treeview, df:pd.DataFrame, tab:tk.Frame, original_df:pd.DataFrame = None):
        treeview.delete(*treeview.get_children())
        treeview['show'] = 'headings'

        x_scrollbar = ttk.Scrollbar(tab, orient="horizontal")
        y_scrollbar = ttk.Scrollbar(tab, orient="vertical")
        x_scrollbar.configure(command=treeview.xview)
        y_scrollbar.configure(command=treeview.yview)

        treeview.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        columns = tuple(df.columns.tolist())
        df_rows = df.to_numpy().tolist()
        treeview['columns'] = columns

        column_sort_order = {column: False for column in columns}

        def sort_treeview(column):
            nonlocal column_sort_order
            column_sort_order[column] = not column_sort_order[column]
            df.sort_values(by=column, ascending=column_sort_order[column], inplace=True)
            # Also sort the original dataframe to maintain alignment
            if original_df is not None:
                original_df.sort_values(by=column, ascending=column_sort_order[column], inplace=True)
            self.populate_treeview_with_coloring(treeview, df, original_df)

        for column in columns:
            treeview.heading(column, text=column, anchor='w', command=lambda c=column: sort_treeview(c))
            treeview.column(column, stretch=False, minwidth=25, width=100)

        # Populate with coloring
        self.populate_treeview_with_coloring(treeview, df, original_df)

        treeview.place(x=1, y=30, width=880, height=650)
        x_scrollbar.place(x=0, y=675, width=880, height=20, anchor='nw')
        y_scrollbar.place(x=880, y=30, width=20, height=650, anchor='nw')

        if tab == self.right_frame_tab1:
            treeview.bind("<Button-3>", self.show_right_click_menu)
    def populate_treeview_with_coloring(self, treeview:ttk.Treeview, df:pd.DataFrame, original_df:pd.DataFrame = None):
        # Clear existing items
        treeview.delete(*treeview.get_children())
        
        # Get column names
        columns = df.columns.tolist()
        
        # Check if item_id and pay_date columns exist
        item_id_col = None
        pay_date_col = None
        
        for i, col in enumerate(columns):
            if 'item_id' in col.lower():
                item_id_col = i
            if 'pay_date' in col.lower():
                pay_date_col = i
        
        # Insert rows with coloring
        for index, row in df.iterrows():
            values = row.tolist()
            
            # Check if row should be colored yellow
            should_color_yellow = False
            
            # Use original dataframe for null detection if available
            if original_df is not None and index < len(original_df):
                original_row = original_df.iloc[index]
                
                if item_id_col is not None:
                    item_id_value = original_row.iloc[item_id_col]
                    if pd.isna(item_id_value) or item_id_value is None or item_id_value == '':
                        should_color_yellow = True
                
                if pay_date_col is not None:
                    pay_date_value = original_row.iloc[pay_date_col]
                    if pd.isna(pay_date_value) or pay_date_value is None or pay_date_value == '':
                        should_color_yellow = True
            else:
                # Fallback to using the converted dataframe
                if item_id_col is not None:
                    item_id_value = values[item_id_col]
                    if pd.isna(item_id_value) or item_id_value is None or item_id_value == '' or item_id_value == 0:
                        should_color_yellow = True
                
                if pay_date_col is not None:
                    pay_date_value = values[pay_date_col]
                    if pd.isna(pay_date_value) or pay_date_value is None or pay_date_value == '':
                        should_color_yellow = True
            
            # Insert the row
            item = treeview.insert("", "end", values=values)
            
            # Apply yellow background if needed
            if should_color_yellow:
                treeview.set(item, columns[0], values[0])  # This ensures the item is properly set
                # Apply yellow background to the entire row
                for col in columns:
                    treeview.set(item, col, values[columns.index(col)])
                # Use tag to apply background color
                treeview.item(item, tags=('yellow_row',))
        
        # Configure the tag for yellow background
        treeview.tag_configure('yellow_row', background='yellow')
        
        # Auto-resize columns after populating
        self.auto_resize_columns(treeview)
    def auto_resize_columns(self, treeview:ttk.Treeview):
        """Auto-resize columns to fit content width"""
        for column in treeview['columns']:
            # Get the maximum width needed for this column
            max_width = 0
            
            # Determine if this is an ID, name, or other specific column for more compact sizing
            column_lower = str(column).lower()
            is_id_column = 'id' in column_lower and column_lower != 'item_id'
            is_name_column = 'name' in column_lower
            is_pay_rate_column = 'pay_rate' in column_lower
            is_payment_good_till_column = 'payment_good_till' in column_lower
            is_profile_comment_column = 'profile_comment' in column_lower
            
            # Use different character width and padding for different column types
            if is_id_column:
                char_width = 6  # More compact for ID columns
                padding = 10    # Less padding for ID columns
                min_width = 40  # Smaller minimum for ID columns
            elif is_name_column:
                char_width = 6  # More compact for name columns
                padding = 12    # Less padding for name columns
                min_width = 50  # Smaller minimum for name columns
            elif is_pay_rate_column:
                char_width = 6  # More compact for pay_rate columns
                padding = 10    # Less padding for pay_rate columns
                min_width = 45  # Smaller minimum for pay_rate columns
            elif is_payment_good_till_column:
                char_width = 6  # More compact for payment_good_till columns
                padding = 10    # Less padding for payment_good_till columns
                min_width = 45  # Smaller minimum for payment_good_till columns
            elif is_profile_comment_column:
                char_width = 6  # More compact for profile_comment columns
                padding = 10    # Less padding for profile_comment columns
                min_width = 45  # Smaller minimum for profile_comment columns
            else:
                char_width = 8  # Standard character width
                padding = 20    # Standard padding
                min_width = 50  # Standard minimum width
            
            # Check header width
            header_width = len(str(column)) * char_width
            max_width = max(max_width, header_width)
            
            # Check content width for each row
            for item in treeview.get_children():
                value = treeview.set(item, column)
                if value:
                    content_width = len(str(value)) * char_width
                    max_width = max(max_width, content_width)
            
            # Set final width with appropriate padding
            final_width = max(min_width, max_width + padding)
            
            # Configure the column width
            treeview.column(column, width=final_width)
    def refresh_datagrid_equipment(self, treeview:ttk.Treeview, df:pd.DataFrame, tab:tk.Frame):
        """Refresh datagrid with auto-resize for PMA Equipment tab"""
        treeview.delete(*treeview.get_children())
        treeview['show'] = 'headings'

        x_scrollbar = ttk.Scrollbar(tab, orient="horizontal")
        y_scrollbar = ttk.Scrollbar(tab, orient="vertical")
        x_scrollbar.configure(command=treeview.xview)
        y_scrollbar.configure(command=treeview.yview)

        treeview.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        columns = tuple(df.columns.tolist())
        df_rows = df.to_numpy().tolist()
        treeview['columns'] = columns

        column_sort_order = {column: False for column in columns}

        def sort_treeview(column):
            nonlocal column_sort_order
            column_sort_order[column] = not column_sort_order[column]
            df.sort_values(by=column, ascending=column_sort_order[column], inplace=True)
            self.populate_treeview_equipment(treeview, df)

        for column in columns:
            treeview.heading(column, text=column, anchor='w', command=lambda c=column: sort_treeview(c))
            treeview.column(column, stretch=False, minwidth=25, width=100)

        # Populate the treeview
        self.populate_treeview_equipment(treeview, df)

        treeview.place(x=1, y=30, width=880, height=650)
        x_scrollbar.place(x=0, y=675, width=880, height=20, anchor='nw')
        y_scrollbar.place(x=880, y=30, width=20, height=650, anchor='nw')

        if tab == self.right_frame_tab1:
            treeview.bind("<Button-3>", self.show_right_click_menu)
    def populate_treeview_equipment(self, treeview:ttk.Treeview, df:pd.DataFrame):
        """Populate treeview for PMA Equipment tab"""
        # Clear existing items
        treeview.delete(*treeview.get_children())
        
        # Insert rows
        for index, row in df.iterrows():
            values = row.tolist()
            treeview.insert("", "end", values=values)
        
        # Auto-resize columns after populating
        self.auto_resize_columns(treeview)
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

            email_handler_google.create_email(
                subject="PMA - ", 
                email_from="saoneil@live.com",
                emails_to=[],
                emails_cc=[],
                emails_bcc=email_list,
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
    def toggle_waitlist_right_click(self):
        student_id_list = []
        selected_items = self.my_tree.selection()
        if selected_items:
            records_data = [self.my_tree.item(item, 'values') for item in selected_items]
            for record in records_data:
                student_id_list.append(record[0])

            for id in student_id_list:
                print(id + " - toggle wait_list value")
                db.sp_toggle_trial_or_active(id, 'waitlist')

            messagebox.showinfo("Toggle Active", "Toggled 'Wait List' field for StudentID = " + str(student_id_list))
        else:
            messagebox.showwarning("No Selection", "Please select records to toggle waitlist.")
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
        
        # Auto-resize columns after populating
        self.auto_resize_columns(treeview)
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
                ("ID:", None, "ID4", 17, None, (0, 0)),
                ("Good 'Til (y-m-d):", None, "date_till", 18, None, (0, 0)),
                ("Pay Rate:", None, "pay_rate", 19, None, (0, 0)),
                ("Total:", None, "total", 20, None, (0, 0)),
                ("Calc. Tax:", None, "calc_tax", 21, None, (0, 0)),
                ("PKRT:", None, "club", 22, None, (0, 0)),
                ("E-transfer:", None, "etransfer", 23, None, (0, 0)),
                ("Txn Note:", None, "txn_note", 24, None, (0, 0)),
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
            try:
                existing_student_dropdown['values'] = self.all_students_list_command()
            except:
                existing_student_dropdown['values'] = ["DB Connection Failed"]
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
        def tab5(self):
            datagrid_label = tk.Label(self.right_frame_tab5, text="Result Datagrid", font="verdana 15 bold")
            datagrid_label.pack()

            definition_label = tk.Label(self.left_frame_tab5, text="Control Panel", font='verdana 15 bold')
            definition_label.grid(row=1, column=1, columnspan=2, pady=(0,15))

            # View Students at the top
            view_students_label = tk.Label(self.left_frame_tab5, text="View Students:")
            view_students_label.grid(row=2, column=1, sticky='ne', pady=(0,3))

            view_students_button = tk.Button(self.left_frame_tab5, text="Students", height=1, command=self.view_students_equipment)
            view_students_button.grid(row=2, column=2, sticky='nw', pady=(0,3))

            # Search functionality
            search_section = [
                ("Database Search:", "Search", 3, self.search_grid_equipment_command, (0, 10)),
                ("First Name:", None, 4, None, None),
                ("Last Name:", None, 5, None, None),
                ("Email:", None, 6, None, (0,25))
            ]
            for label_text, button_text, row, command, pady in search_section:
                label = tk.Label(self.left_frame_tab5, text=label_text)
                label.grid(row=row, column=1, sticky='ne', pady=pady)

                if button_text:
                    button = tk.Button(self.left_frame_tab5, text=button_text, command=command)
                    button.grid(row=row, column=2, sticky='nw', pady=pady)
                else:
                    entry = tk.Entry(self.left_frame_tab5, width=10)
                    entry.grid(row=row, column=2, sticky='nw', pady=pady)

                    self.entry_widgets_search_equipment[label_text] = entry

            # Equipment functionality with more spacing
            equipment_section = [
                ("Equipment List:", "Equipment", self.view_equipment_list_equipment, 9, 'ne', (0,3)),
                ("Stock Quantities:", "Stock", self.view_stock_quantities_equipment, 10, 'ne', (0,3)),
                ("Transactions:", "Transactions", self.view_transactions_equipment, 11, 'ne', (0,3))
            ]
            for label_text, button_text, command, row, sticky, pady in equipment_section:
                label = tk.Label(self.left_frame_tab5, text=label_text)
                label.grid(row=row, column=1, sticky=sticky, pady=pady)

                button = tk.Button(self.left_frame_tab5, text=button_text, height=1, command=command)
                button.grid(row=row, column=2, sticky='nw', pady=pady)

            # Add visual spacer between sections
            spacer_label = tk.Label(self.left_frame_tab5, text="", height=2)
            spacer_label.grid(row=13, column=1, columnspan=2, pady=(10, 10))

            # Payment status section with more spacing
            payment_section = [
                ("Received & Paid:", "Received & Paid", self.received_and_paid_dialog, 15, 'ne', (0,3)),
                ("Received, Not Paid:", "Received, Not Paid", self.received_not_paid_dialog, 16, 'ne', (0,3)),
                ("Paid, Not Received:", "Paid, Not Received", self.paid_not_received_dialog, 17, 'ne', (0,3)),
                ("Belt, Testing:", "Belt, Testing", self.belt_testing_dialog, 18, 'ne', (0,3)),
                ("", "", None, 19, 'ne', (10,0)),  # Spacer
                ("Summary:", "Summary", self.view_summary_equipment, 20, 'ne', (0,3))
            ]
            for label_text, button_text, command, row, sticky, pady in payment_section:
                if command is not None:  # Only create label and button if command exists
                    label = tk.Label(self.left_frame_tab5, text=label_text)
                    label.grid(row=row, column=1, sticky=sticky, pady=pady)

                    button = tk.Button(self.left_frame_tab5, text=button_text, height=1, command=command)
                    button.grid(row=row, column=2, sticky='nw', pady=pady)
                else:  # Create spacer
                    spacer_label = tk.Label(self.left_frame_tab5, text="", height=1)
                    spacer_label.grid(row=row, column=1, columnspan=2, pady=pady)

        tab1(self)
        tab2(self)
        tab3(self)
        tab4(self)
        tab5(self)

        
if __name__ == "__main__":
    app = MyApp()
    ttk.Style().theme_use('default')
    app.mainloop()