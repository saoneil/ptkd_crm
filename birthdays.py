import tkinter as tk
from tkinter import scrolledtext
import db

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
    df = db.sp_birthdays()

    root = tk.Tk()
    app = DataFrameDisplayApp(root, df)
    root.mainloop()


if __name__ == '__main__':
    main()