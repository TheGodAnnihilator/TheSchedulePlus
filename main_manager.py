# main_manager.py

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os
import string

class ClientManager:
    def __init__(self, master, status_callback=None):
        self.master = master
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=(5,2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Database connection
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

        # Ensure tables exist and schema updated
        self.create_client_table()
        self.create_project_table()
        self.create_task_table_with_schema_update()
        self.create_project_manager_table()

        # Constants
        self.states = [
            "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida",
            "Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
            "Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska",
            "Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio",
            "Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas",
            "Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"
        ]
        self.cities_by_state = {
            "Alabama":["Birmingham","Montgomery","Mobile","Huntsville","Tuscaloosa","Hoover","Dothan","Decatur","Auburn","Madison"],
            # ... remaining states ...
            "Wyoming":["Cheyenne","Casper","Laramie","Gillette","Rock Springs","Buffalo"]
        }
        self.project_types = ["Estimatic","Scheduling"]
        self.project_statuses = ["Completed","In Progress","Not Started"]
        self.task_statuses = ["Completed","In Progress","Not Done"]
        self.billable_options = ["Yes","No"]

        # GUI setup
        self.create_styles()
        self.notebook = ttk.Notebook(master)
        self.client_tab = ttk.Frame(self.notebook)
        self.project_manager_tab = ttk.Frame(self.notebook)
        self.project_tab = ttk.Frame(self.notebook)
        self.task_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.client_tab, text='Clients')
        self.notebook.add(self.project_manager_tab, text='Project Managers')
        self.notebook.add(self.project_tab, text='Projects')
        self.notebook.add(self.task_tab, text='Tasks')
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Build tabs
        self.create_client_widgets(self.client_tab)
        self.create_project_manager_widgets(self.project_manager_tab)
        self.create_project_widgets(self.project_tab)
        self.create_task_widgets(self.task_tab)

        # Initial population
        self.populate_client_list()
        self.populate_client_dropdown()
        self.populate_project_manager_list()
        self.populate_project_list()
        self.populate_task_list()

    def show_status_message(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

    def load_db_config(self, config_file):
        cfg = configparser.ConfigParser()
        if not os.path.exists(config_file): return None
        cfg.read(config_file)
        if 'mysql' not in cfg: return None
        sec = cfg['mysql']
        for k in ('host','user','password','database'):
            if k not in sec: return None
        return {k: sec[k] for k in ('host','user','password','database')}

    def create_styles(self):
        self.master.option_add('*Font',('Segoe UI',10))
        style = ttk.Style()
        style.theme_use('clam')
        bg, accent = "#ffffff","#0066cc"
        style.configure('TNotebook',background=bg)
        style.configure('TNotebook.Tab',background=bg,foreground='#000000',padding=[10,5])
        style.map('TNotebook.Tab',background=[('selected',accent)],foreground=[('selected','white')])
        style.configure('TFrame',background=bg)
        style.configure('TLabelframe',background=bg,foreground='#000000')
        style.configure('TLabelframe.Label',background=bg,foreground=accent,font=('Segoe UI',11,'bold'))
        style.configure('TLabel',background=bg,foreground='#000000')
        style.configure('TEntry',fieldbackground='#ffffff',foreground='#000000',padding=5,relief='solid',borderwidth=1)
        style.configure('TCombobox',fieldbackground='#ffffff',foreground='#000000',padding=5,relief='solid',borderwidth=1)
        style.configure('Accent.TButton',background=accent,foreground='white',font=('Segoe UI',10,'bold'),padding=8)
        style.map('Accent.TButton',background=[('active','#004d99')],foreground=[('active','white')])
        style.configure('Treeview',rowheight=28,background=bg,foreground='#000000',fieldbackground=bg,font=('Segoe UI',10))
        style.configure('Treeview.Heading',background=accent,foreground='white',font=('Segoe UI',11,'bold'))
        style.map('Treeview',background=[('selected',accent)],foreground=[('selected','white')])
        style.configure('total.Treeview',background='#e6f3ff',font=('Segoe UI',10,'bold'))

    # Table creation
    def create_client_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS client (
                    client_id VARCHAR(255) PRIMARY KEY,
                    client_name VARCHAR(255) NOT NULL,
                    client_address VARCHAR(255),
                    state VARCHAR(50),
                    city VARCHAR(100),
                    zip_code VARCHAR(10),
                    notes TEXT DEFAULT NULL
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error creating client table: {e}", error=True)

    def create_project_manager_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_manager (
                    pm_id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(255) NOT NULL,
                    manager_name VARCHAR(255) NOT NULL,
                    notes TEXT DEFAULT NULL,
                    FOREIGN KEY(client_id) REFERENCES client(client_id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error creating project_manager table: {e}", error=True)

    def create_project_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS project (
                    project_no VARCHAR(255) PRIMARY KEY,
                    client_id VARCHAR(255) NOT NULL,
                    project_name VARCHAR(255) NOT NULL,
                    client_project_manager VARCHAR(255),
                    project_type VARCHAR(20),
                    project_status VARCHAR(20),
                    notes TEXT DEFAULT NULL,
                    FOREIGN KEY(client_id) REFERENCES client(client_id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error creating project table: {e}", error=True)

    def create_task_table_with_schema_update(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS task (
                    task_id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(255) NOT NULL,
                    project_no VARCHAR(255) NOT NULL,
                    task_name VARCHAR(255) NOT NULL,
                    billable ENUM('Yes','No') NOT NULL,
                    hourly_rate DECIMAL(10,2) DEFAULT NULL,
                    lumpsum DECIMAL(10,2) DEFAULT NULL,
                    task_status VARCHAR(20),
                    notes TEXT DEFAULT NULL,
                    FOREIGN KEY(client_id) REFERENCES client(client_id) ON DELETE CASCADE,
                    FOREIGN KEY(project_no) REFERENCES project(project_no) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
            # Ensure columns exist
            self.cursor.execute("SHOW COLUMNS FROM task")
            cols = [c[0].lower() for c in self.cursor.fetchall()]
            alters=[]
            if 'hourly_rate' not in cols: alters.append("ADD COLUMN hourly_rate DECIMAL(10,2) DEFAULT NULL")
            if 'lumpsum' not in cols: alters.append("ADD COLUMN lumpsum DECIMAL(10,2) DEFAULT NULL")
            if 'notes' not in cols: alters.append("ADD COLUMN notes TEXT DEFAULT NULL")
            if alters:
                self.cursor.execute(f"ALTER TABLE task {', '.join(alters)}")
                self.conn.commit()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error creating/updating task table: {e}", error=True)

    # Client tab
    def create_client_widgets(self, parent):
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Client Details", padding=15)
        frm.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        frm.columnconfigure(1, weight=1)
        # Fields
        labels = ["Client ID (unique):","Client Name:","Address:","State:","City:","Zip Code:","Notes:"]
        widgets = []
        self.client_id_entry = ttk.Entry(frm, width=30); widgets.append(self.client_id_entry)
        self.name_entry = ttk.Entry(frm, width=30); widgets.append(self.name_entry)
        self.address_entry = ttk.Entry(frm, width=30); widgets.append(self.address_entry)
        self.state_combo = ttk.Combobox(frm, values=self.states, state="readonly"); widgets.append(self.state_combo)
        self.state_combo.bind("<<ComboboxSelected>>", lambda e: self.update_cities())
        self.city_combo = ttk.Combobox(frm, values=[], state="readonly"); widgets.append(self.city_combo)
        self.zip_entry = ttk.Entry(frm, width=10); widgets.append(self.zip_entry)
        self.notes_text = tk.Text(frm, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        # Layout labels and widgets
        for i, lbl in enumerate(labels):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, padx=8, pady=8, sticky='nw' if lbl=="Notes:" else "w")
            if lbl=="Notes:":
                self.notes_text.grid(row=i, column=1, columnspan=3, padx=8, pady=8, sticky="ew")
            else:
                widgets[i].grid(row=i, column=1, padx=8, pady=8, sticky="ew")
        # Buttons
        btn_frm = ttk.Frame(parent, padding=15)
        btn_frm.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        btn_frm.columnconfigure((0,1,2), weight=1)
        ttk.Button(btn_frm, text="Add New Client", command=self.add_client, style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(btn_frm, text="Update Client", command=self.update_client, style='Accent.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(btn_frm, text="Delete Client", command=self.delete_client, style='Accent.TButton').grid(row=0, column=2, padx=5)
        # Treeview
        tv_frm = ttk.LabelFrame(parent, text="Existing Clients", padding=10)
        tv_frm.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        cols = ("ID","Name","State","City")
        self.client_list = ttk.Treeview(tv_frm, columns=cols, show="headings")
        for c,width in zip(cols,(80,200,120,150)):
            self.client_list.heading(c,text=c if c!="ID" else "Client ID")
            self.client_list.column(c,width=width,anchor='center' if c=="ID" else 'w')
        self.client_list.pack(expand=True, fill='both')
        self.client_list.bind("<<TreeviewSelect>>", lambda e: self.load_client_details())
        # Tag colors
        self.client_list.tag_configure('evenrow',background=self.row_even_color)
        self.client_list.tag_configure('oddrow',background=self.row_odd_color)

    def update_cities(self):
        state = self.state_combo.get()
        self.city_combo['values'] = self.cities_by_state.get(state, [])
        self.city_combo.set('')

    def add_client(self):
        cid = self.client_id_entry.get().strip()
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        state = self.state_combo.get().strip()
        city = self.city_combo.get().strip()
        zipcode = self.zip_entry.get().strip()
        notes = self.notes_text.get('1.0',tk.END).strip()
        if not cid:
            return self.show_status_message("Client ID cannot be empty.", True)
        if not name:
            return self.show_status_message("Client Name cannot be empty.", True)
        if zipcode and not zipcode.isdigit():
            return self.show_status_message("Zip Code must be numeric.", True)
        try:
            self.cursor.execute("SELECT client_id FROM client WHERE client_id=%s",(cid,))
            if self.cursor.fetchone():
                return self.show_status_message(f"Client ID '{cid}' already exists.", True)
            self.cursor.execute(
                "INSERT INTO client(client_id,client_name,client_address,state,city,zip_code,notes) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (cid,name,address,state,city,zipcode or None,notes or None)
            )
            self.conn.commit()
            self.show_status_message(f"Client '{name}' added.")
            self.clear_client_input_fields()
            # Auto-refresh lists and dropdowns
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_list()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding client: {e}", True)

    def update_client(self):
        cid = self.client_id_entry.get().strip()
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        state = self.state_combo.get().strip()
        city = self.city_combo.get().strip()
        zipcode = self.zip_entry.get().strip()
        notes = self.notes_text.get('1.0',tk.END).strip()
        if not cid:
            return self.show_status_message("Client ID cannot be empty.", True)
        if not name:
            return self.show_status_message("Client Name cannot be empty.", True)
        if zipcode and not zipcode.isdigit():
            return self.show_status_message("Zip Code must be numeric.", True)
        try:
            self.cursor.execute("SELECT client_id FROM client WHERE client_id=%s",(cid,))
            if not self.cursor.fetchone():
                return self.show_status_message(f"Client ID '{cid}' does not exist.", True)
            self.cursor.execute(
                "UPDATE client SET client_name=%s,client_address=%s,state=%s,city=%s,zip_code=%s,notes=%s WHERE client_id=%s",
                (name,address,state,city,zipcode or None,notes or None,cid)
            )
            self.conn.commit()
            self.show_status_message(f"Client '{name}' updated.")
            self.clear_client_input_fields()
            # Auto-refresh
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_list()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating client: {e}", True)

    def delete_client(self):
        cid = self.client_id_entry.get().strip()
        if not cid:
            return self.show_status_message("Client ID cannot be empty.", True)
        if not messagebox.askyesno("Confirm","Delete client and related data?"):
            return
        try:
            self.cursor.execute("DELETE FROM project WHERE client_id=%s",(cid,))
            self.cursor.execute("DELETE FROM project_manager WHERE client_id=%s",(cid,))
            self.cursor.execute("DELETE FROM client WHERE client_id=%s",(cid,))
            self.conn.commit()
            self.show_status_message(f"Client '{cid}' deleted.")
            self.clear_client_input_fields()
            # Auto-refresh
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_list()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting client: {e}", True)

    def load_client_details(self):
        sel = self.client_list.selection()
        if not sel: return
        vals = self.client_list.item(sel[0])['values']
        cid = vals[0]
        try:
            self.cursor.execute("SELECT client_name,client_address,state,city,zip_code,notes FROM client WHERE client_id=%s",(cid,))
            row = self.cursor.fetchone()
            if row:
                self.client_id_entry.delete(0,tk.END); self.client_id_entry.insert(0,cid)
                self.name_entry.delete(0,tk.END); self.name_entry.insert(0,row[0])
                self.address_entry.delete(0,tk.END); self.address_entry.insert(0,row[1] or "")
                self.state_combo.set(row[2] or ""); self.update_cities()
                self.city_combo.set(row[3] or "")
                self.zip_entry.delete(0,tk.END); self.zip_entry.insert(0,row[4] or "")
                self.notes_text.delete('1.0',tk.END); self.notes_text.insert('1.0',row[5] or "")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading client: {e}", True)

    def clear_client_input_fields(self):
        self.client_id_entry.delete(0,tk.END)
        self.name_entry.delete(0,tk.END)
        self.address_entry.delete(0,tk.END)
        self.state_combo.set('')
        self.city_combo.set('')
        self.zip_entry.delete(0,tk.END)
        self.notes_text.delete('1.0',tk.END)

    def populate_client_list(self):
        for i in self.client_list.get_children():
            self.client_list.delete(i)
        try:
            self.cursor.execute("SELECT client_id,client_name,state,city FROM client ORDER BY client_name")
            for idx, row in enumerate(self.cursor.fetchall()):
                tag = 'evenrow' if idx%2==0 else 'oddrow'
                self.client_list.insert('',tk.END,values=row,tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching clients: {e}", True)

    def populate_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id,client_name FROM client ORDER BY client_name")
            vals = [f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            self.client_combo['values'] = vals
            if vals and not self.client_combo.get(): self.client_combo.set(vals[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error populating client dropdown: {e}", True)

    # Project Manager tab (similar auto-refresh additions)
    def create_project_manager_widgets(self, parent):
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Project Manager Details", padding=15)
        frm.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        frm.columnconfigure(1, weight=1)
        ttk.Label(frm, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.pm_client_combo = ttk.Combobox(frm, state="readonly")
        self.pm_client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.pm_client_combo.bind("<<ComboboxSelected>>", lambda e: self.populate_project_manager_list(self._extract_id(self.pm_client_combo.get())))
        ttk.Label(frm, text="Manager Name:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.manager_name_entry = ttk.Entry(frm, width=30)
        self.manager_name_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Notes:").grid(row=2, column=0, padx=8, pady=8, sticky="nw")
        self.pm_notes_text = tk.Text(frm, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.pm_notes_text.grid(row=2, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        btn_frm = ttk.Frame(parent, padding=15)
        btn_frm.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        btn_frm.columnconfigure((0,1,2), weight=1)
        ttk.Button(btn_frm, text="Add Manager", command=self.add_project_manager, style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(btn_frm, text="Update Manager", command=self.update_project_manager, style='Accent.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(btn_frm, text="Delete Manager", command=self.delete_project_manager, style='Accent.TButton').grid(row=0, column=2, padx=5)

        tv_frm = ttk.LabelFrame(parent, text="Existing Project Managers", padding=10)
        tv_frm.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1); parent.grid_rowconfigure(2, weight=1)
        cols = ("PM ID","Client ID","Manager Name")
        self.project_manager_list = ttk.Treeview(tv_frm, columns=cols, show="headings")
        for c,width in zip(cols,(70,80,200)):
            self.project_manager_list.heading(c,text=c)
            self.project_manager_list.column(c,width=width,anchor='center' if "ID" in c else 'w')
        self.project_manager_list.pack(expand=True, fill='both')
        self.project_manager_list.bind("<<TreeviewSelect>>", lambda e: self.load_project_manager_details())
        self.project_manager_list.tag_configure('evenrow',background=self.row_even_color)
        self.project_manager_list.tag_configure('oddrow', background=self.row_odd_color)

        # Populate client dropdown for PM
        self.populate_pm_client_dropdown()

    def populate_pm_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id,client_name FROM client ORDER BY client_name")
            vals=[f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            self.pm_client_combo['values']=vals
            if vals and not self.pm_client_combo.get(): self.pm_client_combo.set(vals[0])
            self.populate_project_manager_list(self._extract_id(self.pm_client_combo.get()))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error populating PM client dropdown: {e}", True)

    def add_project_manager(self):
        cid = self._extract_id(self.pm_client_combo.get())
        name = self.manager_name_entry.get().strip()
        notes = self.pm_notes_text.get('1.0',tk.END).strip()
        if not cid or not name:
            return self.show_status_message("Client and Manager name required", True)
        try:
            self.cursor.execute("INSERT INTO project_manager(client_id,manager_name,notes) VALUES(%s,%s,%s)",
                                (cid,name,notes or None))
            self.conn.commit()
            self.show_status_message("Project manager added")
            self.clear_pm_input_fields()
            # Auto-refresh
            self.populate_project_manager_list(cid)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding manager: {e}", True)

    def update_project_manager(self):
        sel=self.project_manager_list.selection()
        if not sel: return self.show_status_message("Select a manager",True)
        pm_id = self.project_manager_list.item(sel[0])['values'][0]
        cid = self._extract_id(self.pm_client_combo.get())
        name = self.manager_name_entry.get().strip()
        notes = self.pm_notes_text.get('1.0',tk.END).strip()
        if not cid or not name:
            return self.show_status_message("Client and Manager name required", True)
        try:
            self.cursor.execute("UPDATE project_manager SET client_id=%s,manager_name=%s,notes=%s WHERE pm_id=%s",
                                (cid,name,notes or None,pm_id))
            self.conn.commit()
            self.show_status_message("Project manager updated")
            self.clear_pm_input_fields()
            # Auto-refresh
            self.populate_project_manager_list(cid)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating manager: {e}", True)

    def delete_project_manager(self):
        sel=self.project_manager_list.selection()
        if not sel: return self.show_status_message("Select a manager",True)
        pm_id = self.project_manager_list.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm","Delete selected manager?"): return
        try:
            self.cursor.execute("DELETE FROM project_manager WHERE pm_id=%s",(pm_id,))
            self.conn.commit()
            self.show_status_message("Project manager deleted")
            self.clear_pm_input_fields()
            # Auto-refresh: refresh all
            self.populate_pm_client_dropdown()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting manager: {e}", True)

    def load_project_manager_details(self):
        sel = self.project_manager_list.selection()
        if not sel: return
        vals = self.project_manager_list.item(sel[0])['values']
        pm_id, cid, name = vals
        # Fetch notes
        try:
            self.cursor.execute("SELECT notes FROM project_manager WHERE pm_id=%s",(pm_id,))
            notes = self.cursor.fetchone()[0] or ""
            self.pm_client_combo.set(f"{self._fetch_client_name(cid)} ({cid})")
            self.manager_name_entry.delete(0,tk.END); self.manager_name_entry.insert(0,name)
            self.pm_notes_text.delete('1.0',tk.END); self.pm_notes_text.insert('1.0',notes)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading manager details: {e}",True)

    def clear_pm_input_fields(self):
        self.pm_client_combo.set('')
        self.manager_name_entry.delete(0,tk.END)
        self.pm_notes_text.delete('1.0',tk.END)

    def populate_project_manager_list(self, client_id=None):
        for i in self.project_manager_list.get_children():
            self.project_manager_list.delete(i)
        try:
            if client_id:
                self.cursor.execute("SELECT pm_id,client_id,manager_name FROM project_manager WHERE client_id=%s ORDER BY manager_name",(client_id,))
            else:
                self.cursor.execute("SELECT pm_id,client_id,manager_name FROM project_manager ORDER BY client_id")
            for idx,row in enumerate(self.cursor.fetchall()):
                tag='evenrow' if idx%2==0 else 'oddrow'
                self.project_manager_list.insert('',tk.END,values=row,tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching managers: {e}",True)

    def _fetch_client_name(self, client_id):
        try:
            self.cursor.execute("SELECT client_name FROM client WHERE client_id=%s",(client_id,))
            r=self.cursor.fetchone()
            return r[0] if r else client_id
        except:
            return client_id

    # Project tab
    def create_project_widgets(self, parent):
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Project Details", padding=15)
        frm.pack(fill='x', padx=15, pady=15)
        frm.columnconfigure(1, weight=1)
        # Fields
        ttk.Label(frm, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.client_combo = ttk.Combobox(frm, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.client_combo.bind("<<ComboboxSelected>>", lambda e: self.on_project_client_selected())
        ttk.Label(frm, text="Project No (unique):").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.project_no_entry = ttk.Entry(frm, width=30)
        self.project_no_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Project Name:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.project_name_entry = ttk.Entry(frm, width=30)
        self.project_name_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Project Manager:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.project_manager_combo = ttk.Combobox(frm, state="readonly")
        self.project_manager_combo.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Project Type:").grid(row=4, column=0, padx=8, pady=8, sticky="w")
        self.project_type_combo = ttk.Combobox(frm, values=self.project_types, state="readonly")
        self.project_type_combo.grid(row=4, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Project Status:").grid(row=5, column=0, padx=8, pady=8, sticky="w")
        self.project_status_combo = ttk.Combobox(frm, values=self.project_statuses, state="readonly")
        self.project_status_combo.grid(row=5, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Notes:").grid(row=6, column=0, padx=8, pady=8, sticky="nw")
        self.project_notes_text = tk.Text(frm, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.project_notes_text.grid(row=6, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        # Buttons
        btn_frm = ttk.Frame(parent, padding=15)
        btn_frm.pack(fill='x', padx=15, pady=15)
        ttk.Button(btn_frm, text="Add New Project", command=self.add_project, style='Accent.TButton').pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(btn_frm, text="Update Project", command=self.update_project, style='Accent.TButton').pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(btn_frm, text="Delete Project", command=self.delete_project, style='Accent.TButton').pack(side='left', expand=True, fill='x', padx=5)

        # Treeview
        tv_frm = ttk.LabelFrame(parent, text="Existing Projects", padding=10)
        tv_frm.pack(expand=True, fill='both', padx=15, pady=15)
        cols = ("Project No","Client ID","Project Name","Manager","Type","Status","Notes")
        self.project_list = ttk.Treeview(tv_frm, columns=cols, show="headings")
        widths = {"Project No":100,"Client ID":80,"Project Name":200,"Manager":140,"Type":100,"Status":100,"Notes":180}
        for c in cols:
            self.project_list.heading(c, text=c)
            self.project_list.column(c, width=widths[c], anchor='center' if "ID" in c or c=="Project No" else 'w')
        self.project_list.pack(expand=True, fill='both')
        self.project_list.bind("<<TreeviewSelect>>", lambda e: self.load_project_details())
        self.project_list.tag_configure('evenrow',background=self.row_even_color)
        self.project_list.tag_configure('oddrow',background=self.row_odd_color)

        # Populate dropdowns
        self.populate_client_dropdown()
        self.populate_pm_client_dropdown()
        self.populate_project_manager_dropdown()
        self.populate_project_list()

    def on_project_client_selected(self):
        cid = self._extract_id(self.client_combo.get())
        # Refresh project manager dropdown and project list
        self.populate_project_manager_dropdown(cid)
        self.populate_project_list(cid)

    def populate_project_manager_dropdown(self, client_id=None):
        vals=[]
        if client_id:
            try:
                self.cursor.execute("SELECT manager_name FROM project_manager WHERE client_id=%s ORDER BY manager_name",(client_id,))
                vals=[r[0] for r in self.cursor.fetchall()]
            except mysql.connector.Error as e:
                self.show_status_message(f"Error loading PMs: {e}",True)
        self.project_manager_combo['values']=vals
        if vals: self.project_manager_combo.set(vals[0]); return
        self.project_manager_combo.set('')

    def add_project(self):
        cid = self._extract_id(self.client_combo.get())
        pno = self.project_no_entry.get().strip()
        pname = self.project_name_entry.get().strip()
        pmgr = self.project_manager_combo.get().strip()
        ptype = self.project_type_combo.get().strip()
        pstat = self.project_status_combo.get().strip()
        notes = self.project_notes_text.get('1.0',tk.END).strip()
        if not cid or not pno or not pname:
            return self.show_status_message("Client, Project No, and Name required",True)
        try:
            self.cursor.execute("SELECT project_no FROM project WHERE project_no=%s",(pno,))
            if self.cursor.fetchone():
                return self.show_status_message("Project No already exists",True)
            self.cursor.execute(
                "INSERT INTO project(project_no,client_id,project_name,client_project_manager,project_type,project_status,notes) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (pno,cid,pname,pmgr or None,ptype or None,pstat or None,notes or None)
            )
            self.conn.commit()
            self.show_status_message("Project added")
            # Auto-refresh lists and dropdowns
            self.populate_project_list(cid)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding project: {e}",True)

    def update_project(self):
        sel=self.project_list.selection()
        if not sel: return self.show_status_message("Select a project",True)
        old_pno=self.project_list.item(sel[0])['values'][0]
        cid = self._extract_id(self.client_combo.get())
        pno = self.project_no_entry.get().strip()
        pname = self.project_name_entry.get().strip()
        pmgr = self.project_manager_combo.get().strip()
        ptype = self.project_type_combo.get().strip()
        pstat = self.project_status_combo.get().strip()
        notes = self.project_notes_text.get('1.0',tk.END).strip()
        if not cid or not pno or not pname:
            return self.show_status_message("Client, Project No, and Name required",True)
        try:
            self.cursor.execute("UPDATE project SET client_id=%s,project_name=%s,client_project_manager=%s,project_type=%s,project_status=%s,notes=%s WHERE project_no=%s",
                                (cid,pname,pmgr or None,ptype or None,pstat or None,notes or None,old_pno))
            self.conn.commit()
            self.show_status_message("Project updated")
            self.populate_project_list(cid)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating project: {e}",True)

    def delete_project(self):
        sel=self.project_list.selection()
        if not sel: return self.show_status_message("Select a project",True)
        pno=self.project_list.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm","Delete selected project?"): return
        try:
            self.cursor.execute("DELETE FROM project WHERE project_no=%s",(pno,))
            self.conn.commit()
            self.show_status_message("Project deleted")
            self.populate_project_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting project: {e}",True)

    def load_project_details(self):
        sel=self.project_list.selection()
        if not sel: return
        vals=self.project_list.item(sel[0])['values']
        pno, cid, pname, pmgr, ptype, pstat, notes = vals
        self.project_no_entry.delete(0,tk.END); self.project_no_entry.insert(0,pno)
        self.project_name_entry.delete(0,tk.END); self.project_name_entry.insert(0,pname)
        self.client_combo.set(f"{self._fetch_client_name(cid)} ({cid})")
        self.populate_project_manager_dropdown(cid)
        self.project_manager_combo.set(pmgr or '')
        self.project_type_combo.set(ptype or '')
        self.project_status_combo.set(pstat or '')
        self.project_notes_text.delete('1.0',tk.END); self.project_notes_text.insert('1.0',notes or '')

    def populate_project_list(self, client_id=None):
        for i in self.project_list.get_children():
            self.project_list.delete(i)
        try:
            if client_id:
                self.cursor.execute("SELECT project_no,client_id,project_name,client_project_manager,project_type,project_status,notes FROM project WHERE client_id=%s ORDER BY project_no",(client_id,))
            else:
                self.cursor.execute("SELECT project_no,client_id,project_name,client_project_manager,project_type,project_status,notes FROM project ORDER BY project_no")
            for idx,row in enumerate(self.cursor.fetchall()):
                tag='evenrow' if idx%2==0 else 'oddrow'
                self.project_list.insert('',tk.END,values=row,tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching projects: {e}",True)

    # Task tab (auto-refresh added)
    def create_task_widgets(self, parent):
        parent.configure(style='TFrame')
        frm = ttk.LabelFrame(parent, text="Task Details", padding=15)
        frm.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        frm.columnconfigure(1, weight=1)
        # Fields
        ttk.Label(frm, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.task_client_combo = ttk.Combobox(frm, state="readonly")
        self.task_client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.task_client_combo.bind("<<ComboboxSelected>>", lambda e: self.on_task_client_selected())
        ttk.Label(frm, text="Project:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.task_project_combo = ttk.Combobox(frm, state="readonly")
        self.task_project_combo.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.task_project_combo.bind("<<ComboboxSelected>>", lambda e: self.populate_task_list(self._extract_id(self.task_project_combo.get())))
        ttk.Label(frm, text="Task Name:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.task_name_entry = ttk.Entry(frm, width=30)
        self.task_name_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")
        ttk.Label(frm, text="Billable:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.billable_combo = ttk.Combobox(frm, values=self.billable_options, state="readonly")
        self.billable_combo.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        self.billable_combo.bind("<<ComboboxSelected>>", lambda e: self.on_billable_changed())
        self.billing_frame = ttk.Frame(frm)
        self.billing_frame.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.billing_frame.columnconfigure(1, weight=1); self.billing_frame.columnconfigure(3, weight=1)
        self.hourly_rate_label = ttk.Label(self.billing_frame, text="Hourly Rate:")
        self.hourly_rate_entry = ttk.Entry(self.billing_frame, width=15)
        self.lumpsum_label = ttk.Label(self.billing_frame, text="Lumpsum:")
        self.lumpsum_entry = ttk.Entry(self.billing_frame, width=15)
        self.hourly_rate_label.grid(row=0,column=0,padx=5,pady=5,sticky="w")
        self.hourly_rate_entry.grid(row=0,column=1,padx=5,pady=5,sticky="ew")
        self.lumpsum_label.grid(row=0,column=2,padx=20,pady=5,sticky="w")
        self.lumpsum_entry.grid(row=0,column=3,padx=5,pady=5,sticky="ew")
        for w in (self.hourly_rate_label,self.hourly_rate_entry,self.lumpsum_label,self.lumpsum_entry):
            w.grid_remove()
        ttk.Label(frm, text="Status:").grid(row=5,column=0,padx=8,pady=8,sticky="w")
        self.task_status_combo = ttk.Combobox(frm, values=self.task_statuses, state="readonly")
        self.task_status_combo.grid(row=5,column=1,padx=8,pady=8,sticky="ew")
        ttk.Label(frm, text="Notes:").grid(row=6,column=0,padx=8,pady=8,sticky="nw")
        self.task_notes_text = tk.Text(frm, height=4, width=35, wrap="word", relief="solid", borderwidth=1)
        self.task_notes_text.grid(row=6,column=1,columnspan=3,padx=8,pady=8,sticky="ew")

        btn_frm=ttk.Frame(parent,padding=15)
        btn_frm.grid(row=1,column=0,padx=15,pady=15,sticky="ew")
        btn_frm.columnconfigure((0,1,2),weight=1)
        ttk.Button(btn_frm,text="Add Task",command=self.add_task,style='Accent.TButton')\
            .grid(row=0,column=0,padx=5)
        ttk.Button(btn_frm,text="Update Task",command=self.update_task,style='Accent.TButton')\
            .grid(row=0,column=1,padx=5)
        ttk.Button(btn_frm,text="Delete Task",command=self.delete_task,style='Accent.TButton')\
            .grid(row=0,column=2,padx=5)

        tv_frm=ttk.LabelFrame(parent,text="Existing Tasks",padding=10)
        tv_frm.grid(row=2,column=0,padx=15,pady=15,sticky="nsew")
        parent.grid_columnconfigure(0,weight=1); parent.grid_rowconfigure(2,weight=1)
        cols=("Task ID","Client ID","Project No","Task Name","Billable","Hourly Rate","Lumpsum","Status","Notes")
        self.task_list=ttk.Treeview(tv_frm,columns=cols,show="headings")
        widths={"Task ID":70,"Client ID":70,"Project No":100,"Task Name":200,"Billable":70,"Hourly Rate":90,"Lumpsum":90,"Status":90,"Notes":200}
        for c in cols:
            self.task_list.heading(c,text=c)
            anchor='center' if c in ("Task ID","Client ID","Project No") else 'w'
            self.task_list.column(c,width=widths[c],anchor=anchor)
        self.task_list.pack(expand=True,fill="both")
        self.task_list.tag_configure('evenrow',background=self.row_even_color)
        self.task_list.tag_configure('oddrow',background=self.row_odd_color)
        self.task_list.bind("<<TreeviewSelect>>",lambda e:self.load_task_details())

        # Initial dropdowns and list
        self.populate_client_dropdown()
        self.populate_pm_client_dropdown()
        self.populate_project_manager_dropdown(self._extract_id(self.client_combo.get()))
        self.populate_task_client_dropdown()
        self.populate_task_list()

    def on_task_client_selected(self):
        cid = self._extract_id(self.task_client_combo.get())
        # Refresh projects and tasks
        self.populate_project_list(cid)
        self.populate_task_client_dropdown()  # repopulate client

    def populate_task_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id,client_name FROM client ORDER BY client_name")
            vals=[f"{r[1]} ({r[0]})" for r in self.cursor.fetchall()]
            self.task_client_combo['values']=vals
            if vals and not self.task_client_combo.get(): self.task_client_combo.set(vals[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error populating task client dropdown: {e}",True)

    def on_billable_changed(self):
        sel=self.billable_combo.get()
        for w in (self.hourly_rate_label,self.hourly_rate_entry,self.lumpsum_label,self.lumpsum_entry):
            w.grid_remove()
        if sel=="Yes":
            self.hourly_rate_label.grid();self.hourly_rate_entry.grid()
            self.lumpsum_label.grid();self.lumpsum_entry.grid()

    def add_task(self):
        cid = self._extract_id(self.task_client_combo.get())
        pno = self._extract_id(self.task_project_combo.get())
        tname = self.task_name_entry.get().strip()
        bill = self.billable_combo.get()
        hrate = self.hourly_rate_entry.get().strip()
        lump = self.lumpsum_entry.get().strip()
        tstat = self.task_status_combo.get().strip()
        notes = self.task_notes_text.get('1.0',tk.END).strip()
        if not cid or not pno or not tname or bill not in self.billable_options:
            return self.show_status_message("Client, project, task name, and billable required",True)
        # Validate rates
        try:
            hrate_f = float(hrate) if bill=="Yes" and hrate else 0
            lump_f = float(lump) if bill=="Yes" and lump else 0
        except:
            return self.show_status_message("Rates must be numeric",True)
        if bill=="Yes" and hrate_f<=0 and lump_f<=0:
            return self.show_status_message("Provide positive hourly rate or lumpsum",True)
        try:
            self.cursor.execute(
                "INSERT INTO task(client_id,project_no,task_name,billable,hourly_rate,lumpsum,task_status,notes) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (cid,pno,tname,bill,hrate_f or None,lump_f or None,tstat or None,notes or None)
            )
            self.conn.commit()
            self.show_status_message("Task added")
            # Auto-refresh
            self.populate_task_list(pno)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding task: {e}",True)

    def update_task(self):
        sel=self.task_list.selection()
        if not sel: return self.show_status_message("Select a task",True)
        tid=self.task_list.item(sel[0])['values'][0]
        cid = self._extract_id(self.task_client_combo.get())
        pno = self._extract_id(self.task_project_combo.get())
        tname = self.task_name_entry.get().strip()
        bill = self.billable_combo.get()
        hrate = self.hourly_rate_entry.get().strip()
        lump = self.lumpsum_entry.get().strip()
        tstat = self.task_status_combo.get().strip()
        notes = self.task_notes_text.get('1.0',tk.END).strip()
        if not cid or not pno or not tname or bill not in self.billable_options:
            return self.show_status_message("Client, project, task name, and billable required",True)
        try:
            hrate_f = float(hrate) if bill=="Yes" and hrate else 0
            lump_f = float(lump) if bill=="Yes" and lump else 0
        except:
            return self.show_status_message("Rates must be numeric",True)
        if bill=="Yes" and hrate_f<=0 and lump_f<=0:
            return self.show_status_message("Provide positive hourly rate or lumpsum",True)
        try:
            self.cursor.execute(
                "UPDATE task SET client_id=%s,project_no=%s,task_name=%s,billable=%s,hourly_rate=%s,lumpsum=%s,task_status=%s,notes=%s "
                "WHERE task_id=%s",
                (cid,pno,tname,bill,hrate_f or None,lump_f or None,tstat or None,notes or None,tid)
            )
            self.conn.commit()
            self.show_status_message("Task updated")
            self.populate_task_list(pno)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating task: {e}",True)

    def delete_task(self):
        sel=self.task_list.selection()
        if not sel: return self.show_status_message("Select a task",True)
        tid=self.task_list.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm","Delete selected task?"): return
        try:
            self.cursor.execute("DELETE FROM task WHERE task_id=%s",(tid,))
            self.conn.commit()
            self.show_status_message("Task deleted")
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting task: {e}",True)

    def load_task_details(self):
        sel=self.task_list.selection()
        if not sel: return
        vals=self.task_list.item(sel[0])['values']
        tid, cid, pno, tname, bill, hrate, lump, tstat, notes = vals
        self.task_client_combo.set(f"{self._fetch_client_name(cid)} ({cid})")
        self.populate_project_list(cid)
        self.task_project_combo.set(f"{self._fetch_project_name(pno)} ({pno})")
        self.task_name_entry.delete(0,tk.END); self.task_name_entry.insert(0,tname)
        self.billable_combo.set(bill); self.on_billable_changed()
        self.hourly_rate_entry.delete(0,tk.END); self.hourly_rate_entry.insert(0,hrate or "")
        self.lumpsum_entry.delete(0,tk.END); self.lumpsum_entry.insert(0,lump or "")
        self.task_status_combo.set(tstat or "")
        self.task_notes_text.delete('1.0',tk.END); self.task_notes_text.insert('1.0',notes or "")

    def populate_task_list(self, project_no=None):
        for i in self.task_list.get_children():
            self.task_list.delete(i)
        try:
            if project_no:
                self.cursor.execute("SELECT task_id,client_id,project_no,task_name,billable,hourly_rate,lumpsum,task_status,notes FROM task WHERE project_no=%s ORDER BY task_id",(project_no,))
            else:
                self.cursor.execute("SELECT task_id,client_id,project_no,task_name,billable,hourly_rate,lumpsum,task_status,notes FROM task ORDER BY task_id")
            for idx,row in enumerate(self.cursor.fetchall()):
                tag='evenrow' if idx%2==0 else 'oddrow'
                self.task_list.insert('',tk.END,values=row,tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching tasks: {e}",True)

    def _extract_id(self, text):
        if '(' in text and text.endswith(')'):
            return text.split('(')[-1][:-1]
        return None

    def _fetch_project_name(self, project_no):
        try:
            self.cursor.execute("SELECT project_name FROM project WHERE project_no=%s",(project_no,))
            r=self.cursor.fetchone()
            return r[0] if r else project_no
        except:
            return project_no

if __name__=="__main__":
    root=tk.Tk()
    root.title("Client & Project Manager")
    app=ClientManager(root)
    root.mainloop()
