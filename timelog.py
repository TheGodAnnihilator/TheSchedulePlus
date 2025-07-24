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

    def __init__(self, master):
        """
        Initializes the TimeLogManager application.
        Args:
            master (tk.Tk): The root window for the application.
        """
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

        # Initialize application components
        self.create_tables()
        self.create_styles()
        self.create_gui()
        self.populate_dropdowns()
        # Initially populate the list with logs from the current date
        self.populate_time_log_list(for_date=datetime.now().strftime('%Y-%m-%d'))

    def create_tables(self):
        """
        Ensures all necessary tables exist in the database.
        Creates tables if they don't exist.
        """
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
                        project_no VARCHAR(255) PRIMARY KEY,
                        client_id VARCHAR(255) NOT NULL,
                        project_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE)""",
            'task': """CREATE TABLE IF NOT EXISTS task (
                      task_id INT AUTO_INCREMENT PRIMARY KEY,
                      project_no VARCHAR(255) NOT NULL,
                      task_name VARCHAR(255) NOT NULL,
                      billable ENUM('Yes', 'No'),
                      hourly_rate DECIMAL(10,2) DEFAULT NULL,
                      lumpsum DECIMAL(10,2) DEFAULT NULL,
                      FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE CASCADE)""",
            'employ': """CREATE TABLE IF NOT EXISTS employ (
                       employ_id VARCHAR(50) PRIMARY KEY,
                       employ_name VARCHAR(255) NOT NULL)""",
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
                         FOREIGN KEY (employ_id) REFERENCES employ(employ_id) ON DELETE SET NULL)"""
        }

        for table, query in tables.items():
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                self.show_status_message(f"Error creating {table} table: {err}", error=True)
        self.conn.commit()

    def create_styles(self):
        """Configures the visual styles for the application's widgets."""
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
        style.configure('total', background='#e6f3ff', font=('Segoe UI', 10, 'bold'))

    def create_gui(self):
        """Creates the main GUI layout with a tabbed interface."""
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
        """Create widgets for the time log entry tab."""
        input_frame = ttk.LabelFrame(parent, text="Time Log Entry", padding=15)
        input_frame.pack(fill='x', padx=10, pady=10)
        input_frame.columnconfigure(1, weight=1)

        fields = [
            ("Date:", "date_entry", DateEntry(input_frame, width=18, date_pattern='y-mm-dd')),
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

        # Bind date selection to filter the list
        self.date_entry.bind("<<DateEntrySelected>>", self.filter_logs_by_entry_date)

        ttk.Label(input_frame, text="Notes:").grid(row=6, column=0, sticky='w', pady=5, padx=5)
        self.notes_text = tk.Text(input_frame, height=4, width=35, wrap='word',
                                  relief='solid', borderwidth=1)
        self.notes_text.grid(row=6, column=1, sticky='ew', pady=5, padx=5)

        self.client_combobox.bind("<<ComboboxSelected>>", self.on_client_selected)
        self.project_combobox.bind("<<ComboboxSelected>>", self.on_project_selected)

        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        buttons_frame.columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Button(buttons_frame, text="Add Entry", command=self.add_time_log, style='Accent.TButton').grid(row=0,
                                                                                                            column=0,
                                                                                                            padx=5,
                                                                                                            pady=5,
                                                                                                            sticky="ew")
        ttk.Button(buttons_frame, text="Update Entry", command=self.update_time_log, style='Accent.TButton').grid(row=0,
                                                                                                                  column=1,
                                                                                                                  padx=5,
                                                                                                                  pady=5,
                                                                                                                  sticky="ew")
        ttk.Button(buttons_frame, text="Delete Entry", command=self.delete_time_log, style='Accent.TButton').grid(row=0,
                                                                                                                  column=2,
                                                                                                                  padx=5,
                                                                                                                  pady=5,
                                                                                                                  sticky="ew")
        # Button to show all logs, clearing the date filter
        ttk.Button(buttons_frame, text="Show All Logs", command=self.show_all_logs, style='Accent.TButton').grid(row=0,
                                                                                                                 column=3,
                                                                                                                 padx=5,
                                                                                                                 pady=5,
                                                                                                                 sticky="ew")

        list_frame = ttk.LabelFrame(parent, text="Time Log List", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Client", "Project", "Task", "Employee", "Hours", "Notes")
        self.time_log_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        col_widths = {"Log ID": 120, "Date": 100, "Client": 150, "Project": 150, "Task": 150, "Employee": 120,
                      "Hours": 80, "Notes": 200}
        for col in columns:
            self.time_log_tree.heading(col, text=col)
            self.time_log_tree.column(col, width=col_widths[col], anchor='center')

        self.time_log_tree.pack(expand=True, fill="both")
        self.time_log_tree.bind("<<TreeviewSelect>>", self.on_time_log_select)

    def create_view_by_date_widgets(self, parent):
        """Create widgets for viewing logs by date."""
        control_frame = ttk.LabelFrame(parent, text="Select Date", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(control_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_date_entry = DateEntry(control_frame, width=18, date_pattern='y-mm-dd')
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.view_date_button = ttk.Button(control_frame, text="View", command=self.view_logs_by_date,
                                           style='Accent.TButton')
        self.view_date_button.grid(row=0, column=2, padx=10, pady=5, sticky='w')

        self.total_hours_label = ttk.Label(control_frame, text="Total Hours: 0.00", font=('Segoe UI', 10, 'bold'))
        self.total_hours_label.grid(row=0, column=3, padx=10, pady=5, sticky='w')

        list_frame = ttk.LabelFrame(parent, text="Time Logs for Selected Date", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Client", "Project", "Task", "Employee", "Hours", "Notes")
        self.view_date_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        col_widths = {"Log ID": 120, "Date": 100, "Client": 150, "Project": 150, "Task": 150, "Employee": 120,
                      "Hours": 80, "Notes": 200}
        for col in columns:
            self.view_date_tree.heading(col, text=col)
            self.view_date_tree.column(col, width=col_widths[col], anchor='center')

        self.view_date_tree.pack(expand=True, fill="both")

    def create_project_report_widgets(self, parent):
        """Create widgets for project reports tab."""
        control_frame = ttk.LabelFrame(parent, text="Select Project", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(control_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_client_combobox = ttk.Combobox(control_frame, state='readonly', width=40)
        self.report_client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.report_client_combobox.bind("<<ComboboxSelected>>", self.on_report_client_selected)

        ttk.Label(control_frame, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.report_project_combobox = ttk.Combobox(control_frame, state='readonly', width=40)
        self.report_project_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.report_project_combobox.bind("<<ComboboxSelected>>", self.on_report_project_selected)

        self.generate_report_button = ttk.Button(control_frame, text="Generate Report",
                                                 command=self.generate_project_report, style='Accent.TButton')
        self.generate_report_button.grid(row=1, column=2, padx=10, pady=5, sticky='w')

        report_frame = ttk.LabelFrame(parent, text="Project Tasks Report", padding=10)
        report_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Task ID", "Task Name", "Start Date", "End Date", "Total Hours", "Employees")
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show="headings", style='Treeview')

        col_widths = {"Task ID": 100, "Task Name": 200, "Start Date": 100, "End Date": 100, "Total Hours": 100,
                      "Employees": 200}
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=col_widths[col], anchor='center')

        self.report_tree.pack(expand=True, fill="both")

    def create_task_data_widgets(self, parent):
        """Create widgets for task data tab, including hourly rate and lumpsum."""
        control_frame = ttk.LabelFrame(parent, text="Select Date Range and Task", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Client selection
        ttk.Label(control_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.task_data_client_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_client_cb.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.task_data_client_cb.bind("<<ComboboxSelected>>", self.on_task_data_client_selected)

        # Project selection
        ttk.Label(control_frame, text="Project:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.task_data_project_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_project_cb.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.task_data_project_cb.bind("<<ComboboxSelected>>", self.on_task_data_project_selected)

        # Task selection
        ttk.Label(control_frame, text="Task:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.task_data_task_cb = ttk.Combobox(control_frame, state='readonly', width=32)
        self.task_data_task_cb.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Date range selection
        ttk.Label(control_frame, text="Start Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.task_start_date_entry = DateEntry(control_frame, width=18, date_pattern='y-mm-dd')
        self.task_start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(control_frame, text="End Date:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.task_end_date_entry = DateEntry(control_frame, width=18, date_pattern='y-mm-dd')
        self.task_end_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # View button
        self.view_task_data_button = ttk.Button(control_frame, text="View Task Data", command=self.view_task_data,
                                                style='Accent.TButton')
        self.view_task_data_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        # Task data display
        list_frame = ttk.LabelFrame(parent, text="Task Logs", padding=10)
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ("Log ID", "Date", "Employee", "Hours", "Hourly Rate", "Lumpsum", "Log Amount", "Notes")
        self.task_data_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')

        col_widths = {"Log ID": 100, "Date": 100, "Employee": 120, "Hours": 80, "Hourly Rate": 90, "Lumpsum": 90,
                      "Log Amount": 90, "Notes": 200}
        for col, width in col_widths.items():
            self.task_data_tree.heading(col, text=col)
            self.task_data_tree.column(col, width=width, anchor='center')

        self.task_data_tree.pack(expand=True, fill="both")

        # Labels for totals
        totals_frame = ttk.Frame(list_frame)
        totals_frame.pack(fill='x', pady=(5, 0), anchor='w')
        self.task_total_hours_label = ttk.Label(totals_frame, text="Total Hours: 0.00", font=('Segoe UI', 10, 'bold'))
        self.task_total_hours_label.pack(side='left', padx=10)
        self.task_total_amount_label = ttk.Label(totals_frame, text="Total Amount: $0.00",
                                                 font=('Segoe UI', 10, 'bold'))
        self.task_total_amount_label.pack(side='left', padx=10)

    def populate_dropdowns(self):
        """Populate all combobox dropdowns with data from the database."""
        try:
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            clients = self.cursor.fetchall()
            client_names = [f"{cli[1]} ({cli[0]})" for cli in clients]

            self.client_combobox['values'] = client_names
            self.report_client_combobox['values'] = client_names
            self.task_data_client_cb['values'] = client_names

            if client_names:
                self.client_combobox.set(client_names[0])
                self.on_client_selected()
                self.report_client_combobox.set(client_names[0])
                self.on_report_client_selected()
                self.task_data_client_cb.set(client_names[0])
                self.on_task_data_client_selected()

            self.cursor.execute("SELECT employ_id, employ_name FROM employ ORDER BY employ_name")
            employs = self.cursor.fetchall()
            employ_names = [f"{employ[1]} ({employ[0]})" for employ in employs]
            self.employ_combobox['values'] = employ_names
            if employ_names:
                self.employ_combobox.set(employ_names[0])

        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching dropdown data: {err}", error=True)

    def populate_time_log_list(self, for_date=None):
        """
        Populate the main time log list. If for_date is provided,
        it filters the logs for that specific date.
        """
        for i in self.time_log_tree.get_children():
            self.time_log_tree.delete(i)

        base_query = """
            SELECT tl.log_id, tl.log_date, c.client_name, p.project_name, t.task_name, e.employ_name, tl.hours, tl.notes,
            c.client_id, p.project_no, t.task_id, e.employ_id
            FROM time_log tl
            LEFT JOIN client c ON tl.client_id = c.client_id
            LEFT JOIN project p ON tl.project_no = p.project_no
            LEFT JOIN task t ON tl.task_id = t.task_id
            LEFT JOIN employ e ON tl.employ_id = e.employ_id
        """
        params = []

        if for_date:
            query = base_query + " WHERE tl.log_date = %s ORDER BY tl.log_id DESC"
            params.append(for_date)
            self.show_status_message(f"Showing logs for {for_date}", error=False)
        else:
            query = base_query + " ORDER BY tl.log_date DESC, tl.log_id DESC"

        try:
            self.cursor.execute(query, tuple(params))
            logs = self.cursor.fetchall()

            for log in logs:
                client_display = f"{log[2]} ({log[8]})" if log[2] and log[8] else log[8] or ""
                project_display = f"{log[3]} ({log[9]})" if log[3] and log[9] else log[9] or ""
                task_display = f"{log[4]} ({log[10]})" if log[4] and log[10] else log[10] or ""
                employ_display = f"{log[5]} ({log[11]})" if log[5] and log[11] else log[11] or ""

                self.time_log_tree.insert("", tk.END, values=(
                    log[0],
                    log[1].strftime("%Y-%m-%d") if log[1] else "",
                    client_display,
                    project_display,
                    task_display,
                    employ_display,
                    f"{log[6]:.2f}" if log[6] is not None else "0.00",
                    log[7] if log[7] else ""
                ))

        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading time logs: {err}", error=True)

    def populate_project_dropdown(self, client_id, project_combobox):
        """Populate projects dropdown based on selected client."""
        if not client_id:
            project_combobox['values'] = []
            project_combobox.set('')
            return

        try:
            self.cursor.execute("SELECT project_no, project_name FROM project WHERE client_id=%s ORDER BY project_name",
                                (client_id,))
            projects = self.cursor.fetchall()
            project_names = [f"{proj[1]} ({proj[0]})" for proj in projects]
            project_combobox['values'] = project_names
            if project_names:
                project_combobox.set(project_names[0])
            else:
                project_combobox.set('')
        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching projects: {err}", error=True)

    def populate_task_dropdown(self, project_no, task_combobox):
        """Populate tasks dropdown based on selected project."""
        if not project_no:
            task_combobox['values'] = []
            task_combobox.set('')
            return

        try:
            self.cursor.execute("SELECT task_id, task_name FROM task WHERE project_no=%s ORDER BY task_name",
                                (project_no,))
            tasks = self.cursor.fetchall()
            task_names = [f"{task[1]} ({task[0]})" for task in tasks]
            task_combobox['values'] = task_names
            if task_names:
                task_combobox.set(task_names[0])
            else:
                task_combobox.set('')
        except mysql.connector.Error as err:
            self.show_status_message(f"Error fetching tasks: {err}", error=True)

    def on_client_selected(self, event=None):
        client_name_with_id = self.client_combobox.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.project_combobox)
        self.on_project_selected()

    def on_project_selected(self, event=None):
        project_name_with_no = self.project_combobox.get()
        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.populate_task_dropdown(project_no, self.task_combobox)

    def on_report_client_selected(self, event=None):
        client_name_with_id = self.report_client_combobox.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.report_project_combobox)
        self.report_tree.delete(*self.report_tree.get_children())

    def on_report_project_selected(self, event=None):
        self.report_tree.delete(*self.report_tree.get_children())

    def on_task_data_client_selected(self, event=None):
        client_name_with_id = self.task_data_client_cb.get()
        client_id = self._extract_id_from_combobox(client_name_with_id)
        self.populate_project_dropdown(client_id, self.task_data_project_cb)
        self.on_task_data_project_selected()

    def on_task_data_project_selected(self, event=None):
        project_name_with_no = self.task_data_project_cb.get()
        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.populate_task_dropdown(project_no, self.task_data_task_cb)
        self.task_data_tree.delete(*self.task_data_tree.get_children())

    def on_time_log_select(self, event):
        """Handle selection of a time log entry."""
        selected = self.time_log_tree.selection()
        if not selected: return
        values = self.time_log_tree.item(selected[0])['values']

        try:
            self.date_entry.set_date(datetime.strptime(values[1], "%Y-%m-%d"))
        except (ValueError, TypeError):
            self.date_entry.set_date(datetime.now())

        self.client_combobox.set(values[2])
        self.on_client_selected()
        self.project_combobox.set(values[3])
        self.on_project_selected()
        self.task_combobox.set(values[4])
        self.employ_combobox.set(values[5])
        self.hours_entry.delete(0, tk.END)
        self.hours_entry.insert(0, values[6])
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert(tk.END, values[7] if values[7] else "")

    def view_logs_by_date(self):
        """View logs filtered by selected date."""
        selected_date_str = self.filter_date_entry.get()
        self.view_date_tree.delete(*self.view_date_tree.get_children())
        try:
            self.cursor.execute("""
                SELECT tl.log_id, tl.log_date, c.client_name, p.project_name, t.task_name, e.employ_name, tl.hours, tl.notes
                FROM time_log tl
                LEFT JOIN client c ON tl.client_id = c.client_id
                LEFT JOIN project p ON tl.project_no = p.project_no
                LEFT JOIN task t ON tl.task_id = t.task_id
                LEFT JOIN employ e ON tl.employ_id = e.employ_id
                WHERE tl.log_date=%s ORDER BY tl.log_id
            """, (selected_date_str,))
            logs = self.cursor.fetchall()

            total_hours = sum(float(log[6]) for log in logs if log[6] is not None)
            self.total_hours_label.config(text=f"Total Hours: {total_hours:.2f}")

            if not logs:
                self.show_status_message(f"No logs found for {selected_date_str}")
                return

            for log in logs:
                self.view_date_tree.insert("", tk.END, values=(
                    log[0], log[1].strftime("%Y-%m-%d"), log[2], log[3], log[4], log[5],
                    f"{log[6]:.2f}" if log[6] is not None else "0.00",
                    log[7] or ""
                ))
            self.show_status_message(f"Displaying logs for {selected_date_str}")
        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading logs: {err}", error=True)

    def generate_project_report(self):
        """Generate project task report."""
        project_name_with_no = self.report_project_combobox.get()
        if not project_name_with_no:
            self.show_status_message("Please select a project first", error=True)
            return

        project_no = self._extract_id_from_combobox(project_name_with_no)
        self.report_tree.delete(*self.report_tree.get_children())

        # Refactored query to reliably get all tasks and their aggregated time logs
        query = """
            SELECT
                t.task_id,
                t.task_name,
                MIN(tl.log_date) AS start_date,
                MAX(tl.log_date) AS end_date,
                SUM(tl.hours) AS total_hours,
                GROUP_CONCAT(DISTINCT e.employ_name SEPARATOR ', ') AS employees
            FROM
                task t
            LEFT JOIN
                time_log tl ON t.task_id = tl.task_id
            LEFT JOIN
                employ e ON tl.employ_id = e.employ_id
            WHERE
                t.project_no = %s
            GROUP BY
                t.task_id, t.task_name
            ORDER BY
                t.task_name;
        """

        try:
            self.cursor.execute(query, (project_no,))
            tasks_data = self.cursor.fetchall()

            if not tasks_data:
                self.show_status_message("No tasks found for the selected project")
                return

            total_project_hours = 0.0
            for row in tasks_data:
                task_id, task_name, start_date, end_date, total_hours, employees = row

                # Ensure hours is a number, default to 0 if None (for tasks with no logs)
                hours_val = total_hours if total_hours is not None else 0.0

                # Format dates, handling None if no logs exist for the task
                start_date_str = start_date.strftime("%Y-%m-%d") if start_date else "N/A"
                end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "N/A"

                self.report_tree.insert("", tk.END, values=(
                    task_id,
                    task_name,
                    start_date_str,
                    end_date_str,
                    f"{float(hours_val):.2f}",
                    employees or ""
                ))

                # FIX for TypeError: Cast Decimal to float before adding
                total_project_hours += float(hours_val)

            # Add total row
            self.report_tree.insert("", tk.END, values=("", "PROJECT TOTAL", "", "", f"{total_project_hours:.2f}", ""),
                                    tags=('total',))
            self.show_status_message(f"Report generated for project {project_name_with_no}")

        except mysql.connector.Error as err:
            self.show_status_message(f"Error generating report: {err}", error=True)

    def view_task_data(self):
        """View task logs for a selected date range, showing financial details."""
        task_name_with_id = self.task_data_task_cb.get()
        if not task_name_with_id:
            self.show_status_message("Please select a task first", error=True)
            return

        task_id = self._extract_id_from_combobox(task_name_with_id)
        start_date = self.task_start_date_entry.get()
        end_date = self.task_end_date_entry.get()
        self.task_data_tree.delete(*self.task_data_tree.get_children())

        try:
            self.cursor.execute("SELECT hourly_rate, lumpsum FROM task WHERE task_id=%s", (task_id,))
            task_details = self.cursor.fetchone()
            hourly_rate = task_details[0] if task_details and task_details[0] else 0.0
            lumpsum = task_details[1] if task_details and task_details[1] else 0.0

            self.cursor.execute("""
                SELECT tl.log_id, tl.log_date, e.employ_name, tl.hours, tl.notes
                FROM time_log tl
                LEFT JOIN employ e ON tl.employ_id = e.employ_id
                WHERE tl.task_id=%s AND tl.log_date BETWEEN %s AND %s
                ORDER BY tl.log_date
            """, (task_id, start_date, end_date))
            logs = self.cursor.fetchall()

            if not logs:
                self.show_status_message(f"No logs found for task '{task_name_with_id}' in the selected date range")
                self.task_total_hours_label.config(text="Total Hours: 0.00")
                self.task_total_amount_label.config(text="Total Amount: $0.00")
                return

            total_hours = 0.0
            total_amount = 0.0
            for log in logs:
                log_id, log_date, employ_name, hours, notes = log
                hours = float(hours) if hours else 0.0
                log_amount = hours * float(hourly_rate)
                total_hours += hours
                total_amount += log_amount

                self.task_data_tree.insert("", tk.END, values=(
                    log_id, log_date.strftime("%Y-%m-%d"), employ_name or "", f"{hours:.2f}",
                    f"${float(hourly_rate):.2f}", f"${float(lumpsum):.2f}", f"${log_amount:.2f}", notes or ""
                ))

            final_total_amount = lumpsum if lumpsum > 0 else total_amount
            self.task_total_hours_label.config(text=f"Total Hours: {total_hours:.2f}")
            self.task_total_amount_label.config(text=f"Total Amount: ${final_total_amount:.2f}")
            self.show_status_message(f"Displaying {len(logs)} logs for task '{task_name_with_id}'")

        except mysql.connector.Error as err:
            self.show_status_message(f"Error loading task data: {err}", error=True)

    def add_time_log(self):
        """Add a new time log entry to the database."""
        log_date = self.date_entry.get()
        client_id = self._extract_id_from_combobox(self.client_combobox.get())
        project_no = self._extract_id_from_combobox(self.project_combobox.get())
        task_id = self._extract_id_from_combobox(self.task_combobox.get())
        employ_id = self._extract_id_from_combobox(self.employ_combobox.get())
        hours = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not all([log_date, client_id, project_no, task_id, employ_id, hours]):
            self.show_status_message("All fields except notes are required", error=True)
            return
        try:
            hours_val = float(hours)
            if hours_val <= 0: raise ValueError("Hours must be positive")
        except ValueError:
            self.show_status_message("Hours must be a positive number", error=True)
            return

        try:
            log_id = self._generate_log_id(log_date, task_id, employ_id)
            self.cursor.execute(
                "INSERT INTO time_log (log_id, log_date, client_id, project_no, task_id, employ_id, hours, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (log_id, log_date, client_id, project_no, task_id, employ_id, hours_val, notes or None)
            )
            self.conn.commit()
            self.show_status_message("Time log entry added successfully")
            self.populate_time_log_list(for_date=log_date)
            self.clear_inputs()
        except (mysql.connector.Error, ValueError) as err:
            self.show_status_message(f"Error adding time log: {err}", error=True)

    def update_time_log(self):
        """Update an existing time log entry."""
        selected = self.time_log_tree.selection()
        if not selected:
            self.show_status_message("Please select a log to update", error=True)
            return
        old_log_id = self.time_log_tree.item(selected[0])['values'][0]

        log_date = self.date_entry.get()
        client_id = self._extract_id_from_combobox(self.client_combobox.get())
        project_no = self._extract_id_from_combobox(self.project_combobox.get())
        task_id = self._extract_id_from_combobox(self.task_combobox.get())
        employ_id = self._extract_id_from_combobox(self.employ_combobox.get())
        hours = self.hours_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not all([log_date, client_id, project_no, task_id, employ_id, hours]):
            self.show_status_message("All fields must be filled", error=True)
            return
        try:
            hours_val = float(hours)
            if hours_val <= 0: raise ValueError("Hours must be positive")
        except ValueError:
            self.show_status_message("Hours must be a positive number", error=True)
            return

        try:
            new_log_id = self._generate_log_id(log_date, task_id, employ_id)
            self.cursor.execute(
                "UPDATE time_log SET log_id=%s, log_date=%s, client_id=%s, project_no=%s, task_id=%s, employ_id=%s, hours=%s, notes=%s WHERE log_id=%s",
                (new_log_id, log_date, client_id, project_no, task_id, employ_id, hours_val, notes or None, old_log_id)
            )
            self.conn.commit()
            self.show_status_message("Time log updated successfully")
            self.populate_time_log_list(for_date=log_date)
            self.clear_inputs()
        except (mysql.connector.Error, ValueError) as err:
            self.show_status_message(f"Error updating time log: {err}", error=True)

    def delete_time_log(self):
        """Delete a selected time log entry."""
        selected = self.time_log_tree.selection()
        if not selected:
            self.show_status_message("Please select a log to delete", error=True)
            return

        item = self.time_log_tree.item(selected[0])['values']
        log_id = item[0]
        log_date = item[1]

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete time log {log_id}?"):
            return
        try:
            self.cursor.execute("DELETE FROM time_log WHERE log_id=%s", (log_id,))
            self.conn.commit()
            self.show_status_message("Time log deleted successfully")
            self.populate_time_log_list(for_date=log_date)
            self.clear_inputs()
        except mysql.connector.Error as err:
            self.show_status_message(f"Error deleting time log: {err}", error=True)

    def filter_logs_by_entry_date(self, event=None):
        """Handler to filter the time log list based on the date_entry widget."""
        selected_date = self.date_entry.get()
        self.populate_time_log_list(for_date=selected_date)

    def show_all_logs(self):
        """Removes the date filter and shows all time logs."""
        self.populate_time_log_list(for_date=None)
        self.show_status_message("Showing all time logs")

    def _extract_id_from_combobox(self, combobox_value):
        """Extract ID from a 'Name (ID)' formatted string."""
        if not combobox_value or '(' not in combobox_value: return None
        return combobox_value.split('(')[-1].strip()[:-1]

    def _generate_log_id(self, log_date, task_id, employ_id):
        """Generate a unique log ID."""
        if not all([log_date, task_id, employ_id]):
            raise ValueError("Date, Task ID and Employee ID are required for log ID")
        # To ensure uniqueness for the same task by the same employee on the same day, add a timestamp
        timestamp = datetime.now().strftime("%H%M%S%f")
        return f"{log_date.replace('-', '')}-{task_id}-{employ_id}-{timestamp}"

    def load_db_config(self, config_file):
        """Load database configuration from an INI file."""
        config = configparser.ConfigParser()
        if not os.path.exists(config_file): return None
        config.read(config_file)
        if 'mysql' not in config: return None
        # Ensure all required keys are present
        required_keys = ['host', 'user', 'password', 'database']
        if not all(key in config['mysql'] for key in required_keys):
            return None
        return {key: config['mysql'][key] for key in required_keys}

    def show_status_message(self, message, error=False):
        """Display a message in the status bar."""
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

    def clear_inputs(self):
        """Clear all input fields in the entry tab."""
        self.date_entry.set_date(datetime.now())
        if self.client_combobox['values']:
            self.client_combobox.set(self.client_combobox['values'][0])
        self.on_client_selected()
        if self.employ_combobox['values']:
            self.employ_combobox.set(self.employ_combobox['values'][0])
        self.hours_entry.delete(0, tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.time_log_tree.selection_remove(self.time_log_tree.selection())


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeLogManager(root)
    root.mainloop()