import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import configparser
import os
import subprocess
import platform

# Import the actual manager classes from their files
from main_manager import ClientManager
from timelog import TimeLogManager
from employ_subconsultant import EmploySubconsultantManager


class MainApplication:
    """
    Centralized GUI application integrating all management systems.
    """

    def __init__(self, master):
        self.master = master
        master.title("The Schedule Plus")
        master.geometry("1200x800")  # Adjusted height after removing status bar
        master.configure(bg="#ffffff")

        self.create_styles()
        self.create_menu()

        # --- Main Notebook (Tabs) ---
        self.main_notebook = ttk.Notebook(master)
        self.main_notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create frames for each tab
        self.client_project_frame = ttk.Frame(self.main_notebook)
        self.timelog_frame = ttk.Frame(self.main_notebook)
        self.employ_subconsultant_frame = ttk.Frame(self.main_notebook)

        self.main_notebook.add(self.client_project_frame, text="Client & Project Management")
        self.main_notebook.add(self.timelog_frame, text="Time Log Management")
        self.main_notebook.add(self.employ_subconsultant_frame, text="Employ & Subconsultant")

        # --- Manager Instantiation ---
        self.client_manager = None
        self.timelog_manager = None
        self.employ_subconsultant_manager = None

        self.main_notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        self.load_client_manager()  # Load the first tab by default

    def create_menu(self):
        """Creates the main application menu bar."""
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database...", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def on_tab_selected(self, event):
        """Handles the lazy loading of managers when a tab is selected."""
        selected_tab = self.main_notebook.index(self.main_notebook.select())
        if selected_tab == 0 and self.client_manager is None:
            self.load_client_manager()
        elif selected_tab == 1 and self.timelog_manager is None:
            self.load_timelog_manager()
        elif selected_tab == 2 and self.employ_subconsultant_manager is None:
            self.load_employ_subconsultant_manager()

    def load_client_manager(self):
        try:
            self.client_manager = ClientManager(self.client_project_frame, self.show_status_message)
        except Exception as e:
            self.handle_load_error("Client & Project", e)

    def load_timelog_manager(self):
        try:
            self.timelog_manager = TimeLogManager(self.timelog_frame, self.show_status_message)
        except Exception as e:
            self.handle_load_error("Time Log", e)

    def load_employ_subconsultant_manager(self):
        try:
            self.employ_subconsultant_manager = EmploySubconsultantManager(self.employ_subconsultant_frame,
                                                                           self.show_status_message)
        except Exception as e:
            self.handle_load_error("Employ & Subconsultant", e)

    def handle_load_error(self, module_name, error):
        self.show_status_message(f"Could not load the {module_name} module: {error}", error=True)

    def create_styles(self):
        """Configures ttk styles for a consistent look and feel."""
        style = ttk.Style()
        style.theme_use('clam')
        bg_color, accent_color = "#ffffff", "#0066cc"

        style.configure('.', font=('Segoe UI', 10))
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', accent_color)], foreground=[('selected', 'white')])
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color,
                        font=('Segoe UI', 11, 'bold'))
        style.configure('TLabel', background=bg_color)
        style.configure('TButton', padding=8, font=('Segoe UI', 10, 'bold'))
        style.configure('Accent.TButton', background=accent_color, foreground='white')
        style.map('Accent.TButton', background=[('active', '#004d99')])
        style.configure('Treeview', rowheight=28)
        style.configure('Treeview.Heading', background=accent_color, foreground='white', font=('Segoe UI', 11, 'bold'))
        style.map('Treeview', background=[('selected', accent_color)])
        style.configure('total.Treeview', background='#e6f3ff', font=('Segoe UI', 10, 'bold'))

    def show_status_message(self, message, error=False):
        """Prints a message to the console and shows a popup for errors."""
        if error:
            print(f"ERROR: {message}")
            messagebox.showerror("Error", message)
        else:
            print(f"STATUS: {message}")

    def backup_database(self):
        """Performs a database backup using mysqldump."""
        config = configparser.ConfigParser()
        try:
            config.read('config.ini')
            db_config = config['mysql']
            user, password, database, host = db_config['user'], db_config['password'], db_config['database'], db_config[
                'host']
        except Exception as e:
            self.show_status_message(f"Could not read database info from config.ini: {e}", error=True)
            return

        backup_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL Backup", "*.sql")],
                                                   title="Save Database Backup")
        if not backup_path:
            self.show_status_message("Backup cancelled.")
            return

        try:
            command = ['mysqldump', f'--user={user}', f'--password={password}', f'--host={host}', '--protocol=tcp',
                       '--single-transaction', database]
            with open(backup_path, 'w', encoding='utf-8') as f:
                process = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True, check=False)

            if process.returncode == 0:
                self.show_status_message(f"Database backed up to {os.path.basename(backup_path)}")
                messagebox.showinfo("Backup Successful", f"Backup saved to:\n{backup_path}")
            else:
                self.handle_backup_error(process.stderr)

        except FileNotFoundError:
            error_msg = "Error: 'mysqldump' not found. Ensure MySQL client tools are installed and in your system's PATH."
            if platform.system() == "Darwin":
                error_msg += "\n\nOn macOS, you may need to add it to your path, e.g., in ~/.zshrc:\nexport PATH=$PATH:/usr/local/mysql/bin"
            self.show_status_message(error_msg, error=True)
        except Exception as e:
            self.handle_backup_error(str(e))

    def handle_backup_error(self, error_text):
        error_msg = f"Backup failed: {error_text.strip()}"
        self.show_status_message(error_msg, error=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()