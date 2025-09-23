from sean_resources.resources import get_connection, execute_sql, get_dataframe
import pandas as pd
import calendar


schema = "pma"

## tab 1 ##
def sp_all_active_students():
    query = "call sp_all_active_students;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_trial_students():
    query = "call sp_all_trial_students;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_waitlist_students():
    query = "call sp_all_waitlist_students;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_emails():
    query = "call sp_all_emails;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_karate_emails():
    query = "call sp_karate_emails;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_waitlist_emails():
    query = "call sp_waitlist_emails;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_outstanding_payments():
    query = "call sp_outstanding_payments;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_pma_general_search(first_name, last_name, email):
    """Search for students using first name, last name, or email with flexible matching"""
    # Handle None values and empty strings
    first_name = first_name if first_name and first_name.strip() else None
    last_name = last_name if last_name and last_name.strip() else None
    email = email if email and email.strip() else None
    
    # Format parameters for the stored procedure call
    first_name_param = f"'{first_name}'" if first_name else "NULL"
    last_name_param = f"'{last_name}'" if last_name else "NULL"
    email_param = f"'{email}'" if email else "NULL"
    
    query = f"call sp_pma_general_search({first_name_param}, {last_name_param}, {email_param});"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def search_grid_tab1(first_name, last_name, email):
    """Legacy function - now uses the new stored procedure"""
    return sp_pma_general_search(first_name, last_name, email)
def sp_commit_payment_to_db(IN_ID, IN_GOOD_TILL, IN_PAY_RATE, IN_TOTAL, IN_TAX, IN_KRT, IN_TXN_NOTE):
    query = f'call sp_commit_payment_to_db({IN_ID}, "{IN_GOOD_TILL}", {IN_PAY_RATE}, {IN_TOTAL}, {IN_TAX}, {IN_KRT}, "{IN_TXN_NOTE}");'
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_insert_club_payment(IN_IDS, IN_AMOUNT, IN_CALC_TAX, IN_METHOD, IN_TXN_NOTE, IN_PAYER_ADDRESS, IN_CLUB):
    query = f'call sp_insert_club_payment("{IN_IDS}", {IN_AMOUNT}, {IN_CALC_TAX}, {IN_METHOD}, "{IN_TXN_NOTE}", "{IN_PAYER_ADDRESS}", "{IN_CLUB}");'
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def get_email_address_for_payment(ids):
    query1 = f"SELECT email1 FROM students where id in({ids}) group by email1 limit 1;"
    query2 = f"select group_concat(CONCAT(' ', first_name, ' ', last_name)) as `names` from students where active = 1 and id in({ids});"
    cn1 = get_connection(sql_db = schema)
    df1 = get_dataframe(connection=cn1, sql=query1)
    address = df1["email1"].to_list()
    # address = ", ".join(df1["email1"].to_list())

    cn2 = get_connection(sql_db = schema)
    df2 = get_dataframe(connection=cn2, sql=query2)
    names = ", ".join(df2["names"].to_list())


    return address, names
def save_db_objects():
    backup_data = [
        ("select * from students;", "students.csv"),
        ("select * from expense;", "expense.csv"),
        ("select * from income;", "income.csv"),
        ("select * from instructors;", "instructors.csv"),
        ("select * from rental_hours;", "rental_hours.csv"),
        ("select * from teaching_hours;", "teaching_hours.csv"),
        ("select * from club_equipment;", "club_equipment.csv"),
        ("select * from club_equipment_transactions;", "club_equipment_transactions.csv"),
        ("select * from club_equipment_stock_orders;", "club_equipment_stock_orders.csv")
    ]
    for query, filename in backup_data:
        cn = get_connection(sql_db = schema)
        df = get_dataframe(connection=cn, sql=query)
        df.to_csv("C:\\Users\\saone\\Documents\\PMA\\zflask_app_files\\" +"zzz_" + filename)

## tab 2 ##
def sp_commit_new_student(first_name, last_name, email1, email2, email3, phone1, phone2, phone3, pay_rate, start_date, dob, dob_approx, does_karate, current_rank):
    query = f"call sp_commit_new_student_to_db('{first_name}', '{last_name}', '{email1}', '{email2}', '{email3}', '{phone1}', '{phone2}', '{phone3}', {pay_rate}, '{start_date}', {dob}, {dob_approx}, {does_karate}, '{current_rank}')"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_view_student_by_id(student_id):
    query = f"call sp_view_student_by_id({student_id});"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_commit_changes_existing_student(IN_ID,IN_FIRST_NAME,IN_LAST_NAME,IN_DOB,IN_DOB_APPROX,IN_START_DATE,IN_ACTIVE,IN_TRIAL_STUDENT,IN_WAIT_LIST,IN_CURRENT_RANK,IN_DOES_KARATE,IN_TKD_COMP_INT,IN_KRT_COMP_INT,IN_SIGNED_WAIVER,IN_AURORA_MEMBER,IN_PROFILE_COMMENT,IN_EMAIL1,IN_EMAIL2,IN_EMAIL3,IN_PHONE1,IN_PHONE2,IN_PHONE3,IN_PAYMENT_GOOD_TILL,IN_PAY_RATE,IN_GENDER,IN_YS_TD,IN_YB_TD,IN_GS_TD,IN_GB_TD,IN_BS_TD,IN_BB_TD,IN_RS_TD,IN_RB_TD,IN_BKS_TD,IN_1ST_TD,IN_2ND_TD,IN_3RD_TD,IN_4TH_TD,IN_5TH_TD,IN_6TH_TD,IN_7TH_TD,IN_8TH_TD,IN_9TH_TD,IN_BLACK_BELT_INTL_ID,IN_BLACK_BELT_NUMBER):
    query = f'call sp_commit_changes_existing_student({IN_ID},"{IN_FIRST_NAME}","{IN_LAST_NAME}",{IN_DOB},{IN_DOB_APPROX},{IN_START_DATE},{IN_ACTIVE},{IN_TRIAL_STUDENT},{IN_WAIT_LIST},"{IN_CURRENT_RANK}",{IN_DOES_KARATE},{IN_TKD_COMP_INT},{IN_KRT_COMP_INT},{IN_SIGNED_WAIVER},{IN_AURORA_MEMBER},"{IN_PROFILE_COMMENT}","{IN_EMAIL1}","{IN_EMAIL2}","{IN_EMAIL3}","{IN_PHONE1}","{IN_PHONE2}","{IN_PHONE3}",{IN_PAYMENT_GOOD_TILL},{IN_PAY_RATE},"{IN_GENDER}",{IN_YS_TD},{IN_YB_TD},{IN_GS_TD},{IN_GB_TD},{IN_BS_TD},{IN_BB_TD},{IN_RS_TD},{IN_RB_TD},{IN_BKS_TD},{IN_1ST_TD},{IN_2ND_TD},{IN_3RD_TD},{IN_4TH_TD},{IN_5TH_TD},{IN_6TH_TD},{IN_7TH_TD},{IN_8TH_TD},{IN_9TH_TD},{IN_BLACK_BELT_INTL_ID},{IN_BLACK_BELT_NUMBER})'
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
    cn.close()

## tab 3 ##
def sp_commit_testing_results(student_id, testing_date):
    query = f"call sp_commit_testing_results({student_id}, '{testing_date}');"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_display_testing_grid():
    query = "call sp_display_testing_grid;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

def get_students_testing_preview(ids):
    """Return detailed testing fields for selected students.

    ids can be a list of integers or a comma-separated string of ids.
    """
    if ids is None:
        return pd.DataFrame()
    if isinstance(ids, list):
        ids = [str(i) for i in ids if str(i).strip()]
        if len(ids) == 0:
            return pd.DataFrame()
        ids_csv = ",".join(ids)
    else:
        ids_csv = str(ids)
        if ids_csv.strip() == "":
            return pd.DataFrame()

    query = f"""
    select
        concat(first_name, ' ', last_name) as name,
        current_rank,
        yellow_stripe_testdate as `YS`,
        yellow_belt_testdate as `YB`,
        green_stripe_testdate as `GS`,
        green_belt_testdate as `GB`,
        blue_stripe_testdate as `BS`,
        blue_belt_testdate as `BB`,
        red_stripe_testdate as `RS`,
        red_belt_testdate as `RB`,
        black_stripe_testdate as `BKS`,
        `1st_dan_testdate` as `1D`,
        `2nd_dan_testdate` as `2D`,
        `3rd_dan_testdate` as `3D`,
        `4th_dan_testdate` as `4D`,
        `5th_dan_testdate` as `5D`,
        `6th_dan_testdate` as `6D`,
        `7th_dan_testdate` as `7D`,
        `8th_dan_testdate` as `8D`,
        `9th_dan_testdate` as `9D`
    from students
    where id in({ids_csv})
    order by name
    ;
    """
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

## tab 4 ##
def sp_view_eom_transfer():
    query = "call sp_view_eom_transfer;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_view_current_rental_hours():
    query = "call sp_view_current_rental_hours;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_view_current_teaching_hours():
    query = "call sp_view_current_teaching_hours;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_import_rental_month(month_name):
    month_dict = {month: index for index, month in enumerate(calendar.month_abbr) if month}
    month_num = month_dict[month_name]
    query = f"call sp_import_rental_month({month_num});"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_cancel_rental_date(cancel_date, cancel_reason):
    query = f"call sp_cancel_rental_date('{cancel_date}', '{cancel_reason}')"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_import_teaching_hours(teaching_date, instructor_id, teaching_hours):
    query = f"call sp_import_teaching_hours('{teaching_date}', {instructor_id}, {teaching_hours})"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_view_instructors():
    query = "call sp_view_instructors;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_pay_instructors():
    query = "call sp_pay_instructors;"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_paid_instructors_email():
    query = "call sp_paid_instructors_email;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_import_expense(expense_date, expense_desc, expense_amount, expense_tax, expense_method, expense_club):
    query = f"call sp_import_expense('{expense_date}', '{expense_desc}', {expense_amount}, {expense_tax}, '{expense_method}', '{expense_club}')"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_all_income():
    query = "call sp_all_income;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_expenses():
    query = "call sp_all_expenses;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_teaching_hours():
    query = "call sp_all_teaching_hours;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_all_rental_hours():
    query = "call sp_all_rental_hours;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df
def sp_projections():
    query = "call sp_projections;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

## context menu actions, all tabs ##
def sp_all_students_list():
    query = "call sp_all_students_list;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    id_list = df["id"].to_list()
    name_list = df["name"].to_list()
    combined_list = [str(x) + " - " + str(y) for x, y in zip(id_list, name_list)]

    return id_list, name_list, combined_list
def sp_toggle_trial_or_active(student_id, field_name):
    query = f"call sp_toggle_trial_or_active({student_id}, '{field_name}');"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
def sp_add_profile_comment(student_id, profile_comment):
    query = f"call sp_add_profile_comment({student_id}, '{profile_comment}');"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)

## accompanying scripts
def sp_birthdays():
    query = "call sp_birthdays;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

## tab 5 - PMA Equipment methods ##
def sp_view_active_students():
    query = """
    select
    id,
    concat(first_name, " ", last_name) as `name`
    from students where active = 1;
    """
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

def sp_view_club_equipment():
    query = "select * from club_equipment;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

def sp_club_equipment_remaining_stock():
    query = "call sp_club_equipment_remaining_stock_v2;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

def sp_view_club_equipment_transactions():
    query = """
    select 
    t.id,
    concat(first_name, " ", last_name) as `name`,
    t.item_id,
    ce.item_description,
    t.qty,
    t.amount_paid,
    pay_date
    from club_equipment_transactions t
    left join club_equipment ce on ce.id = t.item_id
    left join students s on s.id = t.student_id
    order by t.id desc
    """
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)

    return df

def sp_insert_club_equipment_payment(student_id, item_id, quantity, amount, paid_bool, paydate):
    # Handle null item_id
    if item_id is None:
        item_id_str = "null"
    else:
        item_id_str = str(item_id)
    
    # Handle null paydate
    if paydate is None:
        query = f"call sp_insert_club_equipment_payment({student_id}, {item_id_str}, {quantity}, {amount}, {paid_bool}, null);"
    else:
        query = f"call sp_insert_club_equipment_payment({student_id}, {item_id_str}, {quantity}, {amount}, {paid_bool}, '{paydate}');"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
    cn.close()

def get_all_students_for_dropdown():
    query = "select id, concat(first_name, ' ', last_name) as name from students where active = 1 order by first_name, last_name;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def get_all_equipment_for_dropdown():
    query = "select id, item_description from club_equipment order by id asc;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def get_belt_equipment_for_dropdown():
    query = "select id, item_description from club_equipment where item_description like '%belt%' order by id asc;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def update_transaction_payment(transaction_id, amount):
    query = f"update club_equipment_transactions set paid_bool = 1, pay_date = now(), amount_paid = {amount} where id = {transaction_id};"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
    cn.close()

def update_transaction_item(transaction_id, item_id):
    query = f"update club_equipment_transactions set item_id = {item_id} where id = {transaction_id};"
    cn = get_connection(sql_db = schema)
    execute_sql(connection=cn, sql=query)
    cn.close()

def sp_club_equipment_data_v2():
    query = "call sp_club_equipment_data_v2;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def get_tkd_competition_levels():
    query = "select id, competition_level from tkd_competition_interest;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df

def get_krt_competition_levels():
    query = "select id, competition_level from krt_competition_interest;"
    cn = get_connection(sql_db = schema)
    df = get_dataframe(connection=cn, sql=query)
    return df