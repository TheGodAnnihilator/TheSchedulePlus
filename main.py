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

        # Instantiate each manager class within its respective frame
        # Each manager will now manage its own GUI elements within its assigned frame.
        try:
            self.client_manager = ClientManager(self.client_project_frame)

        elif selected_tab_text == "Time Log Management" and self.timelog_manager is None:
            # Instantiate TimeLogManager only when its tab is first selected
            self.timelog_manager = TimeLogManager(self.timelog_frame)
            self.show_status_message("Time Log Manager loaded.")
        except Exception as e:
            self.show_status_message(f"Error loading Time Log Manager: {e}", error=True)

        try:
            self.employ_subconsultant_manager = EmploySubconsultantManager(self.employ_subconsultant_frame)
            self.show_status_message("Employ & Subconsultant Manager loaded.")
        except Exception as e:
            self.show_status_message(f"Error loading Employ & Subconsultant Manager: {e}", error=True)

    def create_styles(self):
        """
        Configures the ttk styles for a consistent look and feel across the application.
        This central style definition will be applied to all widgets.
        """
        self.master.option_add('*Font', ('Segoe UI', 10))  # Set default font for all widgets
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme for a modern look

        # Define color palette
        bg_color = "#ffffff"        # White background
        accent_color = "#0066cc"    # Blue accent for headings and selected items
        text_color = "#000000"      # Black text
        # row_even_color = "#f9f9f9"  # Moved to individual manager classes
        # row_odd_color = "#e5e5e5"   # Moved to individual manager classes

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

        # Treeview row tags are configured within individual manager classes (e.g., ClientManager, TimeLogManager)
        # style.tag_configure('evenrow', background=row_even_color) # REMOVED
        # style.tag_configure('oddrow', background=row_odd_color)   # REMOVED
        # style.tag_configure('total', background='#e6f3ff', font=('Segoe UI', 10, 'bold')) # REMOVED

    def show_status_message(self, message, error=False):
        """Displays a message in the main application's status bar."""
        self.status_var.set(message)
        self.status_bar.configure(foreground='red' if error else 'green')

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
