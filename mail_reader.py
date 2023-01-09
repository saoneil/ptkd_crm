import imaplib
import email
import os

#https://www.youtube.com/watch?v=6DD4IOHhNYo

#datestring_start = 'ALL SINCE "1-Jan-2023"'
#datestring_end = ''
# datestring_start = 'ALL SINCE "1-Jan-2023"'
# datestring_end = ' BEFORE "5-Jan-2023"'
def mail_reader_func(datestring_start, datestring_end):
    host = os.environ.get('email_host_python')
    username = os.environ.get('email_username')
    password = os.environ.get('email_password')

    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)


    mail.select('"PTKD Fee Receipts"')


    #_, search_data = mail.search(None, 'ALL SINCE "1-Jan-2023" BEFORE "5-Jan-2023"')
    _, search_data = mail.search(None, datestring_start + datestring_end)


    list_tuitionfees = []
    list_tuitioncreditsandtesting = []
    for num in search_data[0].split():
        _, data = mail.fetch(num, "(rfc822)")
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        
        # for header in ["subject", "to", "from", "date"]:
        #     print("{}: {}".format(header, email_message[header]))
        
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                bodystr = str(body)
                bodystr_other = bodystr[bodystr.rfind("Paid"):bodystr.rfind("Paid")+40]
                x = bodystr.find("Total Paid:")
                y = bodystr.find("Tax")
                z = bodystr.find("+$")
                a = bodystr_other.find("+")
                if z == -1:
                    list_tuitionfees.append(bodystr[(x+13):(y-4)])
                else:
                    list_tuitionfees.append(bodystr[(x+13):(z-3)])
                
                #print(bodystr_other[a+2:a+5])
                list_tuitioncreditsandtesting.append(bodystr_other[(a+2):(a+5)])


    mail.select('"PTKD Gear Receipts"')


    #_, search_data = mail.search(None, 'ALL SINCE "1-Jan-2021" BEFORE "31-Dec-2021"')
    #_, search_data = mail.search(None, 'ALL SINCE "1-Jan-2023"')
    _, search_data = mail.search(None, datestring_start + datestring_end)


    list_gearfees = []
    for num in search_data[0].split():
        _, data = mail.fetch(num, "(rfc822)")
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                bodystr = str(body)
                x = bodystr.find("Total:")
                y = bodystr.find("Additional Information")
                list_gearfees.append(bodystr[(x+8):(y-154)])


        
    newcreditlist = []
    for i in range(len(list_tuitioncreditsandtesting)):
            try:
                newcreditlist.append(float(list_tuitioncreditsandtesting[i]))
            except:
                pass

    other_sum = 0
    for i in range(len(newcreditlist)):
        other_sum += float(newcreditlist[i])

    fees_sum = 0
    for i in range(len(list_tuitionfees)):
        fees_sum += float(list_tuitionfees[i])
     
    gear_sum = 0
    for i in range(len(list_gearfees)):
        gear_sum += float(list_gearfees[i])  
        

    #print("Annual Starting Balance in Bank Account: $")
    string1 = "Total Fees w/ Receipts: $" + str("{:.2f}".format(fees_sum)) + ", " + str(len(list_tuitionfees)) + " records"
    string2 = "Total Gear Fees w/ Receipts: $" + str("{:.2f}".format(gear_sum)) + ", " + str(len(list_gearfees)) + " records"
    string3 = "Total Testing/Credits Collected: $" + str("{:.2f}".format(other_sum)) + ", " + str(len(newcreditlist)) + " records"

    result = string1 + '\n' + string2 + '\n' + string3
    return result


# return_string = mail_reader_func(datestring_start, datestring_end)
# print(return_string)
