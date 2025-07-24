import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import configparser
import os
import mysql.connector
import subprocess
import platform

# Import the manager classes from the other files
# Ensure these files (main_manager.py, timelog.py, employ_subconsultant.py)
# are in the same directory as this central_gui.py script.
from main_manager import ClientManager
from timelog import TimeLogManager
from employ_subconsultant import EmploySubconsultantManager


class MainApplication:
    """
    Centralized GUI application integrating Client & Project, Time Log,
    and Employ & Subconsultant management systems.
    """

    def __init__(self, master):
        self.master = master
        master.title("The Schedule Plus")
        master.geometry("1200x850")  # Increased height for the backup button
        master.configure(bg="#ffffff")  # White background for the main window

        # Apply consistent styling across the application
        self.create_styles()

        # Create the main notebook (tabbed interface)
        self.main_notebook = ttk.Notebook(master)
        self.main_notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create individual frames for each manager and add them as tabs
        self.client_project_frame = ttk.Frame(self.main_notebook)
        self.timelog_frame = ttk.Frame(self.main_notebook)
        self.employ_subconsultant_frame = ttk.Frame(self.main_notebook)

        self.main_notebook.add(self.client_project_frame, text="Client & Project Management")
        self.main_notebook.add(self.timelog_frame, text="Time Log Management")
        self.main_notebook.add(self.employ_subconsultant_frame, text="Employ & Subconsultant Management")

        # --- Add Backup Feature ---
        backup_frame = ttk.Frame(master, style='TFrame')
        backup_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.backup_button = ttk.Button(backup_frame, text="Download Database Backup", command=self.download_backup,
                                        style='Accent.TButton')
        self.backup_button.pack(pady=5)
        # --- End Backup Feature ---

        # Initialize manager instances to None, they will be created on demand
        self.client_manager = None
        self.timelog_manager = None
        self.employ_subconsultant_manager = None

        # Bind the tab change event
        self.main_notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Manually trigger the tab change for the first tab to load it
        self.on_tab_change(None)

    def on_tab_change(self, event):
        """
        Callback function executed when the selected tab changes.
        This function implements lazy loading of manager classes.
        """
        selected_tab_id = self.main_notebook.select()
        selected_tab_text = self.main_notebook.tab(selected_tab_id, "text")

        if selected_tab_text == "Client & Project Management" and self.client_manager is None:
            # Instantiate ClientManager only when its tab is first selected
            self.client_manager = ClientManager(self.client_project_frame)

        elif selected_tab_text == "Time Log Management" and self.timelog_manager is None:
            # Instantiate TimeLogManager only when its tab is first selected
            self.timelog_manager = TimeLogManager(self.timelog_frame)

        elif selected_tab_text == "Employ & Subconsultant Management" and self.employ_subconsultant_manager is None:
            # Instantiate EmploySubconsultantManager only when its tab is first selected
            self.employ_subconsultant_manager = EmploySubconsultantManager(self.employ_subconsultant_frame)

    def download_backup(self):
        """
        Handles the database backup process using mysqldump.
        """
        # 1. Load database configuration from config.ini
        config = configparser.ConfigParser()
        config_file = 'config.ini'
        if not os.path.exists(config_file):
            messagebox.showerror("Error", f"Configuration file '{config_file}' not found.")
            return

        config.read(config_file)
        if 'mysql' not in config:
            messagebox.showerror("Error", "Invalid configuration file: [mysql] section not found.")
            return

        db_config = config['mysql']
        db_host = db_config.get('host')
        db_user = db_config.get('user')
        db_password = db_config.get('password')
        db_name = db_config.get('database')

        if not all([db_host, db_user, db_password, db_name]):
            messagebox.showerror("Error", "Database configuration is incomplete in config.ini.")
            return

        # 2. Prompt user for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Backup Files", "*.sql"), ("All Files", "*.*")],
            title="Save Database Backup As"
        )
        if not filepath:
            return  # User cancelled the dialog

        # 3. Construct and execute the mysqldump command
        try:
            # For security, it's better to use an option file for credentials,
            # but for this application, we'll pass the password directly.
            command = [
                'mysqldump',
                f'--host={db_host}',
                f'--user={db_user}',
                f'--password={db_password}',
                db_name
            ]

            # On Windows, we need to ensure the command is run without creating a new console window
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            with open(filepath, 'w', encoding='utf-8') as f:
                process = subprocess.run(
                    command,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,  # This will raise a CalledProcessError for non-zero exit codes
                    startupinfo=startupinfo
                )

            messagebox.showinfo("Success", f"Database backup successfully saved to:\n{filepath}")

        except FileNotFoundError:
            messagebox.showerror("Error",
                                 "mysqldump command not found.\nPlease ensure that MySQL is installed and that its 'bin' directory is included in your system's PATH environment variable.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Backup Failed", f"An error occurred while creating the backup:\n\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("An Unexpected Error Occurred", f"An unexpected error occurred:\n\n{str(e)}")

    def create_styles(self):
        """
        Configures the ttk styles for a consistent look and feel across the application.
        This central style definition will be applied to all widgets.
        """
        self.master.option_add('*Font', ('Segoe UI', 10))  # Set default font for all widgets
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme for a modern look

        # Define color palette
        bg_color = "#ffffff"  # White background
        accent_color = "#0066cc"  # Blue accent for headings and selected items
        text_color = "#000000"  # Black text

        # Configure Notebook (tabs) style
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=bg_color,
                        foreground=text_color,
                        padding=[10, 5],
                        font=('Segoe UI', 10, 'bold'))  # Bold font for tabs
        style.map('TNotebook.Tab',
                  background=[('selected', accent_color), ('active', '#004d99')],  # Blue when selected/active
                  foreground=[('selected', '#ffffff'), ('active', '#ffffff')])  # White text when selected/active

        # Configure Frame and LabelFrame styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, foreground=text_color, borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label',
                        background=bg_color,
                        foreground=accent_color,
                        font=('Segoe UI', 11, 'bold'))  # Accent color for LabelFrame titles

        # Configure Label style
        style.configure('TLabel', background=bg_color, foreground=text_color)

        # Configure Entry and Combobox styles
        entry_style_config = {
            'fieldbackground': '#ffffff',
            'foreground': text_color,
            'padding': 5,
            'borderwidth': 1,
            'relief': 'solid',
            'bordercolor': '#cccccc'  # Light grey border
        }
        style.configure('TEntry', **entry_style_config)
        style.configure('TCombobox', **entry_style_config)

        # Configure Accent Button style (for primary actions)
        style.configure('Accent.TButton',
                        background=accent_color,
                        foreground='#ffffff',
                        font=('Segoe UI', 10, 'bold'),
                        padding=8,
                        relief='flat',  # Flat design
                        borderwidth=0,
                        focusthickness=0)  # Remove focus border
        style.map('Accent.TButton',
                  background=[('active', '#004d99')],  # Darker blue on hover/active
                  foreground=[('active', '#ffffff')])

        # Configure standard Button style (for secondary actions)
        style.configure('TButton',
                        background='#cccccc',  # Grey background
                        foreground=text_color,
                        font=('Segoe UI', 10, 'bold'),
                        padding=8,
                        relief='flat',
                        borderwidth=0,
                        focusthickness=0)
        style.map('TButton',
                  background=[('active', '#b3b3b3')],  # Darker grey on hover/active
                  foreground=[('active', '#000000')])

        # Configure Treeview style (general properties, not row tags)
        style.configure('Treeview',
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        rowheight=28,  # Height of each row
                        font=('Segoe UI', 10),
                        bordercolor='#cccccc',  # Light grey border for the Treeview widget itself
                        borderwidth=1,
                        relief='solid')
        style.configure('Treeview.Heading',
                        background=accent_color,
                        foreground='#ffffff',
                        font=('Segoe UI', 11, 'bold'),
                        relief='flat')  # Flat headings
        style.map('Treeview.Heading',
                  background=[('active', '#004d99')])  # Darker blue on heading hover/active


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
