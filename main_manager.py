import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser
import os
import string

class ClientManager:
    def __init__(self, master):
        self.master = master
        master.title("Client & Project Management System")
        master.geometry("900x740")  # extra height for status bar   
        master.configure(bg="#ffffff")  # White background

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=(5,2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Database connection
        self.db_config = self.load_db_config('config.ini')
        if not self.db_config:
            self.show_status_message("Configuration Error: Database config file not found or invalid", error=True)
            master.after(5000, master.destroy)  # close after 5 seconds
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
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
            "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming"
        ]

        self.cities_by_state = {
            # ... (same large dict as provided earlier)
            "Alabama": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa", "Hoover", "Dothan", "Decatur", "Auburn", "Madison"],
            "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan", "Wasilla", "Kenai", "Kodiak"],
            "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Glendale", "Gilbert", "Tempe", "Peoria"],
            "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro", "Conway", "Rogers", "North Little Rock"],
            "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose", "Fresno",
                           "Long Beach", "Oakland", "Bakersfield", "Anaheim", "Santa Ana", "Riverside", "Stockton", "Irvine", "Chula Vista"],
            "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton", "Arvada", "Westminster", "Pueblo", "Centennial"],
            "Connecticut": ["Bridgeport", "New Haven", "Stamford", "Hartford", "Waterbury", "Norwalk", "Danbury", "New Britain"],
            "Delaware": ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna"],
            "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah", "Tallahassee", "Port St. Lucie", "Fort Lauderdale", "Pembroke Pines"],
            "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens", "Sandy Springs", "Roswell"],
            "Hawaii": ["Honolulu", "Hilo", "Kailua", "Kapolei", "Waipahu", "Kaneohe", "Mililani Town"],
            "Idaho": ["Boise", "Nampa", "Meridian", "Idaho Falls", "Caldwell", "Pocatello", "Twin Falls"],
            "Illinois": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Springfield", "Peoria", "Elgin", "Waukegan"],
            "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel", "Fishers", "Bloomington", "Hammond"],
            "Iowa": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City", "Waterloo", "Council Bluffs"],
            "Kansas": ["Wichita", "Overland Park", "Kansas City", "Topeka", "Olathe", "Lawrence", "Shawnee"],
            "Kentucky": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington", "Hopkinsville", "Nicholasville"],
            "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles", "Kenner", "Bossier City"],
            "Maine": ["Portland", "Lewiston", "Bangor", "South Portland", "Auburn", "Biddeford", "Sanford"],
            "Maryland": ["Baltimore", "Columbia", "Germantown", "Silver Spring", "Waldorf", "Ellicott City", "Frederick"],
            "Massachusetts": ["Boston", "Worcester", "Springfield", "Lowell", "Cambridge", "New Bedford", "Quincy", "Lynn"],
            "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Lansing", "Ann Arbor", "Flint", "Dearborn"],
            "Minnesota": ["Minneapolis", "Saint Paul", "Rochester", "Duluth", "Bloomington", "Brooklyn Park", "Plymouth"],
            "Mississippi": ["Jackson", "Gulfport", "Southaven", "Hattiesburg", "Biloxi", "Meridian", "Tupelo"],
            "Missouri": ["Kansas City", "St. Louis", "Springfield", "Columbia", "Independence", "Lee's Summit", "O'Fallon"],
            "Montana": ["Billings", "Missoula", "Great Falls", "Bozeman", "Butte", "Helena", "Kalispell"],
            "Nebraska": ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney", "Fremont", "Hastings"],
            "Nevada": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks", "Carson City", "Fernley"],
            "New Hampshire": ["Manchester", "Nashua", "Concord", "Derry", "Dover", "Rochester", "Salem"],
            "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Edison", "Woodbridge", "Lakewood", "Toms River", "Hamilton", "Trenton", "Clifton", "Camden", "Brick", "Cherry Hill", "Passaic", "Middletown", "Union City", "Old Bridge", "Gloucester", "East Orange", "Bayonne", "Franklin", "North Bergen", "Vineland", "Piscataway", "New Brunswick", "Jackson", "Wayne", "Somerset", "South Brunswick", "Rahway", "Nutley", "Hoboken", "West New York", "Sayreville", "West Orange", "Livingston", "Millville", "Maplewood", "Red Bank"],
            "New Mexico": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell", "Farmington", "Clovis"],
            "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany", "New Rochelle", "Mount Vernon", "Schenectady", "Utica", "White Plains", "Hempstead", "Troy", "Niagara Falls", "Binghamton", "Freeport", "Valley Stream", "Long Beach", "Rome", "North Tonawanda", "Poughkeepsie", "Paterson", "Jamestown", "Middletown", "Elmira", "Johnstown", "Glens Falls", "Cohoes", "Amsterdam", "Newburgh", "Ogdensburg", "Plattsburgh", "Peekskill", "Watertown", "Tonawanda", "Corning", "Lockport", "Mount Kisco", "Geneva", "Mamaroneck", "Saratoga Springs", "Cortland", "Little Falls", "Oneonta", "Olean", "Sherrill", "Cohoes", "Batavia", "Gloversville", "Rensselaer", "Amsterdam"],
            "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville", "Cary", "Wilmington"],
            "North Dakota": ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo", "Williston", "Dickinson"],
            "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton", "Parma", "Canton"],
            "Oklahoma": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond", "Midwest City", "Lawton"],
            "Oregon": ["Portland", "Salem", "Eugene", "Gresham", "Hillsboro", "Beaverton", "Bend"],
            "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton", "Bethlehem", "Lancaster"],
            "Rhode Island": ["Providence", "Cranston", "Warwick", "Pawtucket", "East Providence", "Woonsocket"],
            "South Carolina": ["Columbia", "Charleston", "North Charleston", "Mount Pleasant", "Rock Hill", "Greenville", "Sumter"],
            "South Dakota": ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown", "Mitchell"],
            "Tennessee": ["Memphis", "Nashville", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro", "Franklin"],
            "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo", "Lubbock", "Garland", "Irving"],
            "Utah": ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem", "Sandy"],
            "Vermont": ["Burlington", "South Burlington", "Rutland", "Barre", "Montpelier", "St. Albans"],
            "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News", "Alexandria", "Hampton"],
            "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent", "Everett"],
            "West Virginia": ["Charleston", "Huntington", "Morgantown", "Parkersburg", "Wheeling", "Weirton"],
            "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine", "Appleton", "Waukesha"],
            "Wyoming": ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs", "Buffalo"],
        }

        self.project_types = ["Estimatic", "Scheduling"]
        self.project_statuses = ["Completed", "In Progress", "Not Started"]
        self.task_statuses = ["Completed", "In Progress", "Not Done"]
        self.billable_options = ["Yes", "No"]

        # GUI style
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

        self.create_client_widgets(self.client_tab)
        self.create_project_manager_widgets(self.project_manager_tab)
        self.create_project_widgets(self.project_tab)
        self.create_task_widgets(self.task_tab)

        self.populate_client_list()
        self.populate_client_dropdown()
        self.populate_project_manager_list()
        self.populate_project_list()
        self.populate_task_list()

    def show_status_message(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

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

    def create_styles(self):
        self.master.option_add('*Font', ('Segoe UI', 10))
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.bg_color = "#ffffff"
        self.accent_color = "#0066cc"
        self.text_color = "#000000"
        self.row_even_color = "#f9f9f9"
        self.row_odd_color = "#e5e5e5"

        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color, padding=[10,5])
        self.style.map('TNotebook.Tab',
                       background=[('selected', self.accent_color)],
                       foreground=[('selected', '#ffffff')])

        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabelframe', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.accent_color, font=('Segoe UI', 11, 'bold'))
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)

        self.style.configure('TEntry',
                             fieldbackground='#ffffff',
                             foreground=self.text_color,
                             padding=5,
                             borderwidth=1,
                             relief='solid')
        self.style.configure('TCombobox',
                             fieldbackground='#ffffff',
                             background='#ffffff',
                             foreground=self.text_color,
                             padding=5,
                             borderwidth=1,
                             relief='solid')

        self.style.configure('Accent.TButton',
                             background=self.accent_color,
                             foreground='#ffffff',
                             font=('Segoe UI', 10, 'bold'),
                             padding=8)
        self.style.map('Accent.TButton',
                       background=[('active', '#004d99')],
                       foreground=[('active', '#ffffff')])

        self.style.configure('TButton',
                             background='#cccccc',
                             foreground=self.text_color,
                             font=('Segoe UI', 10, 'bold'),
                             padding=8)
        self.style.map('TButton',
                       background=[('active', '#b3b3b3')],
                       foreground=[('active', '#000000')])

        self.style.configure('Treeview',
                             background=self.bg_color,
                             foreground=self.text_color,
                             fieldbackground=self.bg_color,
                             rowheight=28,
                             font=('Segoe UI', 10),
                             bordercolor=self.bg_color,
                             borderwidth=1)
        self.style.configure('Treeview.Heading',
                             background=self.accent_color,
                             foreground='#ffffff',
                             font=('Segoe UI', 11, 'bold'))
        self.style.map('Treeview.Heading',
                       background=[('active', '#004d99')])

        self.client_list_tag_even = 'evenrow'
        self.client_list_tag_odd = 'oddrow'
        self.project_manager_list_tag_even = 'evenrow'
        self.project_manager_list_tag_odd = 'oddrow'
        self.project_list_tag_even = 'evenrow'
        self.project_list_tag_odd = 'oddrow'
        self.task_list_tag_even = 'evenrow'
        self.task_list_tag_odd = 'oddrow'

        self.style.map('Treeview',
                       foreground=[('selected', '#ffffff')],
                       background=[('selected', self.accent_color)])

    # Tables creation methods below
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
        except mysql.connector.Error as err:
            self.show_status_message(f"Error creating client table: {err}", error=True)

    def create_project_manager_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_manager (
                    pm_id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(255) NOT NULL,
                    manager_name VARCHAR(255) NOT NULL,
                    notes TEXT DEFAULT NULL,
                    FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            self.show_status_message(f"Error creating project_manager table: {err}", error=True)

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
                    FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            self.show_status_message(f"Error creating project table: {err}", error=True)

    def create_task_table_with_schema_update(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS task (
                    task_id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(255) NOT NULL,
                    project_no VARCHAR(255) NOT NULL,
                    task_name VARCHAR(255) NOT NULL,
                    billable ENUM('Yes', 'No') NOT NULL,
                    hourly_rate DECIMAL(10,2) DEFAULT NULL,
                    lumpsum DECIMAL(10,2) DEFAULT NULL,
                    task_status VARCHAR(20),
                    notes TEXT DEFAULT NULL,
                    FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE,
                    FOREIGN KEY (project_no) REFERENCES project(project_no) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
            self.cursor.execute("SHOW COLUMNS FROM task")
            columns = [column[0].lower() for column in self.cursor.fetchall()]
            alters = []
            if 'hourly_rate' not in columns:
                alters.append("ADD COLUMN hourly_rate DECIMAL(10,2) DEFAULT NULL")
            if 'lumpsum' not in columns:
                alters.append("ADD COLUMN lumpsum DECIMAL(10,2) DEFAULT NULL")
            if 'notes' not in columns:
                alters.append("ADD COLUMN notes TEXT DEFAULT NULL")
            if alters:
                alter_statement = f"ALTER TABLE task {', '.join(alters)}"
                self.cursor.execute(alter_statement)
                self.conn.commit()
        except mysql.connector.Error as err:
            self.show_status_message(f"Error creating/updating task table: {err}", error=True)

    # --- Client tab widgets and methods ---
    def create_client_widgets(self, parent):
        parent.configure(style='TFrame')
        input_frame = ttk.LabelFrame(parent, text="Client Details", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Client ID (unique):").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.client_id_entry = ttk.Entry(input_frame, width=30)
        self.client_id_entry.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        ttk.Label(input_frame, text="Client Name:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Address:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.address_entry = ttk.Entry(input_frame, width=30)
        self.address_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="State:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.state_combo = ttk.Combobox(input_frame, values=self.states, state="readonly")
        self.state_combo.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        self.state_combo.bind("<<ComboboxSelected>>", self.update_cities)

        ttk.Label(input_frame, text="City:").grid(row=4, column=0, padx=8, pady=8, sticky="w")
        self.city_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.city_combo.grid(row=4, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Zip Code:").grid(row=5, column=0, padx=8, pady=8, sticky="w")
        self.zip_entry = ttk.Entry(input_frame, width=10)
        self.zip_entry.grid(row=5, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Notes:").grid(row=6, column=0, padx=8, pady=8, sticky="nw")
        self.notes_text = tk.Text(input_frame, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.notes_text.grid(row=6, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        buttons_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(buttons_frame, text="Add New Client", command=self.add_client).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Update Client", command=self.update_client).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Delete Client", command=self.delete_client).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        list_frame = ttk.LabelFrame(parent, text="Existing Clients", padding=10)
        list_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        self.client_list = ttk.Treeview(list_frame, columns=("ID", "Name", "State", "City"), show="headings")
        self.client_list.heading("ID", text="Client ID")
        self.client_list.heading("Name", text="Client Name")
        self.client_list.heading("State", text="State")
        self.client_list.heading("City", text="City")
        self.client_list.column("ID", width=80, anchor='center')
        self.client_list.column("Name", stretch=tk.YES)
        self.client_list.column("State", width=120, anchor='center')
        self.client_list.column("City", width=150, anchor='center')
        self.client_list.pack(expand=True, fill="both")

        self.client_list.tag_configure('evenrow', background=self.row_even_color)
        self.client_list.tag_configure('oddrow', background=self.row_odd_color)

        self.client_list.bind("<Double-1>", self.load_client_details)

    def update_cities(self, event=None):
        state = self.state_combo.get()
        self.city_combo['values'] = self.cities_by_state.get(state, [])
        self.city_combo.set('')

    def add_client(self):
        client_id = self.client_id_entry.get().strip()
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        state = self.state_combo.get().strip()
        city = self.city_combo.get().strip()
        zip_code = self.zip_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not client_id:
            self.show_status_message("Client ID cannot be empty.", True)
            return
        if not name:
            self.show_status_message("Client Name cannot be empty.", True)
            return
        if zip_code and not zip_code.isdigit():
            self.show_status_message("Zip Code must be numeric.", True)
            return

        try:
            self.cursor.execute("SELECT client_id FROM client WHERE client_id=%s", (client_id,))
            if self.cursor.fetchone():
                self.show_status_message(f"Client ID '{client_id}' already exists.", True)
                return
            self.cursor.execute(
                "INSERT INTO client (client_id, client_name, client_address, state, city, zip_code, notes) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (client_id, name, address, state, city, zip_code if zip_code else None, notes if notes else None)
            )
            self.conn.commit()
            self.show_status_message(f"Client '{name}' added with ID: {client_id}")
            self.clear_client_input_fields()
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_client_dropdown()
            self.populate_task_client_dropdown()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding client: {e}", True)

    def update_client(self):
        client_id = self.client_id_entry.get().strip()
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        state = self.state_combo.get().strip()
        city = self.city_combo.get().strip()
        zip_code = self.zip_entry.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not client_id:
            self.show_status_message("Client ID cannot be empty.", True)
            return
        if not name:
            self.show_status_message("Client Name cannot be empty.", True)
            return
        if zip_code and not zip_code.isdigit():
            self.show_status_message("Zip Code must be numeric.", True)
            return

        try:
            self.cursor.execute("SELECT client_id FROM client WHERE client_id=%s", (client_id,))
            if not self.cursor.fetchone():
                self.show_status_message(f"Client ID '{client_id}' does not exist.", True)
                return
            self.cursor.execute(
                "UPDATE client SET client_name=%s, client_address=%s, state=%s, city=%s, zip_code=%s, notes=%s WHERE client_id=%s",
                (name, address, state, city, zip_code if zip_code else None, notes if notes else None, client_id)
            )
            self.conn.commit()
            self.show_status_message(f"Client '{name}' updated successfully.")
            self.clear_client_input_fields()
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_client_dropdown()
            self.populate_task_client_dropdown()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating client: {e}", True)

    def delete_client(self):
        client_id = self.client_id_entry.get().strip()
        if not client_id:
            self.show_status_message("Client ID cannot be empty.", True)
            return
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete client with ID: {client_id}?"):
            return
        try:
            self.cursor.execute("DELETE FROM project WHERE client_id=%s", (client_id,))
            self.cursor.execute("DELETE FROM project_manager WHERE client_id=%s", (client_id,))
            self.cursor.execute("DELETE FROM client WHERE client_id=%s", (client_id,))
            self.conn.commit()
            self.show_status_message(f"Client '{client_id}' deleted along with related projects and managers.")
            self.clear_client_input_fields()
            self.populate_client_list()
            self.populate_client_dropdown()
            self.populate_project_manager_client_dropdown()
            self.populate_project_manager_list()
            self.populate_task_client_dropdown()
            self.populate_project_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting client: {e}", True)

    def load_client_details(self, event):
        item = self.client_list.focus()
        if not item:
            return
        values = self.client_list.item(item, "values")
        client_id = values[0]
        try:
            self.cursor.execute(
                "SELECT client_name, client_address, state, city, zip_code, notes FROM client WHERE client_id=%s", (client_id,)
            )
            row = self.cursor.fetchone()
            if row:
                self.client_id_entry.delete(0, tk.END)
                self.client_id_entry.insert(0, client_id)
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, row[0])
                self.address_entry.delete(0, tk.END)
                self.address_entry.insert(0, row[1] if row[1] else "")
                self.state_combo.set(row[2] if row[2] else "")
                self.update_cities()
                self.city_combo.set(row[3] if row[3] else "")
                self.zip_entry.delete(0, tk.END)
                self.zip_entry.insert(0, row[4] if row[4] else "")
                self.notes_text.delete('1.0', tk.END)
                self.notes_text.insert(tk.END, row[5] if row[5] else "")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading client: {e}", True)

    def clear_client_input_fields(self):
        self.client_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.state_combo.set('')
        self.city_combo.set('')
        self.zip_entry.delete(0, tk.END)
        self.notes_text.delete('1.0', tk.END)

    def populate_client_list(self):
        self.client_list.delete(*self.client_list.get_children())
        try:
            self.cursor.execute("SELECT client_id, client_name, state, city FROM client ORDER BY client_name")
            rows = self.cursor.fetchall()
            for i, row in enumerate(rows):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.client_list.insert('', tk.END, values=row, tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching clients: {e}", True)

    def populate_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            rows = self.cursor.fetchall()
            client_names = [f"{r[1]} ({r[0]})" for r in rows]
            self.client_combo['values'] = client_names
            if client_names and not self.client_combo.get():
                self.client_combo.set(client_names[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching clients for dropdown: {e}", True)

    # --- Project Manager tab ---
    def create_project_manager_widgets(self, parent):
        parent.configure(style='TFrame')
        input_frame = ttk.LabelFrame(parent, text="Project Manager Details", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.pm_client_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.pm_client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Manager Name:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.manager_name_entry = ttk.Entry(input_frame, width=30)
        self.manager_name_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, padx=8, pady=8, sticky="nw")
        self.pm_notes_text = tk.Text(input_frame, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.pm_notes_text.grid(row=2, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        buttons_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(buttons_frame, text="Add Manager", command=self.add_project_manager).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Update Manager", command=self.update_project_manager).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Delete Manager", command=self.delete_project_manager).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        list_frame = ttk.LabelFrame(parent, text="Existing Project Managers", padding=10)
        list_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        self.project_manager_list = ttk.Treeview(list_frame, columns=("PM ID", "Client ID", "Manager Name"), show="headings")
        self.project_manager_list.heading("PM ID", text="PM ID")
        self.project_manager_list.heading("Client ID", text="Client ID")
        self.project_manager_list.heading("Manager Name", text="Manager Name")
        self.project_manager_list.column("PM ID", width=70, anchor='center')
        self.project_manager_list.column("Client ID", width=80, anchor='center')
        self.project_manager_list.column("Manager Name", stretch=tk.YES)
        self.project_manager_list.pack(expand=True, fill="both")

        self.project_manager_list.tag_configure('evenrow', background=self.row_even_color)
        self.project_manager_list.tag_configure('oddrow', background=self.row_odd_color)

        self.project_manager_list.bind("<Double-1>", self.load_project_manager_details)

        self.populate_project_manager_client_dropdown()

    def populate_project_manager_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            rows = self.cursor.fetchall()
            client_names = [f"{r[1]} ({r[0]})" for r in rows]
            self.pm_client_combo['values'] = client_names
            if client_names and not self.pm_client_combo.get():
                self.pm_client_combo.set(client_names[0])
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching clients for managers: {e}", True)

    def add_project_manager(self):
        client_with_id = self.pm_client_combo.get()
        manager_name = self.manager_name_entry.get().strip()
        notes = self.pm_notes_text.get('1.0', tk.END).strip()
        if not client_with_id:
            self.show_status_message("Please select a client for the manager.", True)
            return
        if not manager_name:
            self.show_status_message("Manager name cannot be empty.", True)
            return
        client_id = client_with_id.split("(")[-1][:-1].strip()
        try:
            self.cursor.execute("INSERT INTO project_manager (client_id, manager_name, notes) VALUES (%s, %s, %s)", (client_id, manager_name, notes if notes else None))
            self.conn.commit()
            self.show_status_message(f"Manager '{manager_name}' added for client '{client_id}'.")
            self.clear_project_manager_input_fields()
            self.populate_project_manager_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding project manager: {e}", True)

    def update_project_manager(self):
        selected = self.project_manager_list.focus()
        if not selected:
            self.show_status_message("Select a manager to update.", True)
            return
        pm_id = self.project_manager_list.item(selected, "values")[0]
        client_with_id = self.pm_client_combo.get()
        manager_name = self.manager_name_entry.get().strip()
        notes = self.pm_notes_text.get('1.0', tk.END).strip()
        if not client_with_id or not manager_name:
            self.show_status_message("Client and Manager name must be specified.", True)
            return
        client_id = client_with_id.split("(")[-1][:-1].strip()
        try:
            self.cursor.execute("UPDATE project_manager SET client_id=%s, manager_name=%s, notes=%s WHERE pm_id=%s", (client_id, manager_name, notes if notes else None, pm_id))
            self.conn.commit()
            self.show_status_message("Project Manager updated successfully.")
            self.clear_project_manager_input_fields()
            self.populate_project_manager_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating project manager: {e}", True)

    def delete_project_manager(self):
        selected = self.project_manager_list.focus()
        if not selected:
            self.show_status_message("Select a manager to delete.", True)
            return
        pm_id = self.project_manager_list.item(selected, "values")[0]
        manager_name = self.project_manager_list.item(selected, "values")[2]
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete manager '{manager_name}'?"):
            return
        try:
            self.cursor.execute("DELETE FROM project_manager WHERE pm_id=%s", (pm_id,))
            self.conn.commit()
            self.show_status_message("Project Manager deleted successfully.")
            self.clear_project_manager_input_fields()
            self.populate_project_manager_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting project manager: {e}", True)

    def load_project_manager_details(self, event):
        selected = self.project_manager_list.focus()
        if not selected:
            return
        values = self.project_manager_list.item(selected, "values")
        pm_id, client_id, manager_name = values
        try:
            self.cursor.execute("SELECT client_name, notes FROM client WHERE client_id=%s", (client_id,))
            client_row = self.cursor.fetchone()
            client_name = client_row[0] if client_row else client_id
            self.pm_client_combo.set(f"{client_name} ({client_id})")
            self.manager_name_entry.delete(0, tk.END)
            self.manager_name_entry.insert(0, manager_name)
            self.cursor.execute("SELECT notes FROM project_manager WHERE pm_id=%s", (pm_id,))
            notes_row = self.cursor.fetchone()
            self.pm_notes_text.delete('1.0', tk.END)
            self.pm_notes_text.insert(tk.END, notes_row[0] if notes_row and notes_row[0] else "")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading manager details: {e}", True)

    def clear_project_manager_input_fields(self):
        self.pm_client_combo.set('')
        self.manager_name_entry.delete(0, tk.END)
        self.pm_notes_text.delete('1.0', tk.END)

    def populate_project_manager_list(self):
        self.project_manager_list.delete(*self.project_manager_list.get_children())
        try:
            self.cursor.execute("SELECT pm_id, client_id, manager_name FROM project_manager ORDER BY client_id")
            rows = self.cursor.fetchall()
            for i, row in enumerate(rows):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.project_manager_list.insert('', tk.END, values=row, tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching project managers: {e}", True)

    # --- Project tab ---
    def create_project_widgets(self, parent):
        parent.configure(style='TFrame')
        input_frame = ttk.LabelFrame(parent, text="Project Details", padding=15)
        input_frame.pack(fill='x', padx=15, pady=15)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.client_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.client_combo.bind("<<ComboboxSelected>>", self.on_project_client_selected)

        ttk.Label(input_frame, text="Project No (unique):").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.project_no_entry = ttk.Entry(input_frame, width=30)
        self.project_no_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Project Name:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.project_name_entry = ttk.Entry(input_frame, width=30)
        self.project_name_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Project Manager:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.project_manager_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.project_manager_combo.grid(row=3, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Project Type:").grid(row=4, column=0, padx=8, pady=8, sticky="w")
        self.project_type_combo = ttk.Combobox(input_frame, values=self.project_types, state="readonly")
        self.project_type_combo.grid(row=4, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Project Status:").grid(row=5, column=0, padx=8, pady=8, sticky="w")
        self.project_status_combo = ttk.Combobox(input_frame, values=self.project_statuses, state="readonly")
        self.project_status_combo.grid(row=5, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Notes:").grid(row=6, column=0, padx=8, pady=8, sticky="nw")
        self.project_notes_text = tk.Text(input_frame, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.project_notes_text.grid(row=6, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.pack(fill='x', padx=15, pady=15)

        ttk.Button(buttons_frame, text="Add New Project", command=self.add_project).pack(side='left', expand=True,
                                                                                         fill='x',
                                                                                         padx=5)
        ttk.Button(buttons_frame, text="Update Project", command=self.update_project).pack(side='left', expand=True,
                                                                                           fill='x', padx=5)
        ttk.Button(buttons_frame, text="Delete Project", command=self.delete_project).pack(side='left', expand=True,
                                                                                           fill='x', padx=5)

        list_frame = ttk.LabelFrame(parent, text="Existing Projects", padding=10)
        list_frame.pack(expand=True, fill='both', padx=15, pady=15)

        columns = ("Project No", "Client ID", "Project Name", "Manager", "Type", "Status", "Notes")
        self.project_list = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.project_list.heading(col, text=col)
        self.project_list.column("Project No", width=100, anchor='center')
        self.project_list.column("Client ID", width=80, anchor='center')
        self.project_list.column("Project Name", stretch=tk.YES)
        self.project_list.column("Manager", width=140, anchor='center')
        self.project_list.column("Type", width=100, anchor='center')
        self.project_list.column("Status", width=100, anchor='center')
        self.project_list.column("Notes", width=180, anchor='w')
        self.project_list.pack(expand=True, fill='both')

        self.project_list.tag_configure('evenrow', background=self.row_even_color)
        self.project_list.tag_configure('oddrow', background=self.row_odd_color)

        self.project_list.bind("<Double-1>", self.load_project_details)

        self.populate_client_dropdown()
        self.populate_project_manager_dropdown()
        self.populate_project_list()

    def on_project_client_selected(self, event=None):
        client_with_id = self.client_combo.get()
        if client_with_id:
            client_id = client_with_id.split("(")[-1][:-1].strip()
            self.populate_project_manager_dropdown(client_id)
        else:
            self.project_manager_combo['values'] = []
            self.project_manager_combo.set('')

    def populate_project_manager_dropdown(self, client_id=None):
        if not client_id:
            self.project_manager_combo['values'] = []
            self.project_manager_combo.set('')
            return
        try:
            self.cursor.execute("SELECT manager_name FROM project_manager WHERE client_id=%s ORDER BY manager_name",
                                (client_id,))
            managers = [r[0] for r in self.cursor.fetchall()]
            self.project_manager_combo['values'] = managers
            if managers:
                self.project_manager_combo.set(managers[0])
            else:
                self.project_manager_combo.set('')
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading project managers: {e}", error=True)

    def add_project(self):
        client_with_id = self.client_combo.get()
        project_no = self.project_no_entry.get().strip()
        project_name = self.project_name_entry.get().strip()
        project_manager = self.project_manager_combo.get().strip()
        project_type = self.project_type_combo.get().strip()
        project_status = self.project_status_combo.get().strip()
        notes = self.project_notes_text.get('1.0', 'end').strip()

        if not client_with_id or not project_no or not project_name:
            self.show_status_message("Client, Project No, and Project Name are required.", error=True)
            return

        client_id = client_with_id.split("(")[-1][:-1].strip()

        try:
            self.cursor.execute("SELECT project_no FROM project WHERE project_no=%s", (project_no,))
            if self.cursor.fetchone():
                self.show_status_message("Project No already exists.", error=True)
                return
            self.cursor.execute(
                "INSERT INTO project (project_no, client_id, project_name, client_project_manager, project_type, project_status, notes) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (project_no, client_id, project_name, project_manager if project_manager else None,
                 project_type if project_type else None,
                 project_status if project_status else None, notes if notes else None)
            )
            self.conn.commit()
            self.show_status_message(f"Project {project_name} added.")
            self.clear_project_input_fields()
            self.populate_project_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding project: {e}", error=True)

    def update_project(self):
        project_no = self.project_no_entry.get().strip()
        client_with_id = self.client_combo.get()
        project_name = self.project_name_entry.get().strip()
        project_manager = self.project_manager_combo.get().strip()
        project_type = self.project_type_combo.get().strip()
        project_status = self.project_status_combo.get().strip()
        notes = self.project_notes_text.get('1.0', 'end').strip()

        if not project_no or not client_with_id or not project_name:
            self.show_status_message("Project No, Client, and Project Name are required.", error=True)
            return

        client_id = client_with_id.split("(")[-1][:-1].strip()

        try:
            self.cursor.execute("SELECT project_no FROM project WHERE project_no=%s", (project_no,))
            if not self.cursor.fetchone():
                self.show_status_message("Project does not exist.", error=True)
                return

            self.cursor.execute(
                "UPDATE project SET client_id=%s, project_name=%s, client_project_manager=%s, project_type=%s, "
                "project_status=%s, notes=%s WHERE project_no=%s",
                (client_id, project_name, project_manager if project_manager else None,
                 project_type if project_type else None,
                 project_status if project_status else None, notes if notes else None, project_no)
            )
            self.conn.commit()
            self.show_status_message(f"Project {project_name} updated.")
            self.clear_project_input_fields()
            self.populate_project_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating project: {e}", error=True)

    def delete_project(self):
        project_no = self.project_no_entry.get().strip()
        if not project_no:
            self.show_status_message("Project No is required.", error=True)
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete project {project_no}?"):
            return
        try:
            self.cursor.execute("DELETE FROM project WHERE project_no=%s", (project_no,))
            self.conn.commit()
            self.show_status_message(f"Project {project_no} deleted.")
            self.clear_project_input_fields()
            self.populate_project_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting project: {e}", error=True)

    def load_project_details(self, event):
        selected = self.project_list.focus()
        if not selected:
            return
        values = self.project_list.item(selected, "values")
        project_no = values[0]
        try:
            self.cursor.execute(
                "SELECT client_id, project_name, client_project_manager, project_type, project_status, notes FROM project WHERE project_no=%s",
                (project_no,))
            row = self.cursor.fetchone()
            if row:
                client_id, project_name, manager, project_type, project_status, notes = row
                self.project_no_entry.delete(0, tk.END)
                self.project_no_entry.insert(0, project_no)
                self.project_name_entry.delete(0, tk.END)
                self.project_name_entry.insert(0, project_name)
                self.project_type_combo.set(project_type if project_type else '')
                self.project_status_combo.set(project_status if project_status else '')
                self.project_notes_text.delete('1.0', tk.END)
                self.project_notes_text.insert(tk.END, notes if notes else '')
                self.cursor.execute("SELECT client_name FROM client WHERE client_id=%s", (client_id,))
                c = self.cursor.fetchone()
                client_name = c[0] if c else client_id
                self.client_combo.set(f"{client_name} ({client_id})")
                self.on_project_client_selected(None)
                if manager in self.project_manager_combo['values']:
                    self.project_manager_combo.set(manager)
                else:
                    self.project_manager_combo.set('')
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading project details: {e}", error=True)

    def clear_project_input_fields(self):
        self.client_combo.set('')
        self.project_no_entry.delete(0, tk.END)
        self.project_name_entry.delete(0, tk.END)
        self.project_manager_combo.set('')
        self.project_type_combo.set('')
        self.project_status_combo.set('')
        self.project_notes_text.delete('1.0', tk.END)

    def populate_project_list(self):
        self.project_list.delete(*self.project_list.get_children())
        try:
            self.cursor.execute(
                "SELECT project_no, client_id, project_name, client_project_manager, project_type, project_status, notes FROM project ORDER BY client_id")
            rows = self.cursor.fetchall()
            for i, row in enumerate(rows):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.project_list.insert('', tk.END, values=row, tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching projects: {e}", error=True)

    # --- Task tab ---
    def create_task_widgets(self, parent):
        parent.configure(style='TFrame')
        input_frame = ttk.LabelFrame(parent, text="Task Details", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text="Client:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.task_client_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.task_client_combo.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.task_client_combo.bind("<<ComboboxSelected>>", self.on_task_client_selected)

        ttk.Label(input_frame, text="Project:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.task_project_combo = ttk.Combobox(input_frame, values=[], state="readonly")
        self.task_project_combo.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Task Name:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.task_name_entry = ttk.Entry(input_frame, width=30)
        self.task_name_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Billable:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.billable_combo = ttk.Combobox(input_frame, values=self.billable_options, state="readonly")
        self.billable_combo.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        self.billable_combo.bind("<<ComboboxSelected>>", self.on_billable_changed)

        self.billing_details_frame = ttk.Frame(input_frame)
        self.billing_details_frame.grid(row=4, column=0, columnspan=4, sticky="ew")
        self.billing_details_frame.columnconfigure(1, weight=1)
        self.billing_details_frame.columnconfigure(3, weight=1)

        self.hourly_rate_label = ttk.Label(self.billing_details_frame, text="Hourly Rate:")
        self.hourly_rate_entry = ttk.Entry(self.billing_details_frame, width=15)
        self.lumpsum_label = ttk.Label(self.billing_details_frame, text="Lumpsum:")
        self.lumpsum_entry = ttk.Entry(self.billing_details_frame, width=15)

        self.hourly_rate_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.hourly_rate_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.lumpsum_label.grid(row=0, column=2, padx=20, pady=5, sticky='w')
        self.lumpsum_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        self.hourly_rate_label.grid_remove()
        self.hourly_rate_entry.grid_remove()
        self.lumpsum_label.grid_remove()
        self.lumpsum_entry.grid_remove()

        ttk.Label(input_frame, text="Task Status:").grid(row=5, column=0, padx=8, pady=8, sticky="w")
        self.task_status_combo = ttk.Combobox(input_frame, values=self.task_statuses, state="readonly")
        self.task_status_combo.grid(row=5, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(input_frame, text="Notes:").grid(row=6, column=0, padx=8, pady=8, sticky="nw")
        self.task_notes_text = tk.Text(input_frame, height=4, width=35, wrap='word', relief='solid', borderwidth=1)
        self.task_notes_text.grid(row=6, column=1, columnspan=3, padx=8, pady=8, sticky="ew")

        buttons_frame = ttk.Frame(parent, padding=15)
        buttons_frame.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        buttons_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(buttons_frame, text="Add New Task", command=self.add_task).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Update Task", command=self.update_task).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(buttons_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        list_frame = ttk.LabelFrame(parent, text="Existing Tasks", padding=10)
        list_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        columns = ("Task ID", "Client ID", "Project No", "Task Name", "Billable", "Hourly Rate", "Lumpsum", "Status", "Notes")
        self.task_list = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.task_list.heading(col, text=col)
        self.task_list.column("Task ID", width=70, anchor='center')
        self.task_list.column("Client ID", width=70, anchor='center')
        self.task_list.column("Project No", width=100, anchor='center')
        self.task_list.column("Task Name", stretch=tk.YES)
        self.task_list.column("Billable", width=70, anchor='center')
        self.task_list.column("Hourly Rate", width=90, anchor='center')
        self.task_list.column("Lumpsum", width=90, anchor='center')
        self.task_list.column("Status", width=90, anchor='center')
        self.task_list.column("Notes", width=200, stretch=tk.YES)

        self.task_list.pack(expand=True, fill="both")

        self.task_list.tag_configure('evenrow', background=self.row_even_color)
        self.task_list.tag_configure('oddrow', background=self.row_odd_color)

        self.task_list.bind("<Double-1>", self.load_task_details)

        self.populate_task_client_dropdown()

    def on_billable_changed(self, event):
        selected = self.billable_combo.get()
        self.hourly_rate_label.grid_remove()
        self.hourly_rate_entry.grid_remove()
        self.lumpsum_label.grid_remove()
        self.lumpsum_entry.grid_remove()
        if selected == "Yes":
            self.hourly_rate_label.grid()
            self.hourly_rate_entry.grid()
            self.lumpsum_label.grid()
            self.lumpsum_entry.grid()

    def validate_decimal(self, value):
        if value == '':
            return True
        try:
            fval = float(value)
            if fval < 0:
                return False
            if '.' in value and len(value.split('.')[1]) > 2:
                return False
            return True
        except ValueError:
            return False

    def add_task(self):
        client_with_id = self.task_client_combo.get()
        project_with_no = self.task_project_combo.get()
        task_name = self.task_name_entry.get().strip()
        billable = self.billable_combo.get()
        hourly_rate = self.hourly_rate_entry.get().strip()
        lumpsum = self.lumpsum_entry.get().strip()
        task_status = self.task_status_combo.get().strip()
        notes = self.task_notes_text.get('1.0', 'end').strip()

        if not client_with_id:
            self.show_status_message("Please select a client.", True)
            return
        if not project_with_no:
            self.show_status_message("Please select a project.", True)
            return
        if not task_name:
            self.show_status_message("Task name cannot be empty.", True)
            return
        if billable not in self.billable_options:
            self.show_status_message("Please select if task is billable or not.", True)
            return

        client_id = client_with_id.split("(")[-1][:-1].strip()
        project_no = project_with_no.split("(")[-1][:-1].strip()

        if billable == "Yes":
            if not self.validate_decimal(hourly_rate) or not self.validate_decimal(lumpsum):
                self.show_status_message("Hourly rate and lumpsum must be positive numbers with up to 2 decimals.", True)
                return
            if (not hourly_rate or float(hourly_rate) == 0) and (not lumpsum or float(lumpsum) == 0):
                self.show_status_message("Enter either hourly rate or lumpsum greater than zero.", True)
                return
        else:
            hourly_rate = None
            lumpsum = None

        try:
            self.cursor.execute(
                "INSERT INTO task (client_id, project_no, task_name, billable, hourly_rate, lumpsum, task_status, notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (client_id, project_no, task_name, billable, float(hourly_rate) if hourly_rate else None, float(lumpsum) if lumpsum else None, task_status, notes if notes else None)
            )
            self.conn.commit()
            self.show_status_message(f"Task '{task_name}' added successfully.")
            self.clear_task_input_fields()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error adding task: {e}", True)

    def update_task(self):
        selected = self.task_list.focus()
        if not selected:
            self.show_status_message("Select a task to update.", True)
            return
        task_id = self.task_list.item(selected, "values")[0]
        client_with_id = self.task_client_combo.get()
        project_with_no = self.task_project_combo.get()
        task_name = self.task_name_entry.get().strip()
        billable = self.billable_combo.get()
        hourly_rate = self.hourly_rate_entry.get().strip()
        lumpsum = self.lumpsum_entry.get().strip()
        task_status = self.task_status_combo.get().strip()
        notes = self.task_notes_text.get('1.0', 'end').strip()

        if not client_with_id:
            self.show_status_message("Please select a client.", True)
            return
        if not project_with_no:
            self.show_status_message("Please select a project.", True)
            return
        if not task_name:
            self.show_status_message("Task name cannot be empty.", True)
            return
        if billable not in self.billable_options:
            self.show_status_message("Please select if task is billable or not.", True)
            return

        client_id = client_with_id.split("(")[-1][:-1].strip()
        project_no = project_with_no.split("(")[-1][:-1].strip()

        if billable == "Yes":
            if not self.validate_decimal(hourly_rate) or not self.validate_decimal(lumpsum):
                self.show_status_message("Hourly rate and lumpsum must be positive numbers with up to 2 decimals.", True)
                return
            if (not hourly_rate or float(hourly_rate) == 0) and (not lumpsum or float(lumpsum) == 0):
                self.show_status_message("Enter either hourly rate or lumpsum greater than zero.", True)
                return
        else:
            hourly_rate = None
            lumpsum = None

        try:
            self.cursor.execute(
                "UPDATE task SET client_id=%s, project_no=%s, task_name=%s, billable=%s, hourly_rate=%s, lumpsum=%s, task_status=%s, notes=%s WHERE task_id=%s",
                (client_id, project_no, task_name, billable, float(hourly_rate) if hourly_rate else None, float(lumpsum) if lumpsum else None, task_status, notes if notes else None, task_id)
            )
            self.conn.commit()
            self.show_status_message(f"Task '{task_name}' updated successfully.")
            self.clear_task_input_fields()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error updating task: {e}", True)

    def delete_task(self):
        selected = self.task_list.focus()
        if not selected:
            self.show_status_message("Select a task to delete.", True)
            return
        task_id = self.task_list.item(selected, "values")[0]
        task_name = self.task_list.item(selected, "values")[3]
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete task '{task_name}'?"):
            return
        try:
            self.cursor.execute("DELETE FROM task WHERE task_id=%s", (task_id,))
            self.conn.commit()
            self.show_status_message("Task deleted successfully.")
            self.clear_task_input_fields()
            self.populate_task_list()
        except mysql.connector.Error as e:
            self.show_status_message(f"Error deleting task: {e}", True)

    def load_task_details(self, event):
        selected = self.task_list.focus()
        if not selected:
            return
        values = self.task_list.item(selected, "values")
        task_id = values[0]
        try:
            self.cursor.execute(
                "SELECT client_id, project_no, task_name, billable, hourly_rate, lumpsum, task_status, notes FROM task WHERE task_id=%s", (task_id,))
            row = self.cursor.fetchone()
            if row:
                client_id, project_no, task_name, billable, hourly_rate, lumpsum, status, notes = row
                self.task_name_entry.delete(0, tk.END)
                self.task_name_entry.insert(0, task_name)
                self.billable_combo.set(billable)
                self.on_billable_changed(None)
                if billable == "Yes":
                    self.hourly_rate_entry.delete(0, tk.END)
                    self.hourly_rate_entry.insert(0, str(hourly_rate) if hourly_rate else "")
                    self.lumpsum_entry.delete(0, tk.END)
                    self.lumpsum_entry.insert(0, str(lumpsum) if lumpsum else "")
                else:
                    self.hourly_rate_entry.delete(0, tk.END)
                    self.lumpsum_entry.delete(0, tk.END)
                self.task_status_combo.set(status if status else "")

                self.task_notes_text.delete('1.0', tk.END)
                self.task_notes_text.insert(tk.END, notes if notes else "")

                # Set client combobox
                self.cursor.execute("SELECT client_name FROM client WHERE client_id=%s", (client_id,))
                c = self.cursor.fetchone()
                client_name = c[0] if c else client_id
                self.task_client_combo.set(f"{client_name} ({client_id})")

                self.populate_task_project_dropdown(client_id)
                # Set project combobox
                self.cursor.execute("SELECT project_name FROM project WHERE project_no=%s", (project_no,))
                p = self.cursor.fetchone()
                project_name = p[0] if p else project_no
                self.task_project_combo.set(f"{project_name} ({project_no})")
        except mysql.connector.Error as e:
            self.show_status_message(f"Error loading task details: {e}", True)

    def clear_task_input_fields(self):
        self.task_client_combo.set('')
        self.task_project_combo.set('')
        self.task_project_combo['values'] = []
        self.task_name_entry.delete(0, tk.END)
        self.billable_combo.set('')
        self.hourly_rate_entry.delete(0, tk.END)
        self.lumpsum_entry.delete(0, tk.END)
        self.task_status_combo.set('')
        self.task_notes_text.delete('1.0', tk.END)
        self.hourly_rate_label.grid_remove()
        self.hourly_rate_entry.grid_remove()
        self.lumpsum_label.grid_remove()
        self.lumpsum_entry.grid_remove()

    def populate_task_client_dropdown(self):
        try:
            self.cursor.execute("SELECT client_id, client_name FROM client ORDER BY client_name")
            rows = self.cursor.fetchall()
            client_names = [f"{r[1]} ({r[0]})" for r in rows]
            self.task_client_combo['values'] = client_names
            if client_names and not self.task_client_combo.get():
                self.task_client_combo.set(client_names[0])
                self.on_task_client_selected(None)
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching clients for tasks: {e}", True)

    def on_task_client_selected(self, event):
        client_with_id = self.task_client_combo.get()
        if not client_with_id:
            self.task_project_combo.set('')
            self.task_project_combo['values'] = []
            return
        client_id = client_with_id.split("(")[-1][:-1].strip()
        self.populate_task_project_dropdown(client_id)

    def populate_task_project_dropdown(self, client_id):
        if not client_id:
            self.task_project_combo.set('')
            self.task_project_combo['values'] = []
            return
        try:
            self.cursor.execute("SELECT project_no, project_name FROM project WHERE client_id=%s ORDER BY client_id", (client_id,))
            rows = self.cursor.fetchall()
            projects = [f"{r[1]} ({r[0]})" for r in rows]
            self.task_project_combo['values'] = projects
            if projects:
                self.task_project_combo.set(projects[0])
            else:
                self.task_project_combo.set('')
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching projects for tasks: {e}", True)

    def populate_task_list(self):
        self.task_list.delete(*self.task_list.get_children())
        try:
            self.cursor.execute("SELECT task_id, client_id, project_no, task_name, billable, hourly_rate, lumpsum, task_status, notes FROM task ORDER BY client_id")
            rows = self.cursor.fetchall()
            for i, row in enumerate(rows):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                row = list(row)
                # Format hourly_rate and lumpsum
                if row[5] is None:
                    row[5] = ""
                else:
                    row[5] = f"{row[5]:.2f}"
                if row[6] is None:
                    row[6] = ""
                else:
                    row[6] = f"{row[6]:.2f}"
                if row[7] is None:
                    row[7] = ""
                if row[8] is None:
                    row[8] = ""
                self.task_list.insert('', tk.END, values=row, tags=(tag,))
        except mysql.connector.Error as e:
            self.show_status_message(f"Error fetching tasks: {e}", True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientManager(root)
    root.mainloop()

