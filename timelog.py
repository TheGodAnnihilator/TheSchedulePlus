# timelog.py

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os
from datetime import datetime
from tkcalendar import DateEntry

class TimeLogManager:
    """
    A GUI application to manage time logs for clients, projects, and tasks.
    It connects to a MySQL database to store and retrieve data.
    """
    DROP_TABLE_FIRST = False

    def __init__(self, master, status_callback=None):
        self.master = master
        # Status bar setup
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(master, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor='w', padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Database connection
        self.db_config = self.load_db_config('config.ini')
        if not self.db_config:
            self.show_status_message("Config file not found or invalid", error=True)
            master.after(5000, master.destroy)
            return
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            self.show_status_message("Database connection successful", error=False)
        except mysql.connector.Error as e:
            self.show_status_message(f"Database connection error: {e}", error=True)
            master.after(5000, master.destroy)
            return

        # Initialize components
        self.create_tables()
        self.create_styles()
        self.create_gui()
        self.populate_dropdowns()
        # Initially populate logs for today
        today = datetime.now().strftime('%Y-%m-%d')
        self.date_entry.set_date(today)
        self.populate_time_log_list(for_date=today)
        self.filter_date_entry.set_date(today)
        self.view_logs_by_date()

    def create_tables(self):
        if self.DROP_TABLE_FIRST:
            try:
                self.cursor.execute("DROP TABLE IF EXISTS time_log")
                self.conn.commit()
            except mysql.connector.Error as err:
                self.show_status_message(f"Error dropping time_log table: {err}", error=True)
        tables = {
            'client': """CREATE TABLE IF NOT EXISTS client (
                client_id VARCHAR(255) PRIMARY KEY,
                client_name VARCHAR(255) NOT NULL
            )""",
            'project': """CREATE TABLE IF NOT EXISTS project (
                project_no VARCHAR(255) PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
            )""",
            'task': """CREATE TABLE IF NOT EXISTS task (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                project_no VARCHAR(255) NOT NULL,
                task_name VARCHAR(255) NOT NULL,
                billable ENUM('Yes', 'No'),
                hourly_rate DECIMAL(10,2) DEFAULT NULL,
                lumpsum DECIMAL(10,2) DEFAULT NULL,
                FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE CASCADE
            )""",
            'employ': """CREATE TABLE IF NOT EXISTS employ (
                employ_id VARCHAR(50) PRIMARY KEY,
                employ_name VARCHAR(255) NOT NULL
            )""",
            'time_log': """CREATE TABLE IF NOT EXISTS time_log (
                log_id VARCHAR(512) PRIMARY KEY,
                log_date DATE NOT NULL,
                client_id VARCHAR(255),
                project_no VARCHAR(255),
                task_id INT,
                employ_id VARCHAR(50),
                hours DECIMAL(5,2) NOT NULL,
                notes TEXT DEFAULT NULL,
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE SET NULL,
                FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE SET NULL,
                FOREIGN KEY (task_id) REFERENCES task(task_id) ON DELETE SET NULL,
                FOREIGN KEY (employ_id) REFERENCES employ(employ_id) ON DELETE SET NULL
            )"""
        }
        for name, ddl in tables.items():
            try:
                self.cursor.execute(ddl)
            except mysql.connector.Error as err:
                self.show_status_message(f"Error creating {name} table: {err}", error=True)
        self.conn.commit()

    def create_styles(self):
        self.master.option_add('*Font', ('Segoe UI', 10))
        style = ttk.Style()
        style.theme_use('clam')
        accent = "#0066cc"
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff', foreground='#000000')
        style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000', padding=5, borderwidth=1, relief='solid')
        style.configure('Accent.TButton', background=accent, foreground='#ffffff', font=('Segoe UI', 10, 'bold'), padding=8)
        style.map('Accent.TButton', background=[('active', '#004d99')], foreground=[('active', '#ffffff')])
        style.configure('Treeview', background='#ffffff', foreground='#000000', rowheight=28, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background=accent, foreground='#ffffff', font=('Segoe UI', 11, 'bold'))
        style.configure('total', background='#e6f3ff', font=('Segoe UI', 10, 'bold'))

    def create_gui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs
        self.entry_tab = ttk.Frame(self.notebook)
        self.view_date_tab = ttk.Frame(self.notebook)
        self.project_report_tab = ttk.Frame(self.notebook)
        self.task_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.entry_tab, text="Time Log Entry")
        self.notebook.add(self.view_date_tab, text="View by Date")
        self.notebook.add(self.project_report_tab, text="Project Report")
        self.notebook.add(self.task_data_tab, text="Task Data")

        # Build each
        self._build_entry_tab()
        self._build_view_by_date_tab()
        self._build_project_report_tab()
        self._build_task_data_tab()

    def _build_entry_tab(self):
        frm = ttk.LabelFrame(self.entry_tab, text="Time Log Entry", padding=15)
        frm.pack(fill='x', padx=10, pady=10)
        frm.columnconfigure(1, weight=1)

        # Date picker
        ttk.Label(frm, text="Date:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.date_entry = DateEntry(frm, width=18, date_pattern='y-mm-dd')
        self.date_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.populate_time_log_list(for_date=self.date_entry.get()))

        # Client/Project/Task/Employee/Hours
        labels = ["Client:", "Project:", "Task:", "Employee:", "Hours:"]
        attr_names = ["client_combobox", "project_combobox", "task_combobox", "employ_combobox", "hours_entry"]
        widgets = [
            ttk.Combobox(frm, state='readonly', width=40),
            ttk.Combobox(frm, state='readonly', width=40),
            ttk.Combobox(frm, state='readonly', width=40),
            ttk.Combobox(frm, state='readonly', width=40),
            ttk.Entry(frm, width=18)
        ]
        for i, (lbl, name, w) in enumerate(zip(labels, attr_names, widgets), start=1):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            w.grid(row=i, column=1, sticky='ew', pady=5, padx=5)
            setattr(self, name, w)
        # Bind client/project/task
        self.client_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_client_selected())
        self.project_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_project_selected())

        # Notes
        ttk.Label(frm, text="Notes:").grid(row=6, column=0, sticky='nw', pady=5, padx=5)
        self.notes_text = tk.Text(frm, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.notes_text.grid(row=6, column=1, sticky='ew', pady=5, padx=5)

        # Buttons
        btn_frm = ttk.Frame(self.entry_tab, padding=15)
        btn_frm.pack(fill='x', padx=10, pady=10)
        btn_frm.columnconfigure((0,1,2,3), weight=1)
        ttk.Button(btn_frm, text="Add Entry", command=self.add_time_log, style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frm, text="Update Entry", command=self.update_time_log, style='Accent.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frm, text="Delete Entry", command=self.delete_time_log, style='Accent.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frm, text="Show All Logs", command=self.show_all_logs, style='Accent.TButton').grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Treeview
        tv_frm = ttk.LabelFrame(self.entry_tab, text="Time Log List", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Log ID","Date","Client","Project","Task","Employee","Hours","Notes")
        self.time_log_tree = ttk.Treeview(tv_frm, columns=cols, show="headings", style='Treeview')
        widths = {"Log ID":120,"Date":100,"Client":150,"Project":150,"Task":150,"Employee":120,"Hours":80,"Notes":200}
        for c in cols:
            self.time_log_tree.heading(c, text=c)
            self.time_log_tree.column(c, width=widths[c], anchor='center')
        self.time_log_tree.pack(expand=True, fill="both")
        self.time_log_tree.bind("<<TreeviewSelect>>", lambda e: self._on_time_log_select())

    def _build_view_by_date_tab(self):
        frm = ttk.LabelFrame(self.view_date_tab, text="Select Date", padding=10)
        frm.pack(fill='x', padx=10, pady=10)
        ttk.Label(frm, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_date_entry = DateEntry(frm, width=18, date_pattern='y-mm-dd')
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Button(frm, text="View", command=self.view_logs_by_date, style='Accent.TButton').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.total_hours_label = ttk.Label(frm, text="Total Hours: 0.00", font=('Segoe UI', 10, 'bold'))
        self.total_hours_label.grid(row=0, column=3, padx=10, pady=5, sticky='w')

        tv_frm = ttk.LabelFrame(self.view_date_tab, text="Time Logs for Selected Date", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Log ID","Date","Client","Project","Task","Employee","Hours","Notes")
        self.view_date_tree = ttk.Treeview(tv_frm, columns=cols, show="headings", style='Treeview')
        for c in cols:
            self.view_date_tree.heading(c, text=c)
            self.view_date_tree.column(c, width=100, anchor='center')
        self.view_date_tree.pack(expand=True, fill="both")

    def _build_project_report_tab(self):
        frm = ttk.LabelFrame(self.project_report_tab, text="Select Project", padding=10)
        frm.pack(fill='x', padx=10, pady=10)
        ttk.Label(frm, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_client_combobox = ttk.Combobox(frm, state='readonly', width=40)
        self.report_client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.report_client_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_report_client_selected())
        ttk.Label(frm, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.report_project_combobox = ttk.Combobox(frm, state='readonly', width=40)
        self.report_project_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        ttk.Button(frm, text="Generate Report", command=self.generate_project_report, style='Accent.TButton')\
            .grid(row=1, column=2, padx=10, pady=5, sticky='w')

        tv_frm = ttk.LabelFrame(self.project_report_tab, text="Project Tasks Report", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Task ID","Task Name","Start Date","End Date","Total Hours","Employees")
        self.report_tree = ttk.Treeview(tv_frm, columns=cols, show="headings", style='Treeview')
        widths = {"Task ID":100,"Task Name":200,"Start Date":100,"End Date":100,"Total Hours":100,"Employees":200}
        for c in cols:
            self.report_tree.heading(c, text=c)
            self.report_tree.column(c, width=widths[c], anchor='center')
        self.report_tree.pack(expand=True, fill="both")

    def _build_task_data_tab(self):
        frm = ttk.LabelFrame(self.task_data_tab, text="Select Date Range and Task", padding=10)
        frm.pack(fill='x', padx=10, pady=10)
        ttk.Label(frm, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.task_data_client_cb = ttk.Combobox(frm, state='readonly', width=32)
        self.task_data_client_cb.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.task_data_client_cb.bind("<<ComboboxSelected>>", lambda e: self._on_task_data_client_selected())
        ttk.Label(frm, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.task_data_project_cb = ttk.Combobox(frm, state='readonly', width=32)
        self.task_data_project_cb.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.task_data_project_cb.bind("<<ComboboxSelected>>", lambda e: self._on_task_data_project_selected())
        ttk.Label(frm, text="Task:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.task_data_task_cb = ttk.Combobox(frm, state='readonly', width=32)
        self.task_data_task_cb.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(frm, text="Start Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.task_start_date_entry = DateEntry(frm, width=18, date_pattern='y-mm-dd')
        self.task_start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        ttk.Label(frm, text="End Date:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.task_end_date_entry = DateEntry(frm, width=18, date_pattern='y-mm-dd')
        self.task_end_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        ttk.Button(frm, text="View Task Data", command=self.view_task_data, style='Accent.TButton')\
            .grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        tv_frm = ttk.LabelFrame(self.task_data_tab, text="Task Logs", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=10, pady=10)
        cols = ("Log ID","Date","Employee","Hours","Hourly Rate","Lumpsum","Log Amount","Notes")
        self.task_data_tree = ttk.Treeview(tv_frm, columns=cols, show="headings", style='Treeview')
        widths = {"Log ID":100,"Date":100,"Employee":120,"Hours":80,"Hourly Rate":90,"Lumpsum":90,"Log Amount":90,"Notes":200}
        for c in cols:
            self.task_data_tree.heading(c, text=c)
            self.task_data_tree.column(c, width=widths[c], anchor='center')
        self.task_data_tree.pack(expand=True, fill="both")
        # Totals
        tot_frm = ttk.Frame(tv_frm)
        tot_frm.pack(fill='x', pady=(5,0), anchor='w')
        self.task_total_hours_label = ttk.Label(tot_frm, text="Total Hours: 0.00", font=('Segoe UI', 10, 'bold'))
        self.task_total_hours_label.pack(side='left', padx=10)
        self.task_total_amount_label = ttk.Label(tot_frm, text="Total Amount: $0.00", font=('Segoe UI', 10, 'bold'))
        self.task_total_amount_label.pack(side='left', padx=10)

    # Utility methods
    def load_db_config(self, config_file):
        cfg = configparser.ConfigParser()
        if not os.path.exists(config_file): return None
        cfg.read(config_file)
        if 'mysql' not in cfg: return None
        sec = cfg['mysql']
        for k in ('host','user','password','database'):
            if k not in sec: return None
        return {k: sec[k] for k in ('host','user','password','database')}

    def show_status_message(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

    def _extract_id(self, text):
        if '(' in text and text.endswith(')'):
            return text.split('(')[-1][:-1]
        return None

    # Populate dropdowns & lists
    def populate_dropdowns(self):
        try:
            # Clients
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            clients = [f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            for cb in (self.client_combobox, self.report_client_combobox, self.task_data_client_cb):
                cb['values'] = clients
                if clients and not cb.get(): cb.set(clients[0])
            # Employees
            self.cursor.execute("SELECT employ_id, employ_name FROM employ ORDER BY employ_name")
            employs = [f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            self.employ_combobox['values'] = employs
            if employs and not self.employ_combobox.get(): self.employ_combobox.set(employs[0])
            # Trigger cascading
            self._on_client_selected()
            self._on_report_client_selected()
            self._on_task_data_client_selected()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error populating dropdowns: {e}", error=True)

    def populate_time_log_list(self, for_date=None):
        for i in self.time_log_tree.get_children():
            self.time_log_tree.delete(i)
        base = """
            SELECT tl.log_id, tl.log_date, c.client_name, p.project_name, t.task_name, e.employ_name, tl.hours, tl.notes,
                   c.client_id, p.project_no, t.task_id, e.employ_id
            FROM time_log tl
            LEFT JOIN client c ON tl.client_id=c.client_id
            LEFT JOIN project p ON tl.project_no=p.project_no
            LEFT JOIN task t ON tl.task_id=t.task_id
            LEFT JOIN employ e ON tl.employ_id=e.employ_id
        """
        params = ()
        if for_date:
            query = base + " WHERE tl.log_date=%s ORDER BY tl.log_id DESC"
            params = (for_date,)
            self.show_status_message(f"Showing logs for {for_date}", error=False)
        else:
            query = base + " ORDER BY tl.log_date DESC, tl.log_id DESC"
        try:
            self.cursor.execute(query, params)
            for row in self.cursor.fetchall():
                disp = [
                    row[0],
                    row[1].strftime("%Y-%m-%d") if row[1] else "",
                    f"{row[2]} ({row[8]})" if row[2] else row[8] or "",
                    f"{row[3]} ({row[9]})" if row[3] else row[9] or "",
                    f"{row[4]} ({row[10]})" if row[4] else row[10] or "",
                    f"{row[5]} ({row[11]})" if row[5] else row[11] or "",
                    f"{float(row[6]):.2f}" if row[6] else "0.00",
                    row[7] or ""
                ]
                self.time_log_tree.insert("", tk.END, values=disp)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading logs: {e}", error=True)

    def populate_project_dropdown(self, client_id, cb):
        if not client_id:
            cb['values']=(); cb.set(''); return
        try:
            self.cursor.execute("SELECT project_no, project_name FROM project WHERE client_id=%s ORDER BY project_name", (client_id,))
            vals = [f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            cb['values'] = vals
            if vals: cb.set(vals[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading projects: {e}", error=True)

    def populate_task_dropdown(self, project_no, cb):
        if not project_no:
            cb['values']=(); cb.set(''); return
        try:
            self.cursor.execute("SELECT task_id, task_name FROM task WHERE project_no=%s ORDER BY task_name", (project_no,))
            vals = [f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            cb['values']=vals
            if vals: cb.set(vals[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading tasks: {e}", error=True)

    # Event handlers
    def _on_client_selected(self):
        cid = self._extract_id(self.client_combobox.get())
        self.populate_project_dropdown(cid, self.project_combobox)
        self._on_project_selected()

    def _on_project_selected(self):
        pno = self._extract_id(self.project_combobox.get())
        self.populate_task_dropdown(pno, self.task_combobox)

    def _on_report_client_selected(self):
        cid = self._extract_id(self.report_client_combobox.get())
        self.populate_project_dropdown(cid, self.report_project_combobox)
        for i in self.report_tree.get_children(): self.report_tree.delete(i)

    def _on_task_data_client_selected(self):
        cid = self._extract_id(self.task_data_client_cb.get())
        self.populate_project_dropdown(cid, self.task_data_project_cb)
        self._on_task_data_project_selected()

    def _on_task_data_project_selected(self):
        pno = self._extract_id(self.task_data_project_cb.get())
        self.populate_task_dropdown(pno, self.task_data_task_cb)
        for i in self.task_data_tree.get_children(): self.task_data_tree.delete(i)

    def _on_time_log_select(self):
        sel = self.time_log_tree.selection()
        if not sel: return
        vals = self.time_log_tree.item(sel[0])['values']
        # Restore date
        try:
            self.date_entry.set_date(vals[1])
        except:
            pass
        # Populate combos
        for attr, v in zip(
            ('client_combobox','project_combobox','task_combobox','employ_combobox','hours_entry'),
            vals[2:7]
        ):
            w = getattr(self, attr)
            if isinstance(w, ttk.Entry):
                w.delete(0,tk.END); w.insert(0, v)
            else:
                w.set(v)
                if attr=='client_combobox': self._on_client_selected()
                if attr=='project_combobox': self._on_project_selected()
        # Notes
        self.notes_text.delete('1.0',tk.END); self.notes_text.insert('1.0', vals[7])

    # CRUD operations
    def add_time_log(self):
        date = self.date_entry.get()
        cid = self._extract_id(self.client_combobox.get())
        pno = self._extract_id(self.project_combobox.get())
        tid = self._extract_id(self.task_combobox.get())
        eid = self._extract_id(self.employ_combobox.get())
        hrs = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0',tk.END).strip()
        if not all([date,cid,pno,tid,eid,hrs]):
            return self.show_status_message("All fields except notes are required", error=True)
        try:
            hrs_f = float(hrs)
            if hrs_f <= 0: raise ValueError
        except:
            return self.show_status_message("Hours must be a positive number", error=True)

        log_id = f"{date.replace('-','')}-{tid}-{eid}-{datetime.now().strftime('%H%M%S%f')}"
        try:
            self.cursor.execute(
                "INSERT INTO time_log(log_id,log_date,client_id,project_no,task_id,employ_id,hours,notes) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (log_id,date,cid,pno,tid,eid,hrs_f, notes or None)
            )
            self.conn.commit()
            self.show_status_message("Time log entry added successfully")
            # Refresh lists and dropdowns
            self.populate_dropdowns()
            self.populate_time_log_list(for_date=date)
            self.view_logs_by_date()
            # Restore date, clear others
            self.date_entry.set_date(date)
            self.hours_entry.delete(0,tk.END)
            self.notes_text.delete('1.0',tk.END)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding time log: {e}", error=True)

    def update_time_log(self):
        sel = self.time_log_tree.selection()
        if not sel: return self.show_status_message("Please select a log to update", error=True)
        old_id = self.time_log_tree.item(sel[0])['values'][0]
        date = self.date_entry.get()
        cid = self._extract_id(self.client_combobox.get())
        pno = self._extract_id(self.project_combobox.get())
        tid = self._extract_id(self.task_combobox.get())
        eid = self._extract_id(self.employ_combobox.get())
        hrs = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0',tk.END).strip()
        if not all([date,cid,pno,tid,eid,hrs]):
            return self.show_status_message("All fields must be filled", error=True)
        try:
            hrs_f = float(hrs)
            if hrs_f <= 0: raise ValueError
        except:
            return self.show_status_message("Hours must be a positive number", error=True)

        new_id = f"{date.replace('-','')}-{tid}-{eid}-{datetime.now().strftime('%H%M%S%f')}"
        try:
            self.cursor.execute(
                "UPDATE time_log SET log_id=%s,log_date=%s,client_id=%s,project_no=%s,task_id=%s,employ_id=%s,hours=%s,notes=%s "
                "WHERE log_id=%s",
                (new_id,date,cid,pno,tid,eid,hrs_f, notes or None, old_id)
            )
            self.conn.commit()
            self.show_status_message("Time log updated successfully")
            self.populate_dropdowns()
            self.populate_time_log_list(for_date=date)
            self.view_logs_by_date()
            self.date_entry.set_date(date)
            self.hours_entry.delete(0,tk.END)
            self.notes_text.delete('1.0',tk.END)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating time log: {e}", error=True)

    def delete_time_log(self):
        sel = self.time_log_tree.selection()
        if not sel: return self.show_status_message("Please select a log to delete", error=True)
        vals = self.time_log_tree.item(sel[0])['values']
        log_id, date = vals[0], vals[1]
        if not messagebox.askyesno("Confirm Delete", f"Delete time log {log_id}?"):
            return
        try:
            self.cursor.execute("DELETE FROM time_log WHERE log_id=%s", (log_id,))
            self.conn.commit()
            self.show_status_message("Time log deleted successfully")
            self.populate_time_log_list(for_date=date)
            self.view_logs_by_date()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting time log: {e}", error=True)

    def view_logs_by_date(self):
        date = self.filter_date_entry.get()
        for i in self.view_date_tree.get_children():
            self.view_date_tree.delete(i)
        try:
            self.cursor.execute("""
                SELECT tl.log_id, tl.log_date, c.client_name, p.project_name, t.task_name, e.employ_name, tl.hours, tl.notes
                FROM time_log tl
                LEFT JOIN client c ON tl.client_id=c.client_id
                LEFT JOIN project p ON tl.project_no=p.project_no
                LEFT JOIN task t ON tl.task_id=t.task_id
                LEFT JOIN employ e ON tl.employ_id=e.employ_id
                WHERE tl.log_date=%s ORDER BY tl.log_id
            """, (date,))
            rows = self.cursor.fetchall()
            total = 0.0
            for r in rows:
                total += float(r[6] or 0)
                disp = [
                    r[0], r[1].strftime("%Y-%m-%d"), r[2] or "", r[3] or "",
                    r[4] or "", r[5] or "", f"{float(r[6]):.2f}" if r[6] else "0.00", r[7] or ""
                ]
                self.view_date_tree.insert("", tk.END, values=disp)
            self.total_hours_label.config(text=f"Total Hours: {total:.2f}")
            self.show_status_message(f"Displaying logs for {date}")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading logs: {e}", error=True)

    def generate_project_report(self):
        proj = self.report_project_combobox.get()
        if not proj: return self.show_status_message("Please select a project first", error=True)
        pno = self._extract_id(proj)
        for i in self.report_tree.get_children(): self.report_tree.delete(i)
        try:
            self.cursor.execute("""
                SELECT t.task_id, t.task_name,
                       MIN(tl.log_date) AS start_date,
                       MAX(tl.log_date) AS end_date,
                       SUM(tl.hours) AS total_hours,
                       GROUP_CONCAT(DISTINCT e.employ_name SEPARATOR ', ') AS employees
                FROM task t
                LEFT JOIN time_log tl ON t.task_id=tl.task_id
                LEFT JOIN employ e ON tl.employ_id=e.employ_id
                WHERE t.project_no=%s
                GROUP BY t.task_id,t.task_name ORDER BY t.task_name
            """, (pno,))
            rows = self.cursor.fetchall()
            total=0.0
            if not rows:
                return self.show_status_message("No tasks/logs for this project")
            for r in rows:
                sh = r[2].strftime("%Y-%m-%d") if r[2] else "N/A"
                eh = r[3].strftime("%Y-%m-%d") if r[3] else "N/A"
                hrs = float(r[4] or 0)
                total+=hrs
                self.report_tree.insert("", tk.END, values=[
                    r[0], r[1], sh, eh, f"{hrs:.2f}", r[5] or ""
                ])
            self.report_tree.insert("", tk.END, values=["","PROJECT TOTAL","","",f"{total:.2f}",""], tags=('total',))
            self.show_status_message(f"Report generated for project {proj}")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error generating report: {e}", error=True)

    def view_task_data(self):
        task = self.task_data_task_cb.get()
        if not task: return self.show_status_message("Please select a task first", error=True)
        tid = self._extract_id(task)
        sd = self.task_start_date_entry.get()
        ed = self.task_end_date_entry.get()
        for i in self.task_data_tree.get_children():
            self.task_data_tree.delete(i)
        try:
            self.cursor.execute("SELECT hourly_rate,lumpsum FROM task WHERE task_id=%s", (tid,))
            hr, lump = self.cursor.fetchone() or (0,0)
            self.cursor.execute("""
                SELECT tl.log_id, tl.log_date, e.employ_name, tl.hours, tl.notes
                FROM time_log tl
                LEFT JOIN employ e ON tl.employ_id=e.employ_id
                WHERE tl.task_id=%s AND tl.log_date BETWEEN %s AND %s
                ORDER BY tl.log_date
            """, (tid, sd, ed))
            rows = self.cursor.fetchall()
            if not rows:
                self.task_total_hours_label.config(text="Total Hours: 0.00")
                self.task_total_amount_label.config(text="Total Amount: $0.00")
                return self.show_status_message("No logs in selected range")
            th, amt = 0.0, 0.0
            for r in rows:
                hrs = float(r[3] or 0)
                la = hrs * float(hr or 0)
                th += hrs; amt += la
                self.task_data_tree.insert("", tk.END, values=[
                    r[0], r[1].strftime("%Y-%m-%d"), r[2] or "", f"{hrs:.2f}",
                    f"${float(hr or 0):.2f}", f"${float(lump or 0):.2f}", f"${la:.2f}", r[4] or ""
                ])
            total_amt = lump if lump and lump>0 else amt
            self.task_total_hours_label.config(text=f"Total Hours: {th:.2f}")
            self.task_total_amount_label.config(text=f"Total Amount: ${total_amt:.2f}")
            self.show_status_message(f"Displaying {len(rows)} logs for task")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading task data: {e}", error=True)

    def show_all_logs(self):
        self.populate_time_log_list(for_date=None)
        self.show_status_message("Showing all time logs")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Time Log Manager")
    app = TimeLogManager(root)
    root.mainloop()
