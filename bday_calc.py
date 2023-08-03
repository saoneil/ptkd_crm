import os, sys
import pandas as pd
import pyodbc
from resources.resources import get_dataframe
import tkinter as tk
from tkinter import scrolledtext

def get_connection_pyodbc():
    cnxn = pyodbc.connect(
        DRIVER=os.environ.get('mysql_driver_python'),
        UID=os.environ.get('mysql_user'),
        Password=os.environ.get('mysql_pass'),
        Server=os.environ.get('mysql_host'),
        Database='ptkd_students',
        Port='3306')
    return cnxn
class DataFrameDisplayApp:
    def __init__(self, root, dataframe):
        self.root = root
        self.dataframe = dataframe

        self.init_ui()

    def init_ui(self):
        self.root.title('Club Birthdays')

        self.root.geometry('400x150')

        self.text_widget = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self.display_dataframe()

    def display_dataframe(self):
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, str(self.dataframe))
def main():
    sql_string = """
    SELECT
    first_name,last_name,dob,
    ROUND(TIMESTAMPDIFF(MONTH, dob, CURDATE()) / 12 + (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(dob, '%m%d'))) AS age
    FROM ptkd_students.ptkd_students where active = 1 and
    (
    DATE_FORMAT(CURDATE(), '%m%d') = DATE_FORMAT(dob, '%m%d')
    or DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '%m%d') = DATE_FORMAT(dob, '%m%d')
    or DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), '%m%d') = DATE_FORMAT(dob, '%m%d')
    );
    """
    cn = get_connection_pyodbc()
    df = get_dataframe(cn, sql_string)

    root = tk.Tk()
    app = DataFrameDisplayApp(root, df)
    root.mainloop()


if __name__ == '__main__':
    main()



