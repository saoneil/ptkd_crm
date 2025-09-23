import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinter import simpledialog
import numpy as np
from datetime import datetime, timedelta
import db, email_handler_google
from tkinter import font


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
        
        # Calendar dialog function
        self.calendar_dialog = None
        # Save button reference for color changes
        self.save_button = None
        # Store original values for comparison
        self.original_student_values = {}
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
        print(f"Selected value: {selected_value}")  # Debug print
        
        # Find student ID from the selected name
        student_id = None
        if hasattr(self, 'existing_student_data') and self.existing_student_data:
            print(f"Available students: {len(self.existing_student_data)}")  # Debug print
            for student in self.existing_student_data:
                if student['name'] == selected_value:
                    student_id = student['id']
                    print(f"Found student ID: {student_id}")  # Debug print
                    break
        else:
            print("No student data available")  # Debug print
        
        if not student_id:
            print("No student ID found, returning")  # Debug print
            return
            
        self.student_id = student_id
        df = db.sp_view_student_by_id(self.student_id)
        print(f"Loaded student data for ID: {student_id}")  # Debug print
        if selected_value:
            # Helper function to format values (replace None with empty string)
            def format_value(value):
                if pd.isna(value) or value is None or str(value) == 'None':
                    return ""
                return str(value)
            
            # Helper function to format date values specifically
            def format_date_value(value):
                if pd.isna(value) or value is None or str(value) == 'None':
                    return ""
                # Convert datetime.date to string in YYYY-MM-DD format
                if hasattr(value, 'strftime'):
                    return value.strftime('%Y-%m-%d')
                return str(value)
            
            
            student_info = {
                            "First Name:": format_value(df.loc[0,'first_name']),
                            "Last Name:": format_value(df.loc[0,'last_name']),
                            "DOB (yyyy-mm-dd):": format_date_value(df.loc[0,'dob']),
                            "DOB-approx:": str(df.loc[0,'dob_approx']) if not pd.isna(df.loc[0,'dob_approx']) else "0",
                            "Start Date (yyyy-mm-dd):": format_date_value(df.loc[0,'start_date']),
                            "Active:": str(df.loc[0,'active']) if not pd.isna(df.loc[0,'active']) else "0",
                            "Trial Student:": str(df.loc[0,'trial_student']) if not pd.isna(df.loc[0,'trial_student']) else "0",
                            "Wait List:": str(df.loc[0,'wait_list']) if not pd.isna(df.loc[0,'wait_list']) else "0",
                            "Current Rank:": format_value(df.loc[0,'current_rank']), 
                            "Does Karate:": str(df.loc[0,'does_karate']) if not pd.isna(df.loc[0,'does_karate']) else "0", 
                            "TKD Comp Interest:": str(df.loc[0,'tkd_competition_interest_level']) if not pd.isna(df.loc[0,'tkd_competition_interest_level']) else "1", 
                            "KRT Comp Interest:": str(df.loc[0,'krt_competition_interest_level']) if not pd.isna(df.loc[0,'krt_competition_interest_level']) else "1", 
                            "Signed Waiver:": str(df.loc[0,'signed_waiver']) if not pd.isna(df.loc[0,'signed_waiver']) else "0", 
                            "Aurora Member:": str(df.loc[0,'aurora_member']) if not pd.isna(df.loc[0,'aurora_member']) else "0", 
                            "Profile Comment:": format_value(df.loc[0,'profile_comment']), 
                            "Email 1:": format_value(df.loc[0,'email1']), 
                            "Email 2:": format_value(df.loc[0,'email2']), 
                            "Email 3:": format_value(df.loc[0,'email3']), 
                            "Phone 1:": format_value(df.loc[0,'phone1']), 
                            "Phone 2:": format_value(df.loc[0,'phone2']), 
                            "Phone 3:": format_value(df.loc[0,'phone3']), 
                            "Payment Good Till:": format_date_value(df.loc[0,'payment_good_till']), 
                            "Pay Rate:": str(df.loc[0,'pay_rate']) if not pd.isna(df.loc[0,'pay_rate']) else "0", 
                            "Gender:": format_value(df.loc[0,'gender']), 
                            "YS Test Date:": format_date_value(df.loc[0,'yellow_stripe_testdate']), 
                            "YB Test Date:": format_date_value(df.loc[0,'yellow_belt_testdate']), 
                            "GS Test Date:": format_date_value(df.loc[0,'green_stripe_testdate']), 
                            "GB Test Date:": format_date_value(df.loc[0,'green_belt_testdate']), 
                            "BS Test Date:": format_date_value(df.loc[0,'blue_stripe_testdate']), 
                            "BB Test Date:": format_date_value(df.loc[0,'blue_belt_testdate']), 
                            "RS Test Date:": format_date_value(df.loc[0,'red_stripe_testdate']), 
                            "RB Test Date:": format_date_value(df.loc[0,'red_belt_testdate']), 
                            "BKS Test Date:": format_date_value(df.loc[0,'black_stripe_testdate']),
                            "1st Dan Test Date:": format_date_value(df.loc[0,'1st_dan_testdate']), 
                            "2nd Dan Test Date:": format_date_value(df.loc[0,'2nd_dan_testdate']), 
                            "3rd Dan Test Date:": format_date_value(df.loc[0,'3rd_dan_testdate']), 
                            "4th Dan Test Date:": format_date_value(df.loc[0,'4th_dan_testdate']), 
                            "5th Dan Test Date:": format_date_value(df.loc[0,'5th_dan_testdate']), 
                            "6th Dan Test Date:": format_date_value(df.loc[0,'6th_dan_testdate']), 
                            "7th Dan Test Date:": format_date_value(df.loc[0,'7th_dan_testdate']), 
                            "8th Dan Test Date:": format_date_value(df.loc[0,'8th_dan_testdate']), 
                            "9th Dan Test Date:": format_date_value(df.loc[0,'9th_dan_testdate']), 
                            "Black Belt Intl ID:": str(df.loc[0,'black_belt_international_id']) if not pd.isna(df.loc[0,'black_belt_international_id']) else "", 
                            "Black Belt Number:": format_value(df.loc[0,'black_belt_number']), 
                            "Record Creation:": format_value(df.loc[0,'record_creation_timestamp']), 
                            "Record Update:": format_value(df.loc[0,'record_update_timestamp']), 
                        }

            # Store original values for comparison
            self.original_student_values = {}
            
            # Store the original values from the database
            for field, value in student_info.items():
                self.original_student_values[field] = value

            # Create a clean field mapping system
            field_mapping = {
                "First Name:": (2, 1),
                "Last Name:": (3, 1),
                "Email 1:": (4, 1),
                "Email 2:": (5, 1),
                "Email 3:": (6, 1),
                "Phone 1:": (7, 1),
                "Phone 2:": (8, 1),
                "Phone 3:": (9, 1),
                "Payment Good Till:": (10, 1),
                "Pay Rate:": (11, 1),
                "Start Date (yyyy-mm-dd):": (12, 1),
                "Gender:": (13, 1),
                "DOB (yyyy-mm-dd):": (14, 1),
                "DOB-approx:": (15, 1),
                "Active:": (16, 1),
                "Trial Student:": (17, 1),
                "Wait List:": (18, 1),
                "Does Karate:": (19, 1),
                "Current Rank:": (2, 3),
                "YS Test Date:": (3, 3),
                "YB Test Date:": (4, 3),
                "GS Test Date:": (5, 3),
                "GB Test Date:": (6, 3),
                "BS Test Date:": (7, 3),
                "BB Test Date:": (8, 3),
                "RS Test Date:": (9, 3),
                "RB Test Date:": (10, 3),
                "BKS Test Date:": (11, 3),
                "1st Dan Test Date:": (12, 3),
                "2nd Dan Test Date:": (13, 3),
                "3rd Dan Test Date:": (14, 3),
                "4th Dan Test Date:": (15, 3),
                "5th Dan Test Date:": (16, 3),
                "6th Dan Test Date:": (17, 3),
                "7th Dan Test Date:": (18, 3),
                "8th Dan Test Date:": (19, 3),
                "9th Dan Test Date:": (20, 3),
                "Black Belt Intl ID:": (2, 5),
                "Black Belt Number:": (3, 5),
                "TKD Comp Interest:": (4, 5),
                "KRT Comp Interest:": (5, 5),
                "Signed Waiver:": (6, 5),
                "Aurora Member:": (7, 5),
                "Record Creation:": (8, 5),
                "Record Update:": (9, 5)
            }
            
            # Update widgets using stored widget map first, then grid lookup
            for field, value in student_info.items():
                # Prefer stored widget/variable mapping when available
                if field in self.entry_widgets_existing_student:
                    mapped = self.entry_widgets_existing_student[field]
                    if isinstance(mapped, tk.BooleanVar):
                        mapped.set(value == "1" or value == 1 or value == "True" or value is True)
                        continue
                    if isinstance(mapped, tk.Entry):
                        mapped.delete(0, "end")
                        mapped.insert(0, value)
                        continue
                    # Competition picker stored as Frame -> Entry with attributes
                    if isinstance(mapped, tk.Frame) and field in ["TKD Comp Interest:", "KRT Comp Interest:"]:
                        # Find entry inside
                        for child in mapped.winfo_children():
                            if isinstance(child, tk.Entry):
                                # Set id and display text based on options
                                options = getattr(child, '_comp_options', [])
                                # value is expected to be id as string
                                try:
                                    vid = int(value) if value not in (None, "", "None") else None
                                except Exception:
                                    vid = None
                                display_text = ""
                                if vid is not None:
                                    for oid, otext in options:
                                        if oid == vid:
                                            child._comp_id = vid
                                            display_text = otext
                                            break
                                child.delete(0, tk.END)
                                child.insert(0, display_text)
                                break
                        continue
                    if isinstance(mapped, tk.Frame):
                        # Date field frame containing an Entry
                        for child in mapped.winfo_children():
                            if isinstance(child, tk.Entry):
                                child.delete(0, "end")
                                child.insert(0, value)
                                break
                        continue
                if field in field_mapping:
                    row, col = field_mapping[field]
                    # Find the widget at this grid position
                    widget = None
                    for child in self.top_right_frame_tab2.winfo_children():
                        if hasattr(child, 'grid_info'):
                            info = child.grid_info()
                            if info.get('row') == row and info.get('column') == col + 1:
                                widget = child
                                break
                    
                    if widget:
                        # Handle different widget types
                        if isinstance(widget, tk.Frame):
                            # For date fields wrapped in Frames, find the Entry widget inside
                            entry_widget = None
                            for child in widget.winfo_children():
                                if isinstance(child, tk.Entry):
                                    entry_widget = child
                                    break
                            if entry_widget:
                                entry_widget.delete(0, "end")
                                entry_widget.insert(0, value)
                        elif isinstance(widget, (tk.Entry,)):
                            # Regular Entry widget
                            widget.delete(0, "end")
                            widget.insert(0, value)
                        else:
                            # Non-entry widgets (e.g., Checkbutton) are handled via stored map; skip here
                            pass
            
            # Reset button color when loading new student
            if self.save_button:
                self.save_button.config(bg="SystemButtonFace")
            
            # Suppress extra logging; keep only comparison later
        else:
            # Clear entry widgets if no student is selected
            for widget in self.entry_widgets_existing_student.values():
                if isinstance(widget, tk.BooleanVar):
                    widget.set(False)
                elif isinstance(widget, tk.Checkbutton):
                    widget.deselect()
                elif isinstance(widget, ttk.Combobox):
                    widget.set("")
                elif isinstance(widget, tk.Frame):
                    # For date fields wrapped in Frames, find the Entry widget inside
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry):
                            child.delete(0, "end")
                            break
                else:
                    widget.delete(0, "end")
    def commit_changes_existing_student_command(self):
        # Initialize all variables
        first_name = last_name = email1 = email2 = email3 = phone1 = phone2 = phone3 = ""
        dob = dob_approx = start_date = active = trial_student = wait_list = current_rank = does_karate = 0
        tkd_comp_interest = krt_comp_interest = signed_waiver = aurora_member = 0
        profile_comment = payment_good_till = pay_rate = gender = ""
        ys_testdate = yb_testdate = gs_testdate = gb_testdate = bs_testdate = bb_testdate = rs_testdate = rb_testdate = bks_testdate = "NULL"
        first_dan_testdate = second_dan_testdate = third_dan_testdate = fourth_dan_testdate = fifth_dan_testdate = sixth_dan_testdate = seventh_dan_testdate = eighth_dan_testdate = ninth_dan_testdate = "NULL"
        black_belt_intl_id = "NULL"
        black_belt_number = "NULL"
        
        # Use the same field mapping system for reading values
        field_mapping = {
            "First Name:": (2, 1),
            "Last Name:": (3, 1),
            "Email 1:": (4, 1),
            "Email 2:": (5, 1),
            "Email 3:": (6, 1),
            "Phone 1:": (7, 1),
            "Phone 2:": (8, 1),
            "Phone 3:": (9, 1),
            "Payment Good Till:": (10, 1),
            "Pay Rate:": (11, 1),
            "Start Date (yyyy-mm-dd):": (12, 1),
            "Gender:": (13, 1),
            "DOB (yyyy-mm-dd):": (14, 1),
            "DOB-approx:": (15, 1),
            "Active:": (16, 1),
            "Trial Student:": (17, 1),
            "Wait List:": (18, 1),
            "Does Karate:": (19, 1),
            "Current Rank:": (2, 3),
            "YS Test Date:": (3, 3),
            "YB Test Date:": (4, 3),
            "GS Test Date:": (5, 3),
            "GB Test Date:": (6, 3),
            "BS Test Date:": (7, 3),
            "BB Test Date:": (8, 3),
            "RS Test Date:": (9, 3),
            "RB Test Date:": (10, 3),
            "BKS Test Date:": (11, 3),
            "1st Dan Test Date:": (12, 3),
            "2nd Dan Test Date:": (13, 3),
            "3rd Dan Test Date:": (14, 3),
            "4th Dan Test Date:": (15, 3),
            "5th Dan Test Date:": (16, 3),
            "6th Dan Test Date:": (17, 3),
            "7th Dan Test Date:": (18, 3),
            "8th Dan Test Date:": (19, 3),
            "9th Dan Test Date:": (20, 3),
            "Black Belt Intl ID:": (2, 5),
            "Black Belt Number:": (3, 5),
            "TKD Comp Interest:": (4, 5),
            "KRT Comp Interest:": (5, 5),
            "Signed Waiver:": (6, 5),
            "Aurora Member:": (7, 5),
            "Record Creation:": (8, 5),
            "Record Update:": (9, 5)
        }
        
        # Read values preferring stored widget/variable map, then grid lookup
        for field, (row, col) in field_mapping.items():
            data = ""
            if field in self.entry_widgets_existing_student:
                mapped = self.entry_widgets_existing_student[field]
                if isinstance(mapped, tk.BooleanVar):
                    data = 1 if mapped.get() else 0
                elif isinstance(mapped, tk.Entry):
                    data = mapped.get()
                elif isinstance(mapped, ttk.Combobox):
                    # For competition interest dropdowns, extract the ID from the selection
                    if field in ["TKD Comp Interest:", "KRT Comp Interest:"]:
                        selection = mapped.get()
                        if selection and " - " in selection:
                            data = selection.split(" - ")[0]  # Extract ID part
                        else:
                            # If no selection and original value exists, use it; otherwise default to 1
                            original_val = self.original_student_values.get(field)
                            data = str(original_val) if original_val not in (None, "", "None") else "1"
                    else:
                        data = mapped.get()
                elif isinstance(mapped, tk.Frame):
                    for child in mapped.winfo_children():
                        if isinstance(child, tk.Entry):
                            if field in ["TKD Comp Interest:", "KRT Comp Interest:"]:
                                # Prefer stored selected id
                                sel_id = getattr(child, '_comp_id', None)
                                if sel_id is not None:
                                    data = str(sel_id)
                                else:
                                    # Fall back to original value if no selection
                                    original_val = self.original_student_values.get(field)
                                    data = str(original_val) if original_val not in (None, "", "None") else "1"
                            else:
                                data = child.get()
                            break
                else:
                    # Fallback to grid lookup for any not in map
                    pass
            if data == "":
                # Fallback: grid lookup
                widget = None
                for child in self.top_right_frame_tab2.winfo_children():
                    if hasattr(child, 'grid_info'):
                        info = child.grid_info()
                        if info.get('row') == row and info.get('column') == col + 1:
                            widget = child
                            break
                if widget:
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Entry):
                                data = child.get()
                                break
                    elif isinstance(widget, tk.Entry):
                        data = widget.get()
                
            if field == "First Name:":
                first_name = data
            elif field == "Last Name:":
                last_name = data
            elif field == "DOB (yyyy-mm-dd):":
                if data == "None" or data == "" or data is None:
                    dob = "NULL"
                else:
                    # Validate YYYY-MM-DD; if invalid, treat as NULL to avoid MySQL errors
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        dob = f"'{data}'"
                    except Exception:
                        dob = "NULL"
            elif field == "DOB-approx:":
                dob_approx = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Start Date (yyyy-mm-dd):":
                if data == "None" or data == "" or data is None:
                    start_date = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        start_date = f"'{data}'"
                    except Exception:
                        start_date = "NULL"
            elif field == "Active:":
                active = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Trial Student:":
                trial_student = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Wait List:":
                wait_list = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Current Rank:":
                current_rank = data
            elif field == "Does Karate:":
                does_karate = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "TKD Comp Interest:":
                if data == "" or data is None:
                    tkd_comp_interest = 1
                else:
                    try:
                        tkd_comp_interest = int(data)
                    except ValueError:
                        tkd_comp_interest = 1
            elif field == "KRT Comp Interest:":
                if data == "" or data is None:
                    krt_comp_interest = 1
                else:
                    try:
                        krt_comp_interest = int(data)
                    except ValueError:
                        krt_comp_interest = 1
            elif field == "Aurora Member:":
                aurora_member = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Payment Good Till:":
                if data == "None" or data == "" or data is None:
                    payment_good_till = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        payment_good_till = f"'{data}'"
                    except Exception:
                        payment_good_till = "NULL"
            elif field == "Pay Rate:":
                if data == "" or data is None:
                    pay_rate = 0
                else:
                    try:
                        pay_rate = int(data)
                    except ValueError:
                        pay_rate = 0
            elif field == "Gender:":
                gender = data
            elif field == "Signed Waiver:":
                signed_waiver = 1 if (data == "1" or data == 1 or data == "True" or data is True) else 0
            elif field == "Profile Comment:":
                # Pass plain string; DB layer applies quoting. Empty -> empty string
                profile_comment = "" if (data is None or data == "") else data
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
                if data == "None" or data == "" or data is None:
                    ys_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        ys_testdate = f"'{data}'"
                    except Exception:
                        ys_testdate = "NULL"
            elif field == "YB Test Date:":
                if data == "None" or data == "" or data is None:
                    yb_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        yb_testdate = f"'{data}'"
                    except Exception:
                        yb_testdate = "NULL"
            elif field == "GS Test Date:":
                if data == "None" or data == "" or data is None:
                    gs_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        gs_testdate = f"'{data}'"
                    except Exception:
                        gs_testdate = "NULL"
            elif field == "GB Test Date:":
                if data == "None" or data == "" or data is None:
                    gb_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        gb_testdate = f"'{data}'"
                    except Exception:
                        gb_testdate = "NULL"
            elif field == "BS Test Date:":
                if data == "None" or data == "" or data is None:
                    bs_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        bs_testdate = f"'{data}'"
                    except Exception:
                        bs_testdate = "NULL"
            elif field == "BB Test Date:":
                if data == "None" or data == "" or data is None:
                    bb_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        bb_testdate = f"'{data}'"
                    except Exception:
                        bb_testdate = "NULL"
            elif field == "RS Test Date:":
                if data == "None" or data == "" or data is None:
                    rs_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        rs_testdate = f"'{data}'"
                    except Exception:
                        rs_testdate = "NULL"
            elif field == "RB Test Date:":
                if data == "None" or data == "" or data is None:
                    rb_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        rb_testdate = f"'{data}'"
                    except Exception:
                        rb_testdate = "NULL"
            elif field == "BKS Test Date:":
                if data == "None" or data == "" or data is None:
                    bks_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        bks_testdate = f"'{data}'"
                    except Exception:
                        bks_testdate = "NULL"
            elif field == "1st Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    first_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        first_dan_testdate = f"'{data}'"
                    except Exception:
                        first_dan_testdate = "NULL"
            elif field == "2nd Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    second_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        second_dan_testdate = f"'{data}'"
                    except Exception:
                        second_dan_testdate = "NULL"
            elif field == "3rd Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    third_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        third_dan_testdate = f"'{data}'"
                    except Exception:
                        third_dan_testdate = "NULL"
            elif field == "4th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    fourth_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        fourth_dan_testdate = f"'{data}'"
                    except Exception:
                        fourth_dan_testdate = "NULL"
            elif field == "5th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    fifth_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        fifth_dan_testdate = f"'{data}'"
                    except Exception:
                        fifth_dan_testdate = "NULL"
            elif field == "6th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    sixth_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        sixth_dan_testdate = f"'{data}'"
                    except Exception:
                        sixth_dan_testdate = "NULL"
            elif field == "7th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    seventh_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        seventh_dan_testdate = f"'{data}'"
                    except Exception:
                        seventh_dan_testdate = "NULL"
            elif field == "8th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    eighth_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        eighth_dan_testdate = f"'{data}'"
                    except Exception:
                        eighth_dan_testdate = "NULL"
            elif field == "9th Dan Test Date:":
                if data == "None" or data == "" or data is None:
                    ninth_dan_testdate = "NULL"
                else:
                    # Validate YYYY-MM-DD format
                    try:
                        from datetime import datetime as _dt
                        _dt.strptime(data, "%Y-%m-%d")
                        ninth_dan_testdate = f"'{data}'"
                    except Exception:
                        ninth_dan_testdate = "NULL"
            elif field == "Black Belt Intl ID:":
                if data == "None" or data == "" or data is None:
                    black_belt_intl_id = "NULL"
                else:
                    try:
                        black_belt_intl_id = int(data)
                    except ValueError:
                        black_belt_intl_id = "NULL"
            elif field == "Black Belt Number:":
                if data == "None" or data == "" or data is None:
                    black_belt_number = "NULL"
                else:
                    black_belt_number = f"'{data}'"

            # Do not clear widgets before save; keep user inputs intact
        # Print before/after comparison
        print("\n=== BEFORE/AFTER COMPARISON ===")
        comparison_fields = [
            ("First Name:", first_name),
            ("Last Name:", last_name),
            ("Email 1:", email1),
            ("Email 2:", email2),
            ("Email 3:", email3),
            ("Phone 1:", phone1),
            ("Phone 2:", phone2),
            ("Phone 3:", phone3),
            ("DOB (yyyy-mm-dd):", dob),
            ("DOB-approx:", dob_approx),
            ("Start Date (yyyy-mm-dd):", start_date),
            ("Active:", active),
            ("Trial Student:", trial_student),
            ("Wait List:", wait_list),
            ("Current Rank:", current_rank),
            ("Does Karate:", does_karate),
            ("TKD Comp Interest:", tkd_comp_interest),
            ("KRT Comp Interest:", krt_comp_interest),
            ("Signed Waiver:", signed_waiver),
            ("Aurora Member:", aurora_member),
            ("Profile Comment:", profile_comment),
            ("Payment Good Till:", payment_good_till),
            ("Pay Rate:", pay_rate),
            ("Gender:", gender)
        ]
        
        # Execute the stored procedure
        try:
            db.sp_commit_changes_existing_student(
                self.student_id,
                first_name,
                last_name,
                dob,
                dob_approx,
                start_date,
                active,
                trial_student,
                wait_list,
                current_rank,
                does_karate,
                tkd_comp_interest,
                krt_comp_interest,
                signed_waiver,
                aurora_member,
                profile_comment,
                email1,
                email2,
                email3,
                phone1,
                phone2,
                phone3,
                payment_good_till,
                pay_rate,
                gender,
                ys_testdate,
                yb_testdate,
                gs_testdate,
                gb_testdate,
                bs_testdate,
                bb_testdate,
                rs_testdate,
                rb_testdate,
                bks_testdate,
                first_dan_testdate,
                second_dan_testdate,
                third_dan_testdate,
                fourth_dan_testdate,
                fifth_dan_testdate,
                sixth_dan_testdate,
                seventh_dan_testdate,
                eighth_dan_testdate,
                ninth_dan_testdate,
                black_belt_intl_id,
                black_belt_number,
            )
            # Reset button color after saving
            if self.save_button:
                self.save_button.config(bg="SystemButtonFace")
            # Update original values to current values after successful save
            for field, mapped in self.entry_widgets_existing_student.items():
                if isinstance(mapped, tk.BooleanVar):
                    current_value = 1 if mapped.get() else 0
                elif isinstance(mapped, tk.Entry):
                    current_value = mapped.get()
                elif isinstance(mapped, ttk.Combobox):
                    # For competition interest dropdowns, extract the ID from the selection
                    if field in ["TKD Comp Interest:", "KRT Comp Interest:"]:
                        selection = mapped.get()
                        if selection and " - " in selection:
                            current_value = selection.split(" - ")[0]  # Extract ID part
                        else:
                            current_value = "1"  # Default to ID 1 if no selection
                    else:
                        current_value = mapped.get()
                elif isinstance(mapped, tk.Frame):
                    current_value = ""
                    for child in mapped.winfo_children():
                        if isinstance(child, tk.Entry):
                            current_value = child.get()
                            break
                else:
                    continue
                self.original_student_values[field] = current_value
            messagebox.showinfo("Success", "Changes saved successfully.")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
    
    def show_calendar_dialog(self, entry_widget):
        """Show a simple calendar dialog for date selection"""
        if self.calendar_dialog:
            self.calendar_dialog.destroy()
        
        self.calendar_dialog = tk.Toplevel(self)
        self.calendar_dialog.title("Select Date")
        self.calendar_dialog.geometry("300x300")
        self.calendar_dialog.resizable(False, False)
        self.calendar_dialog.transient(self)
        self.calendar_dialog.grab_set()
        
        # Center the dialog
        self.calendar_dialog.update_idletasks()
        x = (self.calendar_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.calendar_dialog.winfo_screenheight() // 2) - (300 // 2)
        self.calendar_dialog.geometry(f"300x300+{x}+{y}")
        
        # Create calendar frame
        calendar_frame = tk.Frame(self.calendar_dialog)
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Current date
        now = datetime.now()
        self.calendar_year = now.year
        self.calendar_month = now.month
        self.calendar_day = now.day
        
        # Month/Year navigation with fast controls
        nav_frame = tk.Frame(calendar_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))

        # Prev year
        prev_year_btn = tk.Button(nav_frame, text="«", width=2, command=self.prev_year)
        prev_year_btn.pack(side=tk.LEFT)

        # Prev month
        prev_button = tk.Button(nav_frame, text="<", width=2, command=self.prev_month)
        prev_button.pack(side=tk.LEFT, padx=(5, 0))

        # Month dropdown
        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.month_var = tk.StringVar(value=month_names[self.calendar_month-1])
        month_combo = ttk.Combobox(nav_frame, state="readonly", width=12, textvariable=self.month_var, values=month_names)
        month_combo.pack(side=tk.LEFT, padx=(10, 10))
        month_combo.bind('<<ComboboxSelected>>', self.on_calendar_month_change)

        # Year spinbox
        current_year = self.calendar_year
        self.year_var = tk.IntVar(value=current_year)
        year_spin = tk.Spinbox(nav_frame, from_=current_year-100, to=current_year+100, width=6, textvariable=self.year_var, command=self.on_calendar_year_change)
        year_spin.pack(side=tk.LEFT)
        # Also bind Enter / focus-out to commit
        year_spin.bind('<Return>', lambda e: self.on_calendar_year_change())
        year_spin.bind('<FocusOut>', lambda e: self.on_calendar_year_change())

        # Next month
        next_button = tk.Button(nav_frame, text=">", width=2, command=self.next_month)
        next_button.pack(side=tk.LEFT, padx=(10, 5))

        # Next year
        next_year_btn = tk.Button(nav_frame, text="»", width=2, command=self.next_year)
        next_year_btn.pack(side=tk.LEFT)
        
        # Calendar grid
        self.calendar_frame = tk.Frame(calendar_frame)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = tk.Frame(calendar_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        today_button = tk.Button(button_frame, text="Today", command=lambda: self.select_date(now.strftime("%Y-%m-%d")))
        today_button.pack(side=tk.LEFT)
        
        clear_button = tk.Button(button_frame, text="Clear", command=lambda: self.select_date(""))
        clear_button.pack(side=tk.LEFT, padx=(10, 0))
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.calendar_dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
        # Store reference to entry widget
        self.calendar_entry_widget = entry_widget
        
        # Create calendar
        self.create_calendar()
    
    def create_calendar(self):
        """Create the calendar grid"""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            label = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"))
            label.grid(row=0, column=i, padx=2, pady=2)
        
        # Get first day of month and number of days
        import calendar
        first_day, num_days = calendar.monthrange(self.calendar_year, self.calendar_month)
        
        # Sync month/year controls if present
        try:
            if hasattr(self, 'month_var'):
                names = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
                self.month_var.set(names[self.calendar_month-1])
            if hasattr(self, 'year_var'):
                self.year_var.set(self.calendar_year)
        except Exception:
            pass
        
        # Create day buttons
        row = 1
        col = first_day
        
        # Previous month days
        prev_month = self.calendar_month - 1 if self.calendar_month > 1 else 12
        prev_year = self.calendar_year if self.calendar_month > 1 else self.calendar_year - 1
        _, prev_num_days = calendar.monthrange(prev_year, prev_month)
        
        for i in range(first_day):
            day_num = prev_num_days - first_day + i + 1
            button = tk.Button(self.calendar_frame, text=str(day_num), 
                             command=lambda d=day_num, m=prev_month, y=prev_year: self.select_date(f"{y}-{m:02d}-{d:02d}"),
                             fg="gray", state="normal")
            button.grid(row=row, column=i, padx=2, pady=2, sticky="nsew")
        
        # Current month days
        for day in range(1, num_days + 1):
            button = tk.Button(self.calendar_frame, text=str(day), 
                             command=lambda d=day: self.select_date(f"{self.calendar_year}-{self.calendar_month:02d}-{d:02d}"),
                             fg="black")
            button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            # Highlight today
            if (self.calendar_year == datetime.now().year and 
                self.calendar_month == datetime.now().month and 
                day == datetime.now().day):
                button.config(bg="lightblue")
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Next month days
        next_month = self.calendar_month + 1 if self.calendar_month < 12 else 1
        next_year = self.calendar_year if self.calendar_month < 12 else self.calendar_year + 1
        
        day_num = 1
        while col <= 6:
            button = tk.Button(self.calendar_frame, text=str(day_num), 
                             command=lambda d=day_num, m=next_month, y=next_year: self.select_date(f"{y}-{m:02d}-{d:02d}"),
                             fg="gray", state="normal")
            button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            col += 1
            day_num += 1
        
        # Configure grid weights
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
    
    def prev_month(self):
        """Go to previous month"""
        self.calendar_month -= 1
        if self.calendar_month < 1:
            self.calendar_month = 12
            self.calendar_year -= 1
        self.create_calendar()
    
    def next_month(self):
        """Go to next month"""
        self.calendar_month += 1
        if self.calendar_month > 12:
            self.calendar_month = 1
            self.calendar_year += 1
        self.create_calendar()

    def prev_year(self):
        """Go to previous year"""
        self.calendar_year -= 1
        self.create_calendar()

    def next_year(self):
        """Go to next year"""
        self.calendar_year += 1
        self.create_calendar()

    def on_calendar_month_change(self, event=None):
        """Handle month dropdown changes"""
        names = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        try:
            selected = self.month_var.get()
            self.calendar_month = names.index(selected) + 1
        except Exception:
            pass
        self.create_calendar()

    def on_calendar_year_change(self):
        """Handle year spinbox changes"""
        try:
            year = int(self.year_var.get())
            self.calendar_year = year
        except Exception:
            pass
        self.create_calendar()
    
    def select_date(self, date_str):
        """Select a date and update the entry widget"""
        if self.calendar_entry_widget:
            self.calendar_entry_widget.delete(0, tk.END)
            if date_str:
                self.calendar_entry_widget.insert(0, date_str)
        if self.calendar_dialog:
            self.calendar_dialog.destroy()
        self.calendar_dialog = None
    
    def configure_dropdown_listbox(self, dropdown):
        """Configure the dropdown listbox to be wider for better readability"""
        try:
            # Get the listbox widget from the dropdown
            listbox = dropdown.tk.eval('ttk::combobox::PopdownWindow %s.l' % dropdown)
            if listbox:
                # Configure the listbox to be wider
                dropdown.tk.call('ttk::combobox::PopdownWindow', dropdown, 'configure', '-width', 30)
        except:
            # If configuration fails, just continue
            pass
    
    def show_competition_picker(self, entry_widget):
        """Show a popover listbox to choose competition interest (stores id, shows text)."""
        # Build toplevel near the entry
        picker = tk.Toplevel(self)
        picker.overrideredirect(True)
        picker.lift()
        picker.attributes('-topmost', True)

        # Position below the entry
        entry_widget.update_idletasks()
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        picker.geometry(f"240x160+{x}+{y}")

        lb = tk.Listbox(picker)
        lb.pack(fill=tk.BOTH, expand=True)

        # Populate listbox with full text
        options = getattr(entry_widget, '_comp_options', [])
        for comp_id, comp_text in options:
            lb.insert(tk.END, f"{comp_id} - {comp_text}")

        def on_select(event=None):
            sel = lb.curselection()
            if not sel:
                picker.destroy()
                return
            value = lb.get(sel[0])
            if ' - ' in value:
                comp_id_str, comp_text = value.split(' - ', 1)
                try:
                    entry_widget._comp_id = int(comp_id_str)
                except Exception:
                    entry_widget._comp_id = None
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, comp_text)
            picker.destroy()
            self.on_field_change()

        lb.bind('<Double-Button-1>', on_select)
        lb.bind('<Return>', on_select)
        lb.bind('<ButtonRelease-1>', on_select)

        def on_click_out(event):
            # Close if click outside
            if not (picker.winfo_x() <= event.x_root <= picker.winfo_x() + picker.winfo_width() and
                    picker.winfo_y() <= event.y_root <= picker.winfo_y() + picker.winfo_height()):
                picker.destroy()

        # Close on outside click
        self.bind('<Button-1>', on_click_out, add='+')
    
    def on_field_change(self, event=None):
        """Handle field changes - turn save button yellow only if values have actually changed"""
        if self.save_button and hasattr(self, 'original_student_values') and self.original_student_values:
            # Check if any field has changed from its original value
            has_changes = False
            
            for field, widget in self.entry_widgets_existing_student.items():
                if field in self.original_student_values:
                    original_value = self.original_student_values[field]
                    # Get current value from mapped widget types
                    if isinstance(widget, tk.BooleanVar):
                        current_value = 1 if widget.get() else 0
                        original_int = 1 if (original_value == "1" or original_value == 1 or original_value == "True" or original_value is True) else 0
                        if current_value != original_int:
                            has_changes = True
                            break
                    elif isinstance(widget, ttk.Combobox):
                        selection = widget.get()
                        if field in ["TKD Comp Interest:", "KRT Comp Interest:"] and selection:
                            current_value = selection.split(" - ")[0] if " - " in selection else selection
                        else:
                            current_value = selection
                        if str(current_value) != str(original_value):
                            has_changes = True
                            break
                    elif isinstance(widget, tk.Entry):
                        current_value = widget.get()
                        if str(current_value) != str(original_value):
                            has_changes = True
                            break
                    elif isinstance(widget, tk.Frame):
                        current_value = ""
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Entry):
                                current_value = child.get()
                                break
                        if str(current_value) != str(original_value):
                            has_changes = True
                            break
            
            # Only change button color if there are actual changes
            if has_changes:
                self.save_button.config(bg="yellow")
            else:
                self.save_button.config(bg="SystemButtonFace")
    
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

            # Remove duplicates and None values, convert to list
            cleaned_email_list = list(set(filter(lambda x: x is not None, email_list)))
            print(f"Email recipients: {cleaned_email_list}")

            # Use HTML email formatting like Draft to All
            email_handler_google.create_html_email(
                subject="Performance MA - ", 
                email_from="saoneil@live.com",
                emails_to=[],
                emails_cc=[],
                emails_bcc=cleaned_email_list,
                body="""<p>Hello Students/Parents,</p>
                
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

            messagebox.showinfo("Send Email", f"Email draft generated for {len(cleaned_email_list)} recipients, check drafts folder.")
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
            
            # Remove previous horizontal separator; we'll use a vertical divider between frames
            
            ## current student section
            existing_student_label = tk.Label(self.top_right_frame_tab2, text = "Modify Existing Student", font="verdana 15 bold")
            existing_student_label.grid(row=0, column=0, columnspan=6, sticky='w', pady=(30,15))

            existing_student_label = tk.Label(self.top_right_frame_tab2, text="Edit Existing Student:")
            existing_student_label.grid(row=1, column=1, sticky='e', pady=(0,30))

            # Student entry with dynamic filtering
            existing_student_entry = tk.Entry(self.top_right_frame_tab2, textvariable=self.existing_student_dropdown_value, width=33)
            existing_student_entry.grid(row=1, column=2, pady=(0,30))
            
            # Create listbox for student selection (overlay style)
            existing_student_listbox = tk.Listbox(self.top_right_frame_tab2, height=6, width=33)
            existing_student_listbox.grid_remove()  # Hide initially
            
            # Store student data for filtering
            self.existing_student_data = []
            
            # Load student data
            try:
                students_df = db.get_all_students_for_dropdown()
                # Store student data with ID for backend use
                self.existing_student_data = [{'id': row['id'], 'name': row['name']} for _, row in students_df.iterrows()]
                # Populate the listbox initially
                for student in self.existing_student_data:
                    existing_student_listbox.insert(tk.END, student['name'])
                print(f"Loaded {len(self.existing_student_data)} students")  # Debug print
            except Exception as e:
                print(f"Error loading students: {e}")  # Debug print
                existing_student_listbox.insert(tk.END, "DB Connection Failed")
            
            # Add filtering functionality to student entry
            def filter_existing_students():
                # Get the current text in the entry
                typed_text = self.existing_student_dropdown_value.get().lower()
                
                # Clear the listbox
                existing_student_listbox.delete(0, tk.END)
                
                # Filter students based on typed text
                if typed_text:
                    filtered_students = [student['name'] for student in self.existing_student_data 
                                       if typed_text in student['name'].lower()]
                else:
                    filtered_students = [student['name'] for student in self.existing_student_data]
                
                # Add filtered students to listbox
                for student_name in filtered_students:
                    existing_student_listbox.insert(tk.END, student_name)
                
                # Show listbox if there are results
                if filtered_students:
                    # Position listbox below entry box using absolute positioning
                    entry_x = existing_student_entry.winfo_x()
                    entry_y = existing_student_entry.winfo_y()
                    entry_height = existing_student_entry.winfo_height()
                    
                    existing_student_listbox.place(x=entry_x, y=entry_y + entry_height, width=existing_student_entry.winfo_width())
                    existing_student_listbox.lift()  # Bring to front
                    
                    # Auto-select if only one match
                    if len(filtered_students) == 1:
                        existing_student_listbox.selection_set(0)
                else:
                    existing_student_listbox.place_forget()
            
            def on_existing_student_select(event=None):
                # When a student is selected from listbox
                selection = existing_student_listbox.curselection()
                if selection:
                    selected_name = existing_student_listbox.get(selection[0])
                    print(f"Dropdown selection: {selected_name}")  # Debug print
                    self.existing_student_dropdown_value.set(selected_name)
                    existing_student_listbox.place_forget()
                    # Return focus to entry box
                    existing_student_entry.focus_set()
                    # Trigger the existing selection command
                    print("Calling existing_student_selection_tab2_command")  # Debug print
                    self.existing_student_selection_tab2_command()
            
            def on_existing_student_click(event):
                # Single-click selection - select immediately
                on_existing_student_select()
            
            def on_existing_student_key_press(event):
                # Handle keyboard navigation
                if event.keysym == 'Return':
                    on_existing_student_select()
                    return "break"
                elif event.keysym == 'Escape':
                    existing_student_listbox.place_forget()
                    existing_student_entry.focus_set()
                    return "break"
                elif event.keysym == 'Tab':
                    # Auto-select if only one match
                    if existing_student_listbox.size() == 1:
                        on_existing_student_select()
                        return "break"
                    else:
                        existing_student_listbox.place_forget()
                        return
                elif event.keysym in ['Up', 'Down']:
                    # Ensure list is visible and populated
                    if existing_student_listbox.size() == 0:
                        filter_existing_students()
                    else:
                        # Move selection up/down
                        size = existing_student_listbox.size()
                        sel = existing_student_listbox.curselection()
                        if sel:
                            idx = sel[0]
                        else:
                            idx = -1
                        if event.keysym == 'Down':
                            new_idx = min(idx + 1, size - 1) if size > 0 else 0
                        else:  # Up
                            new_idx = max(idx - 1, 0) if size > 0 else 0
                        existing_student_listbox.selection_clear(0, tk.END)
                        if size > 0:
                            existing_student_listbox.selection_set(new_idx)
                            existing_student_listbox.see(new_idx)
                    # Keep focus in entry and prevent cursor move
                    return "break"
                else:
                    # Other keys (typing) are handled by entry/filtering
                    return
            
            def on_existing_student_focus_in(event):
                # Show all students when entry gets focus
                filter_existing_students()
            
            def on_existing_student_focus_out(event):
                # Only hide listbox if focus is not going to the listbox
                if event.widget != existing_student_listbox:
                    self.after(150, lambda: existing_student_listbox.place_forget())
            
            # Bind events
            self.existing_student_dropdown_value.trace('w', lambda *args: filter_existing_students())
            existing_student_entry.bind('<FocusIn>', on_existing_student_focus_in)
            existing_student_entry.bind('<FocusOut>', on_existing_student_focus_out)
            existing_student_entry.bind('<KeyPress>', on_existing_student_key_press)
            existing_student_listbox.bind('<Button-1>', on_existing_student_click)
            existing_student_listbox.bind('<Double-Button-1>', on_existing_student_select)
            existing_student_listbox.bind('<Return>', on_existing_student_select)
            existing_student_listbox.bind('<FocusOut>', lambda e: existing_student_entry.focus_set())

            # Profile Comment field positioned to the right of the dropdown
            profile_comment_label = tk.Label(self.top_right_frame_tab2, text="Profile Comment:")
            profile_comment_label.grid(row=1, column=3, sticky='e', pady=(0,30), padx=(20,0))
            
            profile_comment_entry = tk.Entry(self.top_right_frame_tab2, width=25, justify='left')
            profile_comment_entry.grid(row=1, column=4, pady=(0,30), padx=(0,10), columnspan=2, sticky='w')
            
            # Bind field change events for profile comment
            profile_comment_entry.bind('<KeyRelease>', self.on_field_change)
            profile_comment_entry.bind('<Button-1>', self.on_field_change)
            profile_comment_entry.bind('<FocusOut>', self.on_field_change)
            
            self.entry_widgets_existing_student["Profile Comment:"] = profile_comment_entry

            current_student_label_info = [
            # Column 1: Basic student info, contact, payment, personal details
            ("First Name:", 2, 1),
            ("Last Name:", 3, 1),
            ("Email 1:", 4, 1),
            ("Email 2:", 5, 1),
            ("Email 3:", 6, 1),
            ("Phone 1:", 7, 1),
            ("Phone 2:", 8, 1),
            ("Phone 3:", 9, 1),
            ("Payment Good Till:", 10, 1),
            ("Pay Rate:", 11, 1),
            ("Start Date (yyyy-mm-dd):", 12, 1),
            ("Gender:", 13, 1),
            ("DOB (yyyy-mm-dd):", 14, 1),
            ("DOB-approx:", 15, 1),
            ("Active:", 16, 1),
            ("Trial Student:", 17, 1),
            ("Wait List:", 18, 1),
            ("Does Karate:", 19, 1),

            # Column 2: Rank and test dates
            ("Current Rank:", 2, 3),
            ("YS Test Date:", 3, 3),
            ("YB Test Date:", 4, 3),
            ("GS Test Date:", 5, 3),
            ("GB Test Date:", 6, 3),
            ("BS Test Date:", 7, 3),
            ("BB Test Date:", 8, 3),
            ("RS Test Date:", 9, 3),
            ("RB Test Date:", 10, 3),
            ("BKS Test Date:", 11, 3),
            ("1st Dan Test Date:", 12, 3),
            ("2nd Dan Test Date:", 13, 3),
            ("3rd Dan Test Date:", 14, 3),
            ("4th Dan Test Date:", 15, 3),
            ("5th Dan Test Date:", 16, 3),
            ("6th Dan Test Date:", 17, 3),
            ("7th Dan Test Date:", 18, 3),
            ("8th Dan Test Date:", 19, 3),
            ("9th Dan Test Date:", 20, 3),

            # Column 3: Black belt info, competition, membership, timestamps
            ("Black Belt Intl ID:", 2, 5),
            ("Black Belt Number:", 3, 5),
            ("TKD Comp Interest:", 4, 5),
            ("KRT Comp Interest:", 5, 5),
            ("Signed Waiver:", 6, 5),
            ("Aurora Member:", 7, 5),
            ("Record Creation:", 8, 5),
            ("Record Update:", 9, 5)
            ]
            for (text, row, col) in current_student_label_info:
                label = tk.Label(self.top_right_frame_tab2, text=text)
                label.grid(row=row, column=col, sticky='e', pady=(0,5))

                # Check if this is a date field
                date_fields = ["DOB (yyyy-mm-dd):", "Start Date (yyyy-mm-dd):", "Payment Good Till:", 
                             "YS Test Date:", "YB Test Date:", "GS Test Date:", "GB Test Date:", 
                             "BS Test Date:", "BB Test Date:", "RS Test Date:", "RB Test Date:", 
                             "BKS Test Date:", "1st Dan Test Date:", "2nd Dan Test Date:", 
                             "3rd Dan Test Date:", "4th Dan Test Date:", "5th Dan Test Date:", 
                             "6th Dan Test Date:", "7th Dan Test Date:", "8th Dan Test Date:", 
                             "9th Dan Test Date:"]
                
                # Check if this is a boolean field (checkbox)
                boolean_fields = ["DOB-approx:", "Active:", "Trial Student:", "Wait List:", 
                                "Does Karate:", "Signed Waiver:", "Aurora Member:"]
                # Email fields (wider width)
                email_fields = ["Email 1:", "Email 2:", "Email 3:"]
                # Name fields (wider width)
                name_fields = ["First Name:", "Last Name:"]
                
                if text in date_fields:
                    # Create frame for entry and calendar button
                    date_frame = tk.Frame(self.top_right_frame_tab2)
                    date_frame.grid(row=row, column=col+1, padx=(0, 10), sticky='w')
                    
                    entry = tk.Entry(date_frame, width=15, justify='left')
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    # Calendar button
                    calendar_button = tk.Button(date_frame, text="📅", width=3, 
                                              command=lambda e=entry: self.show_calendar_dialog(e))
                    calendar_button.pack(side=tk.RIGHT, padx=(5, 0))
                    
                    # Bind field change events for date fields
                    entry.bind('<KeyRelease>', self.on_field_change)
                    entry.bind('<Button-1>', self.on_field_change)
                    entry.bind('<FocusOut>', self.on_field_change)
                    
                    self.entry_widgets_existing_student[text] = entry
                    
                elif text in boolean_fields:
                    # Create checkbox for boolean fields using ttk.Checkbutton with variable
                    var = tk.BooleanVar()
                    checkbox = ttk.Checkbutton(self.top_right_frame_tab2, variable=var, command=self.on_field_change)
                    checkbox.grid(row=row, column=col+1, padx=(0, 10), sticky='w')
                    # Store the variable for later use
                    self.entry_widgets_existing_student[text] = var
                elif text in email_fields:
                    # Create wider entries for email fields (double width)
                    entry = tk.Entry(self.top_right_frame_tab2, width=30, justify='left')
                    entry.grid(row=row, column=col+1, padx=(0, 10), sticky='w')

                    # Bind field change events for email fields
                    entry.bind('<KeyRelease>', self.on_field_change)
                    entry.bind('<Button-1>', self.on_field_change)
                    entry.bind('<FocusOut>', self.on_field_change)

                    self.entry_widgets_existing_student[text] = entry
                elif text in name_fields:
                    # Create wider entries for name fields (double width)
                    entry = tk.Entry(self.top_right_frame_tab2, width=30, justify='left')
                    entry.grid(row=row, column=col+1, padx=(0, 10), sticky='w')

                    # Bind field change events for name fields
                    entry.bind('<KeyRelease>', self.on_field_change)
                    entry.bind('<Button-1>', self.on_field_change)
                    entry.bind('<FocusOut>', self.on_field_change)

                    self.entry_widgets_existing_student[text] = entry
                elif text in ["TKD Comp Interest:", "KRT Comp Interest:"]:
                    # Create a picker: Entry + button that opens a list of options
                    picker_frame = tk.Frame(self.top_right_frame_tab2)
                    picker_frame.grid(row=row, column=col+1, padx=(0, 10), sticky='w')

                    entry = tk.Entry(picker_frame, width=15, justify='left')
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Load options from DB and store on entry
                    options = []
                    try:
                        if text == "TKD Comp Interest:":
                            df_levels = db.get_tkd_competition_levels()
                        else:
                            df_levels = db.get_krt_competition_levels()
                        options = [(int(row['id']), str(row['competition_level'])) for _, row in df_levels.iterrows()]
                    except Exception:
                        options = [(1, "Beginner"), (2, "Intermediate"), (3, "Advanced")]
                    entry._comp_options = options  # store as attribute
                    entry._comp_id = None          # selected id

                    btn = tk.Button(picker_frame, text="▼", width=2, command=lambda e=entry: self.show_competition_picker(e))
                    btn.pack(side=tk.RIGHT, padx=(5, 0))

                    # Bind field change events for picker
                    entry.bind('<KeyRelease>', self.on_field_change)
                    entry.bind('<Button-1>', self.on_field_change)
                    entry.bind('<FocusOut>', self.on_field_change)

                    # Store the frame (consistent with date fields) for lookup
                    self.entry_widgets_existing_student[text] = picker_frame
                    
                else:
                    entry = tk.Entry(self.top_right_frame_tab2, width=15, justify='left')
                    entry.grid(row=row, column=col+1, padx=(0, 10), sticky='w')

                    # Bind field change events for regular fields
                    entry.bind('<KeyRelease>', self.on_field_change)
                    entry.bind('<Button-1>', self.on_field_change)
                    entry.bind('<FocusOut>', self.on_field_change)

                    # Store mapping for regular entry fields
                    self.entry_widgets_existing_student[text] = entry

            self.save_button = tk.Button(self.top_right_frame_tab2, text="Save Changes", command=self.commit_changes_existing_student_command)
            self.save_button.grid(row=25, column=1, columnspan=6, sticky='n', pady=(40, 0))
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