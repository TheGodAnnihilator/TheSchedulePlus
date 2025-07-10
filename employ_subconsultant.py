import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os

class EmploySubconsultantManager:
    def __init__(self, master):
        self.master = master
        master.title("Employ & Subconsultant Manager")
        master.geometry("900x600")
        master.configure(bg="#ffffff")

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
            # Check if 'hourly_rate' exists in employ table, add if missing
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
        self.style = ttk.Style()
        self.style.theme_use('clam')

        accent_color = "#0066cc"
        self.style.configure('TFrame', background='#ffffff')
        self.style.configure('TLabelframe', background='#ffffff')
        self.style.configure('TLabel', background='#ffffff', foreground='#000000')
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        self.style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        self.style.configure('Accent.TButton', background=accent_color, foreground='#ffffff', font=('Segoe UI', 10, 'bold'), padding=8)
        self.style.map('Accent.TButton', background=[('active', '#004d99')], foreground=[('active', '#ffffff')])

        self.style.configure('Treeview', background='#ffffff', foreground='#000000', fieldbackground='#ffffff', rowheight=28,
                             font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', background=accent_color, foreground='#ffffff', font=('Segoe UI', 11, 'bold'))
        self.style.map('Treeview.Heading', background=[('active', '#004d99')])

    def load_db_config(self, config_file):
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            return None
        config.read(config_file)
        if 'mysql' not in config:
            return None
        db_config = {}
        for key in ['host', 'user', 'password', 'database']:
            if key not in config['mysql']:
                return None
            db_config[key] = config['mysql'][key]
        return db_config

    def show_status_message(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

    # Employ Tab Widgets and Methods
    def create_employ_widgets(self):
        parent = self.employ_tab
        parent.configure(style='TFrame')

        input_frame = ttk.LabelFrame(parent, text="Employ Details", padding=15)
        input_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(input_frame, text="Employ ID:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.employ_id_entry = ttk.Entry(input_frame, style='TEntry')
        self.employ_id_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Employ Name:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.employ_name_entry = ttk.Entry(input_frame, style='TEntry')
        self.employ_name_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Contact Number:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.employ_contact_entry = ttk.Entry(input_frame, style='TEntry')
        self.employ_contact_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Email Address:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.employ_email_entry = ttk.Entry(input_frame, style='TEntry')
        self.employ_email_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Hourly Rate:").grid(row=4, column=0, sticky='w', pady=5, padx=5)
        self.employ_hourly_rate_entry = ttk.Entry(input_frame, style='TEntry')
        self.employ_hourly_rate_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=5)

        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        buttons_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(buttons_frame, text="Add Employ", command=self.add_employ, style='Accent.TButton').grid(row=0, column=0, sticky='ew', padx=5)
        ttk.Button(buttons_frame, text="Update Employ", command=self.update_employ, style='Accent.TButton').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(buttons_frame, text="Delete Employ", command=self.delete_employ, style='Accent.TButton').grid(row=0, column=2, sticky='ew', padx=5)

        tree_frame = ttk.LabelFrame(parent, text="Employ List", padding=10)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Employ ID", "Name", "Contact Number", "Email Address", "Hourly Rate")
        self.employ_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        widths = [100, 180, 130, 180, 100]
        for col, width in zip(columns, widths):
            self.employ_tree.heading(col, text=col)
            self.employ_tree.column(col, width=width, anchor='center' if col == "Employ ID" else 'w')
        self.employ_tree.pack(side='left', fill='both', expand=True)
        self.employ_tree.bind("<<TreeviewSelect>>", self.on_employ_select)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.employ_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.employ_tree.configure(yscrollcommand=scrollbar.set)

    def clear_employ_input(self):
        self.employ_id_entry.delete(0, tk.END)
        self.employ_name_entry.delete(0, tk.END)
        self.employ_contact_entry.delete(0, tk.END)
        self.employ_email_entry.delete(0, tk.END)
        self.employ_hourly_rate_entry.delete(0, tk.END)

    def populate_employ_list(self):
        for item in self.employ_tree.get_children():
            self.employ_tree.delete(item)
        try:
            self.cursor.execute("SELECT employ_id, employ_name, employ_contact_number, employ_email_address, hourly_rate FROM employ ORDER BY employ_name")
            rows = self.cursor.fetchall()
            for row in rows:
                self.employ_tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading employs: {e}", error=True)

    def add_employ(self):
        eid = self.employ_id_entry.get().strip()
        name = self.employ_name_entry.get().strip()
        contact = self.employ_contact_entry.get().strip()
        email = self.employ_email_entry.get().strip()
        hourly_rate = self.employ_hourly_rate_entry.get().strip()

        if not eid or not name or not contact or not email or not hourly_rate:
            self.show_status_message("All fields are required", error=True)
            return

        try:
            hourly_rate_val = float(hourly_rate)
            if hourly_rate_val <= 0:
                raise ValueError
        except:
            self.show_status_message("Hourly Rate must be positive number", error=True)
            return

        try:
            self.cursor.execute(
                "INSERT INTO employ (employ_id, employ_name, employ_contact_number, employ_email_address, hourly_rate) VALUES (%s, %s, %s, %s, %s)",
                (eid, name, contact, email, hourly_rate_val)
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
            self.show_status_message("Select an employ entry to update", error=True)
            return

        eid = self.employ_id_entry.get().strip()
        name = self.employ_name_entry.get().strip()
        contact = self.employ_contact_entry.get().strip()
        email = self.employ_email_entry.get().strip()
        hourly_rate = self.employ_hourly_rate_entry.get().strip()

        if not eid or not name or not contact or not email or not hourly_rate:
            self.show_status_message("All fields are required", error=True)
            return

        try:
            hourly_rate_val = float(hourly_rate)
            if hourly_rate_val <= 0:
                raise ValueError
        except:
            self.show_status_message("Hourly Rate must be positive number", error=True)
            return

        try:
            self.cursor.execute(
                "UPDATE employ SET employ_name=%s, employ_contact_number=%s, employ_email_address=%s, hourly_rate=%s WHERE employ_id=%s",
                (name, contact, email, hourly_rate_val, eid)
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
            self.show_status_message("Select an employ entry to delete", error=True)
            return
        eid = self.employ_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employ ID '{eid}'?"):
            try:
                self.cursor.execute("DELETE FROM employ WHERE employ_id=%s", (eid,))
                self.conn.commit()
                self.show_status_message("Employ deleted")
                self.clear_employ_input()
                self.populate_employ_list()
            except mysql.connector.Error as e:
                self.show_status_message(f"Error deleting employ: {e}", error=True)

    def on_employ_select(self, event):
        selected = self.employ_tree.selection()
        if not selected:
            return
        item = self.employ_tree.item(selected[0])
        values = item['values']
        self.employ_id_entry.delete(0, tk.END)
        self.employ_id_entry.insert(0, values[0])
        self.employ_name_entry.delete(0, tk.END)
        self.employ_name_entry.insert(0, values[1])
        self.employ_contact_entry.delete(0, tk.END)
        self.employ_contact_entry.insert(0, values[2])
        self.employ_email_entry.delete(0, tk.END)
        self.employ_email_entry.insert(0, values[3])
        self.employ_hourly_rate_entry.delete(0, tk.END)
        self.employ_hourly_rate_entry.insert(0, values[4])

    # Subconsultant Tab Widgets and Methods
    def create_subconsultant_widgets(self):
        parent = self.subconsultant_tab
        parent.configure(style='TFrame')

        input_frame = ttk.LabelFrame(parent, text="Subconsultant Details", padding=15)
        input_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(input_frame, text="Subconsultant ID:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.subconsultant_id_entry = ttk.Entry(input_frame, style='TEntry')
        self.subconsultant_id_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Subconsultant Name:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.subconsultant_name_entry = ttk.Entry(input_frame, style='TEntry')
        self.subconsultant_name_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Contact Number:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.subconsultant_contact_entry = ttk.Entry(input_frame, style='TEntry')
        self.subconsultant_contact_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Email Address:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.subconsultant_email_entry = ttk.Entry(input_frame, style='TEntry')
        self.subconsultant_email_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=5)

        ttk.Label(input_frame, text="Hourly Rate:").grid(row=4, column=0, sticky='w', pady=5, padx=5)
        self.subconsultant_hourly_rate_entry = ttk.Entry(input_frame, style='TEntry')
        self.subconsultant_hourly_rate_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=5)

        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        buttons_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(buttons_frame, text="Add Subconsultant", command=self.add_subconsultant, style='Accent.TButton').grid(row=0, column=0, sticky='ew', padx=5)
        ttk.Button(buttons_frame, text="Update Subconsultant", command=self.update_subconsultant, style='Accent.TButton').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(buttons_frame, text="Delete Subconsultant", command=self.delete_subconsultant, style='Accent.TButton').grid(row=0, column=2, sticky='ew', padx=5)

        tree_frame = ttk.LabelFrame(parent, text="Subconsultant List", padding=10)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Subconsultant ID", "Name", "Contact Number", "Email Address", "Hourly Rate")
        self.subconsultant_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        widths = [120, 180, 130, 180, 100]
        for col, width in zip(columns, widths):
            self.subconsultant_tree.heading(col, text=col)
            self.subconsultant_tree.column(col, width=width, anchor='center' if 'ID' in col else 'w')
        self.subconsultant_tree.pack(side='left', fill='both', expand=True)
        self.subconsultant_tree.bind("<<TreeviewSelect>>", self.on_subconsultant_select)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.subconsultant_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.subconsultant_tree.configure(yscrollcommand=scrollbar.set)

    def clear_subconsultant_input(self):
        self.subconsultant_id_entry.delete(0, tk.END)
        self.subconsultant_name_entry.delete(0, tk.END)
        self.subconsultant_contact_entry.delete(0, tk.END)
        self.subconsultant_email_entry.delete(0, tk.END)
        self.subconsultant_hourly_rate_entry.delete(0, tk.END)

    def populate_subconsultant_list(self):
        for item in self.subconsultant_tree.get_children():
            self.subconsultant_tree.delete(item)
        try:
            self.cursor.execute("SELECT subconsultant_id, subconsultant_name, subconsultant_contact_number, subconsultant_email_address, hourly_rate FROM subconsultant ORDER BY subconsultant_name")
            rows = self.cursor.fetchall()
            for row in rows:
                self.subconsultant_tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading subconsultants: {e}", error=True)

    def add_subconsultant(self):
        sid = self.subconsultant_id_entry.get().strip()
        name = self.subconsultant_name_entry.get().strip()
        contact = self.subconsultant_contact_entry.get().strip()
        email = self.subconsultant_email_entry.get().strip()
        hourly_rate = self.subconsultant_hourly_rate_entry.get().strip()

        if not sid or not name or not contact or not email or not hourly_rate:
            self.show_status_message("All fields are required", error=True)
            return

        try:
            hourly_rate_val = float(hourly_rate)
            if hourly_rate_val <= 0:
                raise ValueError
        except:
            self.show_status_message("Hourly Rate must be positive number", error=True)
            return

        try:
            self.cursor.execute(
                "INSERT INTO subconsultant (subconsultant_id, subconsultant_name, subconsultant_contact_number, subconsultant_email_address, hourly_rate) VALUES (%s,%s,%s,%s,%s)",
                (sid, name, contact, email, hourly_rate_val)
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
            self.show_status_message("Select a subconsultant entry to update", error=True)
            return

        sid = self.subconsultant_id_entry.get().strip()
        name = self.subconsultant_name_entry.get().strip()
        contact = self.subconsultant_contact_entry.get().strip()
        email = self.subconsultant_email_entry.get().strip()
        hourly_rate = self.subconsultant_hourly_rate_entry.get().strip()

        if not sid or not name or not contact or not email or not hourly_rate:
            self.show_status_message("All fields are required", error=True)
            return

        try:
            hourly_rate_val = float(hourly_rate)
            if hourly_rate_val <= 0:
                raise ValueError
        except:
            self.show_status_message("Hourly Rate must be positive number", error=True)
            return

        try:
            self.cursor.execute(
                "UPDATE subconsultant SET subconsultant_name=%s, subconsultant_contact_number=%s, subconsultant_email_address=%s, hourly_rate=%s WHERE subconsultant_id=%s",
                (name, contact, email, hourly_rate_val, sid)
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
            self.show_status_message("Select a subconsultant entry to delete", error=True)
            return
        sid = self.subconsultant_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete subconsultant ID '{sid}'?"):
            try:
                self.cursor.execute("DELETE FROM subconsultant WHERE subconsultant_id=%s", (sid,))
                self.conn.commit()
                self.show_status_message("Subconsultant deleted")
                self.clear_subconsultant_input()
                self.populate_subconsultant_list()
            except mysql.connector.Error as e:
                self.show_status_message(f"Error deleting subconsultant: {e}", error=True)

    def on_subconsultant_select(self, event):
        selected = self.subconsultant_tree.selection()
        if not selected:
            return
        item = self.subconsultant_tree.item(selected[0])
        values = item['values']
        self.subconsultant_id_entry.delete(0, tk.END)
        self.subconsultant_id_entry.insert(0, values[0])
        self.subconsultant_name_entry.delete(0, tk.END)
        self.subconsultant_name_entry.insert(0, values[1])
        self.subconsultant_contact_entry.delete(0, tk.END)
        self.subconsultant_contact_entry.insert(0, values[2])
        self.subconsultant_email_entry.delete(0, tk.END)
        self.subconsultant_email_entry.insert(0, values[3])
        self.subconsultant_hourly_rate_entry.delete(0, tk.END)
        self.subconsultant_hourly_rate_entry.insert(0, values[4])

if __name__ == "__main__":
    root = tk.Tk()
    app = EmploySubconsultantManager(root)
    root.mainloop()
