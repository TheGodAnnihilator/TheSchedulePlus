import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os

class EmploySubconsultantManager:
    def __init__(self, master, status_callback=None):
        self.master = master
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.db_config = self.load_db_config('config.ini')
        if not self.db_config:
            self.show_status_message("Configuration Error: Database config file not found or invalid", error=True)
            master.after(5000, master.destroy)
            return

        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            self.show_status_message(f"Database Connection Error: {err}", error=True)
            master.after(5000, master.destroy)
            return

        self.create_tables()
        self.create_styles()

        self.notebook = ttk.Notebook(master)
        self.employ_tab = ttk.Frame(self.notebook)
        self.subconsultant_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employ_tab, text='Employ')
        self.notebook.add(self.subconsultant_tab, text='Subconsultant')
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.create_employ_widgets()
        self.create_subconsultant_widgets()

        self.populate_employ_list()
        self.populate_subconsultant_list()

    def load_db_config(self, config_file):
        cfg = configparser.ConfigParser()
        if not os.path.exists(config_file):
            return None
        cfg.read(config_file)
        if 'mysql' not in cfg:
            return None
        sec = cfg['mysql']
        for k in ('host','user','password','database'):
            if k not in sec:
                return None
        return {k: sec[k] for k in ('host','user','password','database')}

    def show_status_message(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS employ (
                    employ_id VARCHAR(50) PRIMARY KEY,
                    employ_name VARCHAR(255) NOT NULL,
                    employ_contact_number VARCHAR(20) NOT NULL,
                    employ_email_address VARCHAR(255) NOT NULL
                )
            """)
            self.cursor.execute("SHOW COLUMNS FROM employ LIKE 'hourly_rate'")
            if not self.cursor.fetchone():
                self.cursor.execute("ALTER TABLE employ ADD COLUMN hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 0")
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS subconsultant (
                    subconsultant_id VARCHAR(50) PRIMARY KEY,
                    subconsultant_name VARCHAR(255) NOT NULL,
                    subconsultant_contact_number VARCHAR(20) NOT NULL,
                    subconsultant_email_address VARCHAR(255) NOT NULL,
                    hourly_rate DECIMAL(10,2) NOT NULL
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            self.show_status_message(f"Error creating or modifying tables: {err}", error=True)

    def create_styles(self):
        self.master.option_add('*Font', ('Segoe UI', 10))
        style = ttk.Style()
        style.theme_use('clam')
        accent = "#0066cc"
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabelframe', background='#ffffff')
        style.configure('TLabel', background='#ffffff', foreground='#000000')
        style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        style.configure('Accent.TButton', background=accent, foreground='#ffffff', font=('Segoe UI', 10, 'bold'), padding=8)
        style.map('Accent.TButton', background=[('active', '#004d99')], foreground=[('active', '#ffffff')])
        style.configure('Treeview', background='#ffffff', foreground='#000000', fieldbackground='#ffffff', rowheight=28, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background=accent, foreground='#ffffff', font=('Segoe UI', 11, 'bold'))
        style.map('Treeview.Heading', background=[('active', '#004d99')])

    def create_employ_widgets(self):
        parent = self.employ_tab
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Employ Details", padding=15)
        frm.pack(fill='x', padx=10, pady=10)

        labels = ["Employ ID:", "Employ Name:", "Contact Number:", "Email Address:", "Hourly Rate:"]
        entries = []
        for i, text in enumerate(labels):
            ttk.Label(frm, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(frm, style='TEntry')
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries.append(entry)
        self.employ_id_entry, self.employ_name_entry, self.employ_contact_entry, self.employ_email_entry, self.employ_hourly_rate_entry = entries

        btn_frm = ttk.Frame(parent)
        btn_frm.pack(fill='x', padx=10, pady=10)
        btn_frm.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(btn_frm, text="Add Employ", command=self.add_employ, style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(btn_frm, text="Update Employ", command=self.update_employ, style='Accent.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(btn_frm, text="Delete Employ", command=self.delete_employ, style='Accent.TButton').grid(row=0, column=2, padx=5)

        tv_frm = ttk.LabelFrame(parent, text="Employ List", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Employ ID", "Name", "Contact Number", "Email Address", "Hourly Rate")
        self.employ_tree = ttk.Treeview(tv_frm, columns=cols, show="headings")
        widths = [100, 180, 130, 180, 100]
        for c, w in zip(cols, widths):
            self.employ_tree.heading(c, text=c)
            self.employ_tree.column(c, width=w, anchor='center' if c == "Employ ID" else 'w')
        self.employ_tree.pack(side='left', fill='both', expand=True)
        self.employ_tree.bind("<<TreeviewSelect>>", lambda e: self.on_employ_select())
        scrollbar = ttk.Scrollbar(tv_frm, orient='vertical', command=self.employ_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.employ_tree.configure(yscrollcommand=scrollbar.set)

    def populate_employ_list(self):
        for item in self.employ_tree.get_children():
            self.employ_tree.delete(item)
        try:
            self.cursor.execute("SELECT employ_id, employ_name, employ_contact_number, employ_email_address, hourly_rate FROM employ ORDER BY employ_name")
            for row in self.cursor.fetchall():
                self.employ_tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading employs: {e}", error=True)

    def add_employ(self):
        eid = self.employ_id_entry.get().strip()
        name = self.employ_name_entry.get().strip()
        contact = self.employ_contact_entry.get().strip()
        email = self.employ_email_entry.get().strip()
        rate = self.employ_hourly_rate_entry.get().strip()
        if not eid or not name or not contact or not email or not rate:
            return self.show_status_message("All fields are required", error=True)
        try:
            rate_val = float(rate)
            if rate_val <= 0:
                raise ValueError
        except:
            return self.show_status_message("Hourly Rate must be a positive number", error=True)
        try:
            self.cursor.execute(
                "INSERT INTO employ (employ_id, employ_name, employ_contact_number, employ_email_address, hourly_rate) VALUES (%s, %s, %s, %s, %s)",
                (eid, name, contact, email, rate_val)
            )
            self.conn.commit()
            self.show_status_message(f"Employ '{name}' added")
            self.clear_employ_input()
            self.populate_employ_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding employ: {e}", error=True)

    def update_employ(self):
        selected = self.employ_tree.selection()
        if not selected:
            return self.show_status_message("Select an employ entry to update", error=True)
        eid = self.employ_id_entry.get().strip()
        name = self.employ_name_entry.get().strip()
        contact = self.employ_contact_entry.get().strip()
        email = self.employ_email_entry.get().strip()
        rate = self.employ_hourly_rate_entry.get().strip()
        if not eid or not name or not contact or not email or not rate:
            return self.show_status_message("All fields are required", error=True)
        try:
            rate_val = float(rate)
            if rate_val <= 0:
                raise ValueError
        except:
            return self.show_status_message("Hourly Rate must be a positive number", error=True)
        try:
            self.cursor.execute(
                "UPDATE employ SET employ_name=%s, employ_contact_number=%s, employ_email_address=%s, hourly_rate=%s WHERE employ_id=%s",
                (name, contact, email, rate_val, eid)
            )
            self.conn.commit()
            self.show_status_message(f"Employ '{name}' updated")
            self.clear_employ_input()
            self.populate_employ_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating employ: {e}", error=True)

    def delete_employ(self):
        selected = self.employ_tree.selection()
        if not selected:
            return self.show_status_message("Select an employ entry to delete", error=True)
        eid = self.employ_tree.item(selected[0])['values'][0]
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employ ID '{eid}'?"):
            return
        try:
            self.cursor.execute("DELETE FROM employ WHERE employ_id=%s", (eid,))
            self.conn.commit()
            self.show_status_message("Employ deleted")
            self.clear_employ_input()
            self.populate_employ_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting employ: {e}", error=True)

    def on_employ_select(self):
        selected = self.employ_tree.selection()
        if not selected:
            return
        vals = self.employ_tree.item(selected[0])['values']
        self.employ_id_entry.delete(0, tk.END)
        self.employ_id_entry.insert(0, vals[0])
        self.employ_name_entry.delete(0, tk.END)
        self.employ_name_entry.insert(0, vals[1])
        self.employ_contact_entry.delete(0, tk.END)
        self.employ_contact_entry.insert(0, vals[2])
        self.employ_email_entry.delete(0, tk.END)
        self.employ_email_entry.insert(0, vals[3])
        self.employ_hourly_rate_entry.delete(0, tk.END)
        self.employ_hourly_rate_entry.insert(0, vals[4])

    def clear_employ_input(self):
        self.employ_id_entry.delete(0, tk.END)
        self.employ_name_entry.delete(0, tk.END)
        self.employ_contact_entry.delete(0, tk.END)
        self.employ_email_entry.delete(0, tk.END)
        self.employ_hourly_rate_entry.delete(0, tk.END)

    def create_subconsultant_widgets(self):
        parent = self.subconsultant_tab
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Subconsultant Details", padding=15)
        frm.pack(fill='x', padx=10, pady=10)

        labels = ["Subconsultant ID:", "Subconsultant Name:", "Contact Number:", "Email Address:", "Hourly Rate:"]
        entries = []
        for i, text in enumerate(labels):
            ttk.Label(frm, text=text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(frm, style='TEntry')
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            entries.append(entry)
        self.subconsultant_id_entry, self.subconsultant_name_entry, self.subconsultant_contact_entry, self.subconsultant_email_entry, self.subconsultant_hourly_rate_entry = entries

        btn_frm = ttk.Frame(parent)
        btn_frm.pack(fill='x', padx=10, pady=10)
        btn_frm.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(btn_frm, text="Add Subconsultant", command=self.add_subconsultant, style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(btn_frm, text="Update Subconsultant", command=self.update_subconsultant, style='Accent.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(btn_frm, text="Delete Subconsultant", command=self.delete_subconsultant, style='Accent.TButton').grid(row=0, column=2, padx=5)

        tv_frm = ttk.LabelFrame(parent, text="Subconsultant List", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Subconsultant ID", "Name", "Contact Number", "Email Address", "Hourly Rate")
        self.subconsultant_tree = ttk.Treeview(tv_frm, columns=cols, show="headings")
        widths = [120, 180, 130, 180, 100]
        for c, w in zip(cols, widths):
            self.subconsultant_tree.heading(c, text=c)
            self.subconsultant_tree.column(c, width=w, anchor='center' if 'ID' in c else 'w')
        self.subconsultant_tree.pack(side='left', fill='both', expand=True)
        self.subconsultant_tree.bind("<<TreeviewSelect>>", lambda e: self.on_subconsultant_select())
        scrollbar = ttk.Scrollbar(tv_frm, orient='vertical', command=self.subconsultant_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.subconsultant_tree.configure(yscrollcommand=scrollbar.set)

    def populate_subconsultant_list(self):
        for item in self.subconsultant_tree.get_children():
            self.subconsultant_tree.delete(item)
        try:
            self.cursor.execute("SELECT subconsultant_id, subconsultant_name, subconsultant_contact_number, subconsultant_email_address, hourly_rate FROM subconsultant ORDER BY subconsultant_name")
            for row in self.cursor.fetchall():
                self.subconsultant_tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading subconsultants: {e}", error=True)

    def add_subconsultant(self):
        sid = self.subconsultant_id_entry.get().strip()
        name = self.subconsultant_name_entry.get().strip()
        contact = self.subconsultant_contact_entry.get().strip()
        email = self.subconsultant_email_entry.get().strip()
        rate = self.subconsultant_hourly_rate_entry.get().strip()
        if not sid or not name or not contact or not email or not rate:
            return self.show_status_message("All fields are required", error=True)
        try:
            rate_val = float(rate)
            if rate_val <= 0:
                raise ValueError
        except:
            return self.show_status_message("Hourly Rate must be a positive number", error=True)
        try:
            self.cursor.execute(
                "INSERT INTO subconsultant (subconsultant_id, subconsultant_name, subconsultant_contact_number, subconsultant_email_address, hourly_rate) VALUES (%s, %s, %s, %s, %s)",
                (sid, name, contact, email, rate_val)
            )
            self.conn.commit()
            self.show_status_message(f"Subconsultant '{name}' added")
            self.clear_subconsultant_input()
            self.populate_subconsultant_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding subconsultant: {e}", error=True)

    def update_subconsultant(self):
        selected = self.subconsultant_tree.selection()
        if not selected:
            return self.show_status_message("Select a subconsultant entry to update", error=True)
        sid = self.subconsultant_id_entry.get().strip()
        name = self.subconsultant_name_entry.get().strip()
        contact = self.subconsultant_contact_entry.get().strip()
        email = self.subconsultant_email_entry.get().strip()
        rate = self.subconsultant_hourly_rate_entry.get().strip()
        if not sid or not name or not contact or not email or not rate:
            return self.show_status_message("All fields are required", error=True)
        try:
            rate_val = float(rate)
            if rate_val <= 0:
                raise ValueError
        except:
            return self.show_status_message("Hourly Rate must be a positive number", error=True)
        try:
            self.cursor.execute(
                "UPDATE subconsultant SET subconsultant_name=%s, subconsultant_contact_number=%s, subconsultant_email_address=%s, hourly_rate=%s WHERE subconsultant_id=%s",
                (name, contact, email, rate_val, sid)
            )
            self.conn.commit()
            self.show_status_message(f"Subconsultant '{name}' updated")
            self.clear_subconsultant_input()
            self.populate_subconsultant_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating subconsultant: {e}", error=True)

    def delete_subconsultant(self):
        selected = self.subconsultant_tree.selection()
        if not selected:
            return self.show_status_message("Select a subconsultant entry to delete", error=True)
        sid = self.subconsultant_tree.item(selected[0])['values'][0]
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete subconsultant ID '{sid}'?"):
            return
        try:
            self.cursor.execute("DELETE FROM subconsultant WHERE subconsultant_id=%s", (sid,))
            self.conn.commit()
            self.show_status_message("Subconsultant deleted")
            self.clear_subconsultant_input()
            self.populate_subconsultant_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting subconsultant: {e}", error=True)

    def on_subconsultant_select(self):
        selected = self.subconsultant_tree.selection()
        if not selected:
            return
        vals = self.subconsultant_tree.item(selected[0])['values']
        self.subconsultant_id_entry.delete(0, tk.END)
        self.subconsultant_id_entry.insert(0, vals[0])
        self.subconsultant_name_entry.delete(0, tk.END)
        self.subconsultant_name_entry.insert(0, vals[1])
        self.subconsultant_contact_entry.delete(0, tk.END)
        self.subconsultant_contact_entry.insert(0, vals[2])
        self.subconsultant_email_entry.delete(0, tk.END)
        self.subconsultant_email_entry.insert(0, vals[3])
        self.subconsultant_hourly_rate_entry.delete(0, tk.END)
        self.subconsultant_hourly_rate_entry.insert(0, vals[4])

    def clear_subconsultant_input(self):
        self.subconsultant_id_entry.delete(0, tk.END)
        self.subconsultant_name_entry.delete(0, tk.END)
        self.subconsultant_contact_entry.delete(0, tk.END)
        self.subconsultant_email_entry.delete(0, tk.END)
        self.subconsultant_hourly_rate_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Employ & Subconsultant Manager")
    app = EmploySubconsultantManager(root)
    root.mainloop()
