import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os
from datetime import datetime
from tkcalendar import DateEntry


class TimeLogManager:
    DROP_TABLE_FIRST = False

    def __init__(self, master):
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
        except mysql.connector.Error as e:
            self.show_status_message(f"Database connection error: {e}", error=True)
            master.after(5000, master.destroy)
            return

        # Initialize application components
        self.create_tables()
        self.create_styles()
        self.create_gui()
        self.populate_dropdowns()
        self.populate_time_log_list()

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
                       client_name VARCHAR(255) NOT NULL)""",
            'project': """CREATE TABLE IF NOT EXISTS project (
                        project_no VARCHAR(20) PRIMARY KEY,
                        client_id VARCHAR(255) NOT NULL,
                        project_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE)""",
            'task': """CREATE TABLE IF NOT EXISTS task (
                      task_id INT AUTO_INCREMENT PRIMARY KEY,
                      project_no VARCHAR(20) NOT NULL,
                      task_name VARCHAR(255) NOT NULL,
                      FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE CASCADE)""",
            'employ': """CREATE TABLE IF NOT EXISTS employ (
                       employ_id INT PRIMARY KEY,
                       employ_name VARCHAR(255) NOT NULL)""",
            'time_log': """CREATE TABLE IF NOT EXISTS time_log (
                         log_id VARCHAR(512) PRIMARY KEY,
                         log_date DATE NOT NULL,
                         client_id VARCHAR(255),
                         project_no VARCHAR(20),
                         task_id INT,
                         employ_id VARCHAR(50),
                         hours DECIMAL(5,2) NOT NULL,
                         notes TEXT DEFAULT NULL,
                         FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE SET NULL,
                         FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE SET NULL,
                         FOREIGN KEY (task_id) REFERENCES task(task_id) ON DELETE SET NULL,
                         FOREIGN KEY (employ_id) REFERENCES employ(employ_id) ON DELETE SET NULL)"""
        }

        for table, query in tables.items():
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                self.show_status_message(f"Error creating {table} table: {err}", error=True)
        self.conn.commit()

    def create_styles(self):
        self.master.option_add('*Font', ('Segoe UI', 10))
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        accent_color = "#0066cc"
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff', foreground='#000000')

        # Entry/combobox styling
        entry_style = {
            'fieldbackground': '#ffffff',
            'foreground': '#000000',
            'padding': 5,
            'borderwidth': 1,
            'relief': 'solid'
        }
        style.configure('TEntry', **entry_style)
        style.configure('TCombobox', **entry_style)

        # Button styling
        style.configure('Accent.TButton',
                        background=accent_color,
                        foreground='#ffffff',
                        font=('Segoe UI', 10, 'bold'),
                        padding=8)
        style.map('Accent.TButton',
                  background=[('active', '#004d99')],
                  foreground=[('active', '#ffffff')])

        # Treeview styling
        style.configure('Treeview',
                        background='#ffffff',
                        foreground='#000000',
                        rowheight=28,
                        font=('Segoe UI', 10))
        style.configure('Treeview.Heading',
                        background=accent_color,
                        foreground='#ffffff',
                        font=('Segoe UI', 11, 'bold'))
        style.configure('Total.Treeview',
                        background='#e6f3ff',
                        font=('Segoe UI', 10, 'bold'))

    def create_gui(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create tabs
        self.entry_tab = ttk.Frame(self.notebook)
        self.view_date_tab = ttk.Frame(self.notebook)
        self.project_report_tab = ttk.Frame(self.notebook)
        self.task_data_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.entry_tab, text="Time Log Entry")
        self.notebook.add(self.view_date_tab, text="View by Date")
        self.notebook.add(self.project_report_tab, text="Project Report")
        self.notebook.add(self.task_data_tab, text="Task Data")

        # Build widgets for each tab
        self.create_time_log_widgets(self.entry_tab)
        self.create_view_by_date_widgets(self.view_date_tab)
        self.create_project_report_widgets(self.project_report_tab)
        self.create_task_data_widgets(self.task_data_tab)

    def create_time_log_widgets(self, parent):
        """Create widgets for the time log entry tab"""
        input_frame = ttk.LabelFrame(parent, text="Time Log Entry", padding=15)
        input_frame.pack(fill='x', padx=10, pady=10)

        # Create fields for time log entry
        fields = [
            ("Date:", "date_entry", DateEntry(input_frame, width=18)),
            ("Client:", "client_combobox", ttk.Combobox(input_frame, state='readonly', width=40)),
            ("Project:", "project_combobox", ttk.Combobox(input_frame, state='readonly', width=40)),
            ("Task:", "task_combobox", ttk.Combobox(input_frame, state='readonly', width=40)),
            ("Employee:", "employ_combobox", ttk.Combobox(input_frame, state='readonly', width=40)),
            ("Hours:", "hours_entry", ttk.Entry(input_frame, width=18))
        ]

        for row, (label_text, attr_name, widget) in enumerate(fields):
            ttk.Label(input_frame, text=label_text).grid(row=row, column=0, sticky='w', pady=5, padx=5)
            widget.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            setattr(self, attr_name, widget)

        # Notes field
        ttk.Label(input_frame, text="Notes:").grid(row=6, column=0, sticky='w', pady=5, padx=5)
        self.notes_text = tk.Text(input_frame, height=4, width=35, wrap='word',
                                  relief='solid', borderwidth=1)
        self.notes_text.grid(row=6, column=1, sticky='ew', pady=5, padx=5)

        # Bind events
        self.client_combobox.bind("<<ComboboxSelected>>", self.on_client_selected)
        self.project_combobox.bind("<<ComboboxSelected>>", self.on_project_selected)

        # Action buttons
        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        buttons_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(buttons_frame, text="Add Entry",
                   command=self.add_time_log,
                   style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Update Entry",
                   command=self.update_time_log,
                   style='Accent.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Delete Entry",
                   command=self.delete_time_log,
                   style='Accent.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Time log list
        list_frame = ttk.LabelFrame(parent, text="Time Log List", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Client", "Project", "Task", "Employee", "Hours", "Notes")
        self.time_log_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        # Configure columns
        col_widths = {
            "Log ID": 120,
            "Date": 100,
            "Client": 150,
            "Project": 150,
            "Task": 150,
            "Employee": 120,
            "Hours": 80,
            "Notes": 200
        }

        for col in columns:
            self.time_log_tree.heading(col, text=col)
            self.time_log_tree.column(col, width=col_widths[col], anchor='center')

        self.time_log_tree.pack(expand=True, fill="both")
        self.time_log_tree.bind("<<TreeviewSelect>>", self.on_time_log_select)

    def create_view_by_date_widgets(self, parent):
        """Create widgets for viewing logs by date"""
        control_frame = ttk.LabelFrame(parent, text="Select Date", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Date selection
        ttk.Label(control_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_date_entry = DateEntry(control_frame, width=18)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # View button
        self.view_date_button = ttk.Button(control_frame, text="View",
                                           command=self.view_logs_by_date,
                                           style='Accent.TButton')
        self.view_date_button.grid(row=0, column=2, padx=10, pady=5, sticky='w')

        # Total hours label
        self.total_hours_label = ttk.Label(control_frame, text="Total Hours: 0.00",
                                           font=('Segoe UI', 10, 'bold'))
        self.total_hours_label.grid(row=0, column=3, padx=10, pady=5, sticky='w')

        # Logs list
        list_frame = ttk.LabelFrame(parent, text="Time Logs for Selected Date", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Client", "Project", "Task", "Employee", "Hours", "Notes")
        self.view_date_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        # Configure columns
        col_widths = {
            "Log ID": 120,
            "Date": 100,
            "Client": 150,
            "Project": 150,
            "Task": 150,
            "Employee": 120,
            "Hours": 80,
            "Notes": 200
        }

        for col in columns:
            self.view_date_tree.heading(col, text=col)
            self.view_date_tree.column(col, width=col_widths[col], anchor='center')

        self.view_date_tree.pack(expand=True, fill="both")

    def create_project_report_widgets(self, parent):
        """Create widgets for project reports tab"""
        control_frame = ttk.LabelFrame(parent, text="Select Project", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Client selection
        ttk.Label(control_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_client_combobox = ttk.Combobox(control_frame, state='readonly', width=40)
        self.report_client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.report_client_combobox.bind("<<ComboboxSelected>>", self.on_report_client_selected)

        # Project selection
        ttk.Label(control_frame, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.report_project_combobox = ttk.Combobox(control_frame, state='readonly', width=40)
        self.report_project_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.report_project_combobox.bind("<<ComboboxSelected>>", self.on_report_project_selected)

        # Generate report button
        self.generate_report_button = ttk.Button(control_frame, text="Generate Report",
                                                 command=self.generate_project_report,
                                                 style='Accent.TButton')
        self.generate_report_button.grid(row=1, column=2, padx=10, pady=5, sticky='w')

        # Report display
        report_frame = ttk.LabelFrame(parent, text="Project Tasks Report", padding=10)
        report_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Task ID", "Task Name", "Start Date", "End Date", "Total Hours", "Employees")
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show="headings", style='Treeview')

        # Configure columns
        col_widths = {
            "Task ID": 100,
            "Task Name": 200,
            "Start Date": 100,
            "End Date": 100,
            "Total Hours": 100,
            "Employees": 200
        }

        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=col_widths[col], anchor='center')

        self.report_tree.pack(expand=True, fill="both")

    def create_task_data_widgets(self, parent):
        """Create widgets for task data tab"""
        control_frame = ttk.LabelFrame(parent, text="Select Date Range and Task", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Client selection
        ttk.Label(control_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.task_data_client_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_client_cb.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.task_data_client_cb.bind("<<ComboboxSelected>>", self.on_task_data_client_selected)

        # Project selection (dependent on client)
        ttk.Label(control_frame, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.task_data_project_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_project_cb.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.task_data_project_cb.bind("<<ComboboxSelected>>", self.on_task_data_project_selected)

        # Task selection (dependent on project)
        ttk.Label(control_frame, text="Task:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.task_data_task_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_task_cb.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Date range selection
        ttk.Label(control_frame, text="Start Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.task_start_date_entry = DateEntry(control_frame, width=18)
        self.task_start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(control_frame, text="End Date:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.task_end_date_entry = DateEntry(control_frame, width=18)
        self.task_end_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # View button
        self.view_task_data_button = ttk.Button(control_frame, text="View Task Data",
                                                command=self.view_task_data,
                                                style='Accent.TButton')
        self.view_task_data_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        # Task data display
        list_frame = ttk.LabelFrame(parent, text="Task Logs", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Client", "Project", "Task", "Employee", "Hours", "Notes")
        self.task_data_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        # Configure columns
        col_widths = {
            "Log ID": 120,
            "Date": 100,
            "Client": 150,
            "Project": 150,
            "Task": 150,
            "Employee": 120,
            "Hours": 80,
            "Notes": 200
        }

        for col in columns:
            self.task_data_tree.heading(col, text=col)
            self.task_data_tree.column(col, width=col_widths[col], anchor='center')

        self.task_data_tree.pack(expand=True, fill="both")

    def populate_dropdowns(self):
        """Populate all combobox dropdowns with database data"""
        try:
            # Clients dropdown
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            clients = self.cursor.fetchall()
            client_names = [f"{cli[1]} ({cli[0]})" for cli in clients]

            # Set values for all client comboboxes
            self.client_combobox['values'] = client_names
            self.report_client_combobox['values'] = client_names
            self.task_data_client_cb['values'] = client_names

            if client_names:
                self.client_combobox.current(0)
                self.on_client_selected()
                self.report_client_combobox.current(0)
                self.task_data_client_cb.current(0)

            # Employees dropdown
            self.cursor.execute("SELECT employ_id, employ_name FROM employ ORDER BY employ_name")
            employs = self.cursor.fetchall()
            employ_names = [f"{employ[1]} ({employ[0]})" for employ in employs]
            self.employ_combobox['values'] = employ_names
            if employ_names:
                self.employ_combobox.current(0)

        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching dropdown data: {err}", error=True)

    def populate_time_log_list(self):
        """Populate the main time log list with all entries"""
        self.time_log_tree.delete(*self.time_log_tree.get_children())
        try:
            self.cursor.execute("""
                SELECT log_id, log_date, client_id, project_no, task_id, employ_id, hours, notes
                FROM time_log ORDER BY log_date DESC
            """)
            logs = self.cursor.fetchall()

            for log in logs:
                client_name = self.fetch_name("client", log[2], "client_id", "client_name")
                project_name = self.fetch_name("project", log[3], "project_no", "project_name")
                task_name = self.fetch_name("task", log[4], "task_id", "task_name")
                employ_name = self.fetch_name("employ", log[5], "employ_id", "employ_name")

                self.time_log_tree.insert("", tk.END, values=(
                    log[0],
                    log[1].strftime("%Y-%m-%d") if log[1] else "",
                    client_name,
                    project_name,
                    task_name,
                    employ_name,
                    f"{log[6]:.2f}",
                    log[7] if log[7] else ""
                ))

        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading time logs: {err}", error=True)

    def populate_project_dropdown(self, client_id, project_combobox):
        """Populate projects dropdown based on selected client"""
        if not client_id:
            project_combobox['values'] = []
            project_combobox.set('')
            return

        try:
            self.cursor.execute("""
                SELECT project_no, project_name FROM project 
                WHERE client_id=%s ORDER BY project_name
            """, (client_id,))
            projects = self.cursor.fetchall()
            project_names = [f"{proj[1]} ({proj[0]})" for proj in projects]
            project_combobox['values'] = project_names
            if project_names:
                project_combobox.current(0)
        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching projects: {err}", error=True)

    def populate_task_dropdown(self, project_no, task_combobox):
        """Populate tasks dropdown based on selected project"""
        if not project_no:
            task_combobox['values'] = []
            task_combobox.set('')
            return

        try:
            self.cursor.execute("""
                SELECT task_id, task_name FROM task 
                WHERE project_no=%s ORDER BY task_name
            """, (project_no,))
            tasks = self.cursor.fetchall()
            task_names = [f"{task[1]} ({task[0]})" for task in tasks]
            task_combobox['values'] = task_names
            if task_names:
                task_combobox.current(0)
        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching tasks: {err}", error=True)

    def on_client_selected(self, event=None):
        """Handle client selection in time log entry tab"""
        client_name_with_id = self.client_combobox.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.project_combobox)
        # Clear task dropdown when client changes
        self.task_combobox.set('')
        self.task_combobox['values'] = []

    def on_project_selected(self, event=None):
        """Handle project selection in time log entry tab"""
        project_name_with_no = self.project_combobox.get()
        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.populate_task_dropdown(project_no, self.task_combobox)

    def on_report_client_selected(self, event=None):
        """Handle client selection in project report tab"""
        client_name_with_id = self.report_client_combobox.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.report_project_combobox)
        # Clear report when client changes
        self.report_tree.delete(*self.report_tree.get_children())

    def on_report_project_selected(self, event=None):
        """Handle project selection in project report tab"""
        self.report_tree.delete(*self.report_tree.get_children())

    def on_task_data_client_selected(self, event=None):
        """Handle client selection in task data tab"""
        client_name_with_id = self.task_data_client_cb.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.task_data_project_cb)
        # Clear task dropdown when client changes
        self.task_data_task_cb.set('')
        self.task_data_task_cb['values'] = []
        # Clear task data
        self.task_data_tree.delete(*self.task_data_tree.get_children())

    def on_task_data_project_selected(self, event=None):
        """Handle project selection in task data tab"""
        project_name_with_no = self.task_data_project_cb.get()
        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.populate_task_dropdown(project_no, self.task_data_task_cb)
        # Clear task data when project changes
        self.task_data_tree.delete(*self.task_data_tree.get_children())

    def on_time_log_select(self, event):
        """Handle selection of a time log entry"""
        selected = self.time_log_tree.selection()
        if not selected:
            return

        item = self.time_log_tree.item(selected[0])
        values = item['values']

        try:
            self.date_entry.set_date(datetime.strptime(values[1], "%Y-%m-%d"))
        except (ValueError, TypeError):
            self.date_entry.set_date(datetime.now())

        self.set_combobox_value(self.client_combobox, values[2])
        client_id = self._extract_id_from_combobox(self.client_combobox.get())
        self.populate_project_dropdown(client_id, self.project_combobox)

        self.set_combobox_value(self.project_combobox, values[3])
        project_no = self._extract_id_from_combobox(self.project_combobox.get())
        self.populate_task_dropdown(project_no, self.task_combobox)

        self.set_combobox_value(self.task_combobox, values[4])
        self.set_combobox_value(self.employ_combobox, values[5])

        self.hours_entry.delete(0, tk.END)
        self.hours_entry.insert(0, values[6])

        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert(tk.END, values[7] if values[7] else "")

    def set_combobox_value(self, combobox, display_name):
        """Set combobox value based on display text"""
        if not display_name:
            combobox.set('')
            return

        combobox.set(display_name)

    def view_logs_by_date(self):
        """View logs filtered by selected date"""
        selected_date = self.filter_date_entry.get_date()
        date_str = selected_date.strftime("%Y-%m-%d")

        self.view_date_tree.delete(*self.view_date_tree.get_children())

        try:
            self.cursor.execute("""
                SELECT log_id, log_date, client_id, project_no, task_id, employ_id, hours, notes
                FROM time_log WHERE log_date=%s ORDER BY log_date DESC
            """, (date_str,))
            logs = self.cursor.fetchall()

            # Calculate total hours
            self.cursor.execute("""
                SELECT COALESCE(SUM(hours), 0) FROM time_log WHERE log_date=%s
            """, (date_str,))
            total_hours = self.cursor.fetchone()[0]
            self.total_hours_label.config(text=f"Total Hours: {total_hours:.2f}")

            if not logs:
                self.show_status_message(f"No logs found for {date_str}")
                return

            for log in logs:
                client_name = self.fetch_name("client", log[2], "client_id", "client_name")
                project_name = self.fetch_name("project", log[3], "project_no", "project_name")
                task_name = self.fetch_name("task", log[4], "task_id", "task_name")
                employ_name = self.fetch_name("employ", log[5], "employ_id", "employ_name")

                self.view_date_tree.insert("", tk.END, values=(
                    log[0],
                    log[1].strftime("%Y-%m-%d"),
                    client_name,
                    project_name,
                    task_name,
                    employ_name,
                    f"{log[6]:.2f}",
                    log[7] if log[7] else ""
                ))

            self.show_status_message(f"Displaying logs for {date_str}")

        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading logs: {err}", error=True)

    def generate_project_report(self):
        """Generate project task report"""
        project_name_with_no = self.report_project_combobox.get()
        if not project_name_with_no:
            self.show_status_message("Please select a project first", error=True)
            return

        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.report_tree.delete(*self.report_tree.get_children())

        try:
            # Get all tasks for the project
            self.cursor.execute("""
                SELECT task_id, task_name FROM task 
                WHERE project_no=%s ORDER BY task_name
            """, (project_no,))
            tasks = self.cursor.fetchall()

            if not tasks:
                self.show_status_message("No tasks found for selected project", error=True)
                return

            # Get task data in bulk
            task_ids = [task[0] for task in tasks]
            placeholders = ','.join(['%s'] * len(task_ids))

            self.cursor.execute(f"""
                SELECT task_id, MIN(log_date), MAX(log_date), SUM(hours)
                FROM time_log WHERE task_id IN ({placeholders}) GROUP BY task_id
            """, task_ids)
            task_stats = {row[0]: (row[1], row[2], row[3]) for row in self.cursor.fetchall()}

            # Get employees for each task
            self.cursor.execute(f"""
                SELECT tl.task_id, GROUP_CONCAT(DISTINCT e.employ_name SEPARATOR ', ')
                FROM time_log tl
                JOIN employ e ON tl.employ_id = e.employ_id
                WHERE tl.task_id IN ({placeholders}) GROUP BY tl.task_id
            """, task_ids)
            task_employees = {row[0]: row[1] for row in self.cursor.fetchall()}

            total_project_hours = 0.0

            # Populate report tree
            for task in tasks:
                task_id, task_name = task
                stats = task_stats.get(task_id, (None, None, 0.0))
                employees = task_employees.get(task_id, "")

                self.report_tree.insert("", tk.END, values=(
                    task_id,
                    task_name,
                    stats[0].strftime("%Y-%m-%d") if stats[0] else "",
                    stats[1].strftime("%Y-%m-%d") if stats[1] else "",
                    f"{float(stats[2]):.2f}",
                    employees
                ))
                total_project_hours += float(stats[2])

            # Add summary row
            self.report_tree.insert("", tk.END, values=(
                "",
                "PROJECT TOTAL",
                "",
                "",
                f"{total_project_hours:.2f}",
                ""
            ), tags=('total',))

            self.show_status_message(f"Report generated for project {project_name_with_no}")

        except mysql.connector.Error as err:
            self.show_status_message(f"Error generating report: {err}", error=True)

    def view_task_data(self):
        """View task logs for selected date range"""
        task_name_with_id = self.task_data_task_cb.get()
        if not task_name_with_id:
            self.show_status_message("Please select a task first", error=True)
            return

        task_id = self._extract_id_from_combobox(task_name_with_id)

        # Get date range
        start_date = self.task_start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.task_end_date_entry.get_date().strftime("%Y-%m-%d")

        self.task_data_tree.delete(*self.task_data_tree.get_children())

        try:
            self.cursor.execute("""
                SELECT log_id, log_date, client_id, project_no, employ_id, hours, notes
                FROM time_log 
                WHERE task_id=%s AND log_date BETWEEN %s AND %s
                ORDER BY log_date
            """, (task_id, start_date, end_date))
            logs = self.cursor.fetchall()

            # Calculate total hours
            self.cursor.execute("""
                SELECT COALESCE(SUM(hours), 0) 
                FROM time_log 
                WHERE task_id=%s AND log_date BETWEEN %s AND %s
            """, (task_id, start_date, end_date))
            total_hours = self.cursor.fetchone()[0]

            if not logs:
                self.show_status_message(f"No logs found for task {task_name_with_id}")
                return

            # Get client and project info from first log (all logs should have same project/client)
            sample_log = logs[0]
            client_name = self.fetch_name("client", sample_log[2], "client_id", "client_name")
            project_name = self.fetch_name("project", sample_log[3], "project_no", "project_name")

            for log in logs:
                employ_name = self.fetch_name("employ", log[4], "employ_id", "employ_name")

                self.task_data_tree.insert("", tk.END, values=(
                    log[0],
                    log[1].strftime("%Y-%m-%d"),
                    client_name,
                    project_name,
                    task_name_with_id,
                    employ_name,
                    f"{log[5]:.2f}",
                    log[6] if log[6] else ""
                ))

            # Add totals row
            self.task_data_tree.insert("", tk.END, values=(
                "",
                "",
                "",
                "",
                "TOTAL:",
                "",
                f"{float(total_hours):.2f}",
                ""
            ), tags=('total',))

            self.show_status_message(f"Displaying {len(logs)} logs for task {task_name_with_id}")

        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading task data: {err}", error=True)

    def add_time_log(self):
        """Add a new time log entry"""
        log_date = self.date_entry.get_date().strftime("%Y-%m-%d")

        # Get selected values from comboboxes
        client_name_with_id = self.client_combobox.get()
        project_name_with_no = self.project_combobox.get()
        task_name_with_id = self.task_combobox.get()
        employ_name_with_id = self.employ_combobox.get()

        hours = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        # Validate required fields
        if not all([log_date, client_name_with_id, project_name_with_no,
                    task_name_with_id, employ_name_with_id, hours]):
            self.show_status_message("All fields except notes are required", error=True)
            return

        # Validate hours
        try:
            hours_val = float(hours)
            if hours_val <= 0:
                raise ValueError("Hours must be positive")
        except ValueError:
            self.show_status_message("Hours must be a positive number", error=True)
            return

        # Extract IDs from combobox selections
        client_id = self._extract_id_from_combobox(client_name_with_id)
        project_no = self._extract_id_from_combobox(project_name_with_no)
        task_id = self._extract_id_from_combobox(task_name_with_id)
        employ_id = self._extract_id_from_combobox(employ_name_with_id)

        # Generate log ID
        log_id = self._generate_log_id(log_date, task_id)

        try:
            self.cursor.execute("""
                INSERT INTO time_log 
                (log_id, log_date, client_id, project_no, task_id, employ_id, hours, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log_id, log_date, client_id, project_no, task_id, employ_id,
                hours_val, notes if notes else None
            ))
            self.conn.commit()

            self.show_status_message("Time log entry added successfully")
            self.populate_time_log_list()
            self.clear_inputs()

        except mysql.connector.Error as err:
            if err.errno == 1062:
                self.show_status_message("Duplicate log ID - change date or task", error=True)
            else:
                self.show_status_message(f"Error adding time log: {err}", error=True)

    def update_time_log(self):
        """Update an existing time log entry"""
        selected = self.time_log_tree.selection()
        if not selected:
            self.show_status_message("Please select a log to update", error=True)
            return

        old_log_id = self.time_log_tree.item(selected[0])['values'][0]

        # Get current values
        log_date = self.date_entry.get_date().strftime("%Y-%m-%d")
        client_name_with_id = self.client_combobox.get()
        project_name_with_no = self.project_combobox.get()
        task_name_with_id = self.task_combobox.get()
        employ_name_with_id = self.employ_combobox.get()
        hours = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        # Validation
        if not all([log_date, client_name_with_id, project_name_with_no,
                    task_name_with_id, employ_name_with_id, hours]):
            self.show_status_message("All fields except notes are required", error=True)
            return

        try:
            hours_val = float(hours)
            if hours_val <= 0:
                raise ValueError("Hours must be positive")
        except ValueError:
            self.show_status_message("Hours must be a positive number", error=True)
            return

        # Extract IDs from combobox selections
        client_id = self._extract_id_from_combobox(client_name_with_id)
        project_no = self._extract_id_from_combobox(project_name_with_no)
        task_id = self._extract_id_from_combobox(task_name_with_id)
        employ_id = self._extract_id_from_combobox(employ_name_with_id)

        # Generate new log ID based on current selections
        new_log_id = self._generate_log_id(log_date, task_id)

        try:
            # Check if new log ID conflicts with existing entries (except current one)
            if new_log_id != old_log_id:
                self.cursor.execute("""
                    SELECT log_id FROM time_log WHERE log_id=%s AND log_id != %s
                """, (new_log_id, old_log_id))
                if self.cursor.fetchone():
                    self.show_status_message("New log ID already exists in another entry", error=True)
                    return

            # Update the entry
            self.cursor.execute("""
                UPDATE time_log 
                SET log_id=%s, log_date=%s, client_id=%s, project_no=%s, 
                    task_id=%s, employ_id=%s, hours=%s, notes=%s
                WHERE log_id=%s
            """, (
                new_log_id, log_date, client_id, project_no,
                task_id, employ_id, hours_val, notes if notes else None,
                old_log_id
            ))
            self.conn.commit()

            self.show_status_message("Time log updated successfully")
            self.populate_time_log_list()
            self.clear_inputs()

        except mysql.connector.Error as err:
            self.show_status_message(f"Error updating time log: {err}", error=True)

    def delete_time_log(self):
        """Delete a time log entry"""
        selected = self.time_log_tree.selection()
        if not selected:
            self.show_status_message("Please select a log to delete", error=True)
            return

        log_id = self.time_log_tree.item(selected[0])['values'][0]

        if not messagebox.askyesno("Confirm Delete", f"Delete time log {log_id}?"):
            return

        try:
            self.cursor.execute("DELETE FROM time_log WHERE log_id=%s", (log_id,))
            self.conn.commit()

            self.show_status_message("Time log deleted successfully")
            self.populate_time_log_list()
            self.clear_inputs()

        except mysql.connector.Error as err:
            self.show_status_message(f"Error deleting time log: {err}", error=True)

    def fetch_name(self, table, id_value, id_col, name_col):
        """Fetch a name value from specified table"""
        if not id_value:
            return ""

        try:
            self.cursor.execute(f"""
                SELECT {name_col} FROM {table} WHERE {id_col}=%s
            """, (id_value,))
            result = self.cursor.fetchone()
            return result[0] if result else str(id_value)
        except mysql.connector.Error:
            return str(id_value)

    def _extract_id_from_combobox(self, combobox_value):
        """Extract ID from formatted combobox display value"""
        if not combobox_value:
            return None

        try:
            # Format is "Display Name (ID)"
            start = combobox_value.rfind('(') + 1
            end = combobox_value.rfind(')')
            return combobox_value[start:end].strip()
        except IndexError:
            return combobox_value

    def _generate_log_id(self, log_date, task_id):
        """Generate a unique log ID based on date and task ID"""
        if not task_id:
            raise ValueError("Task ID required for log ID generation")
        date_part = log_date.replace("-", "")
        return f"{date_part}{task_id}"

    def load_db_config(self, config_file):
        """Load database configuration from INI file"""
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
        """Display a status message"""
        self.status_var.set(message)
        foreground = 'red' if error else 'green'
        self.status_bar.configure(foreground=foreground)

    def clear_inputs(self):
        """Clear all input fields"""
        self.date_entry.set_date(datetime.now())
        self.client_combobox.set('')
        self.project_combobox.set('')
        self.project_combobox['values'] = []
        self.task_combobox.set('')
        self.task_combobox['values'] = []
        self.employ_combobox.set('')
        self.hours_entry.delete(0, tk.END)
        self.notes_text.delete('1.0', tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeLogManager(root)
    root.mainloop()
