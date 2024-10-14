import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date, time, timedelta

class ReceptionRegisterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reception Register")
        self.geometry("1000x600")

        self.create_database()
        self.create_main_ui()
        
        # Start the time update
        self.update_time()

    def create_database(self):
        conn = sqlite3.connect('reception_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_date DATE NOT NULL,
            visit_time TIME NOT NULL,
            patient_count INTEGER NOT NULL,
            name_surname TEXT NOT NULL,
            file_number TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            cash_amount REAL,
            age INTEGER NOT NULL,
            id_number TEXT,
            medical_aid_number TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def create_main_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.register_frame = ttk.Frame(self.notebook, padding="20")
        self.view_frame = ttk.Frame(self.notebook, padding="20")
        self.report_frame = ttk.Frame(self.notebook, padding="20")
        self.search_frame = ttk.Frame(self.notebook, padding="20")

        self.notebook.add(self.register_frame, text="Register Patient")
        self.notebook.add(self.view_frame, text="View Daily Records")
        self.notebook.add(self.report_frame, text="Weekly Report")
        self.notebook.add(self.search_frame, text="Patient Search")

        self.create_register_ui()
        self.create_view_ui()
        self.create_report_ui()
        self.create_search_ui()

        # Create a label for displaying current time
        self.time_label = ttk.Label(self, text="")
        self.time_label.pack(anchor="ne", padx=10, pady=10)

    def create_register_ui(self):
        labels = ["Name Surname", "File Number", "Age", "ID Number", "Medical Aid Number"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.register_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(self.register_frame, width=50)
            entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            self.entries[label] = entry

        ttk.Label(self.register_frame, text="Payment Method").grid(row=len(labels), column=0, sticky=tk.W, pady=5)
        self.payment_method = tk.StringVar(value="medical_aid")
        ttk.Radiobutton(self.register_frame, text="Medical Aid", variable=self.payment_method, value="medical_aid").grid(row=len(labels), column=1, sticky=tk.W)
        ttk.Radiobutton(self.register_frame, text="Cash", variable=self.payment_method, value="cash").grid(row=len(labels), column=1, sticky=tk.E)

        ttk.Label(self.register_frame, text="Cash Amount").grid(row=len(labels)+1, column=0, sticky=tk.W, pady=5)
        self.cash_amount_entry = ttk.Entry(self.register_frame, width=50)
        self.cash_amount_entry.grid(row=len(labels)+1, column=1, sticky=tk.W, pady=5)

        submit_button = ttk.Button(self.register_frame, text="Register Patient", command=self.register_patient)
        submit_button.grid(row=len(labels)+2, column=1, sticky=tk.E, pady=20)

    def create_view_ui(self):
        ttk.Label(self.view_frame, text="Select Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(self.view_frame, width=20)
        self.date_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        view_button = ttk.Button(self.view_frame, text="View Records", command=self.view_daily_records)
        view_button.grid(row=0, column=2, sticky=tk.W, pady=5)

        self.records_tree = ttk.Treeview(self.view_frame, columns=('Time', 'Count', 'Name', 'File Number', 'Payment', 'Amount', 'Age'), show='headings')
        self.records_tree.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.records_tree.heading('Time', text='Time')
        self.records_tree.heading('Count', text='Count')
        self.records_tree.heading('Name', text='Name')
        self.records_tree.heading('File Number', text='File Number')
        self.records_tree.heading('Payment', text='Payment')
        self.records_tree.heading('Amount', text='Amount')
        self.records_tree.heading('Age', text='Age')

        scrollbar = ttk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.records_tree.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.records_tree.configure(yscroll=scrollbar.set)

    def create_report_ui(self):
        ttk.Label(self.report_frame, text="Select Week End Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.week_end_entry = ttk.Entry(self.report_frame, width=20)
        self.week_end_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.week_end_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        report_button = ttk.Button(self.report_frame, text="Generate Report", command=self.generate_weekly_report)
        report_button.grid(row=0, column=2, sticky=tk.W, pady=5)

        self.report_text = tk.Text(self.report_frame, height=20, width=80)
        self.report_text.grid(row=1, column=0, columnspan=3, pady=10)

    def create_search_ui(self):
        ttk.Label(self.search_frame, text="Search Patient").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(self.search_frame, width=50)
        self.search_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        search_button = ttk.Button(self.search_frame, text="Search", command=self.search_patient)
        search_button.grid(row=0, column=2, sticky=tk.W, pady=5)

        self.search_result = tk.Text(self.search_frame, height=20, width=80)
        self.search_result.grid(row=1, column=0, columnspan=3, pady=10)

    def register_patient(self):
        name_surname = self.entries["Name Surname"].get()
        file_number = self.entries["File Number"].get()
        age = self.entries["Age"].get()
        id_number = self.entries["ID Number"].get()
        medical_aid_number = self.entries["Medical Aid Number"].get()
        payment_method = self.payment_method.get()
        cash_amount = self.cash_amount_entry.get() if payment_method == "cash" else None

        if not all([name_surname, file_number, age]):
            messagebox.showerror("Error", "Name, File Number, and Age are required fields.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
            return

        if payment_method == "cash" and not cash_amount:
            messagebox.showerror("Error", "Cash amount is required for cash payments.")
            return

        try:
            if cash_amount:
                cash_amount = float(cash_amount)
        except ValueError:
            messagebox.showerror("Error", "Cash amount must be a number.")
            return

        conn = sqlite3.connect('reception_register.db')
        cursor = conn.cursor()

        visit_date = date.today().isoformat()
        visit_time = datetime.now().time().isoformat()

        cursor.execute("SELECT COUNT(*) FROM patient_visits WHERE visit_date = ?", (visit_date,))
        patient_count = cursor.fetchone()[0] + 1

        cursor.execute('''
        INSERT INTO patient_visits (visit_date, visit_time, patient_count, name_surname, file_number, payment_method, cash_amount, age, id_number, medical_aid_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (visit_date, visit_time, patient_count, name_surname, file_number, payment_method, cash_amount, age, id_number, medical_aid_number))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Patient {name_surname} registered successfully.")
        self.clear_entries()

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.cash_amount_entry.delete(0, tk.END)
        self.payment_method.set("medical_aid")

    def view_daily_records(self):
        selected_date = self.date_entry.get()
        try:
            datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        conn = sqlite3.connect('reception_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT visit_time, patient_count, name_surname, file_number, payment_method, cash_amount, age
        FROM patient_visits
        WHERE visit_date = ?
        ORDER BY visit_time
        ''', (selected_date,))
        records = cursor.fetchall()
        conn.close()

        self.records_tree.delete(*self.records_tree.get_children())
        for record in records:
            self.records_tree.insert('', 'end', values=record)

    def generate_weekly_report(self):
        week_end_date = self.week_end_entry.get()
        try:
            week_end = datetime.strptime(week_end_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        week_start = week_end - timedelta(days=6)

        conn = sqlite3.connect('reception_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT visit_date, COUNT(*) as daily_count,
               SUM(CASE WHEN payment_method = 'cash' THEN 1 ELSE 0 END) as cash_count,
               SUM(CASE WHEN payment_method = 'medical_aid' THEN 1 ELSE 0 END) as medical_aid_count
        FROM patient_visits
        WHERE visit_date BETWEEN ? AND ?
        GROUP BY visit_date
        ORDER BY visit_date
        ''', (week_start.isoformat(), week_end.isoformat()))
        records = cursor.fetchall()
        conn.close()

        report = f"Weekly Report: {week_start} to {week_end}\n\n"
        report += "Date       | Total | Cash | Medical Aid\n"
        report += "-" * 40 + "\n"

        total_patients = 0
        total_cash = 0
        total_medical_aid = 0

        for record in records:
            visit_date, daily_count, cash_count, medical_aid_count = record
            report += f"{visit_date} | {daily_count:5d} | {cash_count:4d} | {medical_aid_count:11d}\n"
            total_patients += daily_count
            total_cash += cash_count
            total_medical_aid += medical_aid_count

        report += "-" * 40 + "\n"
        report += f"Total      | {total_patients:5d} | {total_cash:4d} | {total_medical_aid:11d}\n\n"
        report += f"Average daily patients: {total_patients / 7:.2f}"

        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, report)

    def search_patient(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        conn = sqlite3.connect('reception_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT visit_date, visit_time, name_surname, file_number, payment_method, cash_amount, age
        FROM patient_visits
        WHERE name_surname LIKE ? OR file_number LIKE ?
        ORDER BY visit_date DESC, visit_time DESC
        LIMIT 10
        ''', (f'%{search_term}%', f'%{search_term}%'))
        records = cursor.fetchall()
        conn.close()

        self.search_result.delete('1.0', tk.END)
        if not records:
            self.search_result.insert(tk.END, "No matching records found.")
        else:
            for record in records:
                visit_date, visit_time, name, file_number, payment, amount, age = record
                result = f"Date: {visit_date}, Time: {visit_time}\n"
                result += f"Name: {name}, File Number: {file_number}, Age: {age}\n"
                result += f"Payment: {payment}, Amount: {amount if amount else 'N/A'}\n\n"
                self.search_result.insert(tk.END, result)

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)  # Update every 1000ms (1 second)

if __name__ == "__main__":
    app = ReceptionRegisterApp()
    app.mainloop()