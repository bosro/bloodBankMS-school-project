import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import matplotlib
matplotlib.use('TkAgg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import ttk
import mysql.connector
from datetime import datetime, date, timedelta
import ttkthemes
from tkinter import messagebox
import re
from tkcalendar import DateEntry
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import bcrypt


class ModernCalendar(ttk.Frame):
    def __init__(self, parent, colors, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        self.colors = colors
        self.selected_date = date.today()
        self.callback = None
        self.create_calendar_ui()

    def create_calendar_ui(self):
        # Create header frame
        header_frame = ttk.Frame(self, style='Card.TFrame')
        header_frame.pack(fill='x', pady=5)

        # Navigation buttons
        nav_frame = ttk.Frame(header_frame, style='Card.TFrame')
        nav_frame.pack(fill='x')

        # Previous month button - Use tk.Label instead of ttk.Label
        self.prev_btn = tk.Label(
            nav_frame,
            text="◀",
            bg=self.colors['card_bg'],
            fg=self.colors['accent'],
            font=('Segoe UI', 10),
            cursor="hand2"
        )
        self.prev_btn.pack(side='left', padx=10)
        self.prev_btn.bind('<Button-1>', lambda e: self.change_month(-1))

        # Month and year label - Use tk.Label
        self.header_label = tk.Label(
            nav_frame,
            text=self.selected_date.strftime("%B %Y"),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        self.header_label.pack(side='left', expand=True)

        # Next month button - Use tk.Label
        self.next_btn = tk.Label(
            nav_frame,
            text="▶",
            bg=self.colors['card_bg'],
            fg=self.colors['accent'],
            font=('Segoe UI', 10),
            cursor="hand2"
        )
        self.next_btn.pack(side='right', padx=10)
        self.next_btn.bind('<Button-1>', lambda e: self.change_month(1))

        # Weekday headers
        days_frame = ttk.Frame(self, style='Card.TFrame')
        days_frame.pack(fill='x', pady=5)

        for i, day in enumerate(['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']):
            # Use tk.Label
            tk.Label(
                days_frame,
                text=day,
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 10)
            ).grid(row=0, column=i, pady=5)

        # Calendar grid
        self.calendar_frame = ttk.Frame(self, style='Card.TFrame')
        self.calendar_frame.pack(fill='both', expand=True)
        
        self.update_calendar()

    def update_calendar(self):
            # Clear existing calendar
            for widget in self.calendar_frame.winfo_children():
                widget.destroy()

            # Update header
            self.header_label.configure(text=self.selected_date.strftime("%B %Y"))

            # Get calendar information
            year = self.selected_date.year
            month = self.selected_date.month

            # Get first day of month and number of days
            first_day = date(year, month, 1)
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            num_days = last_day.day
            start_day = first_day.weekday()
            start_day = (start_day + 1) % 7  # Adjust to start on Sunday

            # Create calendar grid
            day = 1
            for week in range(6):
                for weekday in range(7):
                    if week == 0 and weekday < start_day:
                        # Empty cells before start of month
                        continue
                    elif day > num_days:
                        # Empty cells after end of month
                        break
                    
                    current_date = date(year, month, day)
                    
                    # Create date button
                    date_frame = ttk.Frame(
                        self.calendar_frame,
                        style='Card.TFrame'
                    )
                    date_frame.grid(row=week, column=weekday, padx=1, pady=1, sticky='nsew')

                    # Style based on selection/today
                    is_selected = current_date == self.selected_date
                    is_today = current_date == date.today()

                    bg_color = self.colors['accent'] if is_selected else (
                        self.colors['bg_light'] if is_today else self.colors['card_bg']
                    )
                    fg_color = self.colors['text'] if is_selected else (
                        self.colors['accent'] if is_today else self.colors['text']
                    )

                    # Use tk.Label instead of ttk.Label
                    date_label = tk.Label(
                        date_frame,
                        text=str(day),
                        bg=bg_color,
                        fg=fg_color,
                        font=('Segoe UI', 10),
                        padx=5,
                        pady=5,
                        cursor="hand2"
                    )
                    date_label.pack(fill='both', expand=True)
                    date_label.bind('<Button-1>', lambda e, d=current_date: self.select_date(d))
                    
                    day += 1

            # Configure grid weights
            for i in range(7):
                self.calendar_frame.grid_columnconfigure(i, weight=1)
            for i in range(6):
                self.calendar_frame.grid_rowconfigure(i, weight=1)

    def change_month(self, delta):
        year = self.selected_date.year
        month = self.selected_date.month + delta
        
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1

        # Keep the same day if possible
        try:
            self.selected_date = self.selected_date.replace(year=year, month=month)
        except ValueError:
            # If day is out of range, use last day of month
            if month == 12:
                self.selected_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                self.selected_date = date(year, month + 1, 1) - timedelta(days=1)

        self.update_calendar()
        
    def select_date(self, selected_date):
        self.selected_date = selected_date
        self.update_calendar()
        if self.callback:
            self.callback(selected_date)

    def get_date(self):
        return self.selected_date

    def set_date(self, new_date):
        self.selected_date = new_date
        self.update_calendar()

    def bind_selection(self, callback):
        self.callback = callback

class ModernBloodBankSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern Blood Bank Management System")
        self.root.geometry("1400x900")
        
        # Enhanced dark theme colors
        self.colors = {
            'bg_dark': '#1a1a1a',
            'bg_light': '#2d2d2d',
            'accent': '#ff4081',  # Modern pink accent
            'accent_hover': '#f50057',
            'success': '#00e676',  # Vibrant green
            'warning': '#ffab00',  # Warm amber
            'error': '#ff5252',    # Bright red
            'text': '#ffffff',
            'text_secondary': '#b3b3b3',
            'card_bg': '#333333',
            'chart_bg': '#2d2d2d',
            'grid': '#3d3d3d',
            'border': '#404040'
        }
        
        # Set root background
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Apply modern theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("equilux")
        
        # Configure custom styles
        self.configure_custom_styles()
        
        self.current_user = None
        self.init_database()
        self.setup_admin()
        
        # Create main container with modern padding
        self.main_container = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Initialize login screen
        self.show_login_screen()
        
    def show_simple_dashboard(self):
        try:
            # Clear main container
            for widget in self.main_container.winfo_children():
                widget.destroy()
                
            # Simple welcome message
            frame = ttk.Frame(self.main_container, style='Modern.TFrame')
            frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Use tk.Label for reliable display
            welcome = tk.Label(
                frame,
                text=f"Welcome, {self.current_user['username']}!",
                font=('Segoe UI', 32, 'bold'),
                bg=self.colors['bg_dark'],
                fg=self.colors['text']
            )
            welcome.pack(pady=20)
            
            # Simple buttons for main functions
            buttons_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
            buttons_frame.pack(pady=20)
            
            button_configs = [
                ("Dashboard", self.show_dashboard),
                ("New Donor", self.show_donor_registration),
                ("Manage Requests", self.show_blood_requests),
                ("View Analytics", self.show_analytics),
                ("Logout", self.logout)
            ]
            
            for text, command in button_configs:
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=('Segoe UI', 14),
                    bg=self.colors['accent'],
                    fg=self.colors['text'],
                    padx=20,
                    pady=10,
                    command=command
                )
                btn.pack(fill='x', pady=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show simple dashboard: {str(e)}")
    
    def configure_custom_styles(self):
        try:
            # Modern frame styles
            self.style.configure('Modern.TFrame', background=self.colors['bg_dark'])
            self.style.configure('Card.TFrame', background=self.colors['card_bg'])
            self.style.configure('DateEntry', background=self.colors['bg_light'])

            # Modern button styles
            self.style.configure('Modern.TButton',
                            padding=(30, 15),
                            font=('Segoe UI', 11))
            
            self.style.map('Modern.TButton',
                        background=[('active', self.colors['accent_hover']), 
                                    ('!active', self.colors['accent'])],
                        foreground=[('active', self.colors['text']), 
                                    ('!active', self.colors['text'])])
            
            # Secondary button style
            self.style.configure('Secondary.TButton',
                            padding=(30, 15),
                            font=('Segoe UI', 11))
            
            self.style.map('Secondary.TButton',
                        background=[('active', self.colors['bg_light']), 
                                    ('!active', self.colors['bg_light'])],
                        foreground=[('active', self.colors['text']), 
                                    ('!active', self.colors['text'])])
            
            # Header styles
            self.style.configure('Header.TLabel',
                            font=('Segoe UI', 32, 'bold'),
                            padding=(0, 20),
                            background=self.colors['bg_dark'],
                            foreground=self.colors['text'])
            
            self.style.configure('Subheader.TLabel',
                            font=('Segoe UI', 16),
                            padding=(0, 10),
                            background=self.colors['bg_dark'],
                            foreground=self.colors['text_secondary'])
            
            # Card header style
            self.style.configure('CardHeader.TLabel',
                            font=('Segoe UI', 18, 'bold'),
                            padding=(20, 10),
                            background=self.colors['card_bg'],
                            foreground=self.colors['text'])
            
            # Modern entry style
            self.style.configure('Modern.TEntry',
                            padding=(15, 10))
            
            # Treeview styling
            self.style.configure('Treeview',
                            background=self.colors['bg_light'],
                            foreground=self.colors['text'],
                            rowheight=25,
                            fieldbackground=self.colors['bg_light'])
            
            self.style.map('Treeview',
                        background=[('selected', self.colors['accent'])],
                        foreground=[('selected', self.colors['text'])])
            
            self.style.configure('Treeview.Heading',
                            background=self.colors['bg_dark'],
                            foreground=self.colors['text'],
                            padding=(10, 5))
            
            # Combobox styling
            self.style.configure('TCombobox',
                            background=self.colors['bg_light'],
                            foreground=self.colors['text'])
                            
        except Exception as e:
            print(f"Error configuring styles: {e}")

    def init_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="bloodbank_user",
                password="Helbert@1",
                database="blood_bank"
            )
            self.cursor = self.db.cursor(buffered=True)
            self.create_tables()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            self.root.quit()

    def create_tables(self):
            tables = [
                """CREATE TABLE IF NOT EXISTS BloodBank (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    blood_group VARCHAR(5) NOT NULL,
                    units_available INT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS Donors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    blood_group VARCHAR(5) NOT NULL,
                    contact_info VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    address TEXT,
                    donation_date DATE NOT NULL,
                    health_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS Requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hospital_name VARCHAR(100) NOT NULL,
                    blood_group VARCHAR(5) NOT NULL,
                    units_requested INT NOT NULL,
                    request_date DATE NOT NULL,
                    priority ENUM('Normal', 'Urgent', 'Emergency') DEFAULT 'Normal',
                    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS Users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'staff') NOT NULL,
                    email VARCHAR(100),
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS DonationSchedule (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    donor_id INT,
                    scheduled_date DATE NOT NULL,
                    time_slot VARCHAR(20) NOT NULL,
                    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
                    notes TEXT,
                    FOREIGN KEY (donor_id) REFERENCES Donors(id)
                )""",
                """CREATE TABLE IF NOT EXISTS Inventory_Alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    blood_group VARCHAR(5) NOT NULL,
                    alert_type ENUM('Low', 'Critical') NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            ]
            
            for table in tables:
                self.cursor.execute(table)
            
            # Initialize blood bank data if empty
            self.cursor.execute("SELECT COUNT(*) FROM BloodBank")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("""
                    INSERT INTO BloodBank (blood_group, units_available) VALUES 
                    ('A+', 0), ('A-', 0), ('B+', 0), ('B-', 0),
                    ('AB+', 0), ('AB-', 0), ('O+', 0), ('O-', 0)
                """)
            
            self.db.commit()
        
    def setup_admin(self):
        try:
            # Check if admin exists
            self.cursor.execute("SELECT * FROM Users WHERE username = 'admin'")
            if not self.cursor.fetchone():
                hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                self.cursor.execute(
                    "INSERT INTO Users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                    ('admin', hashed, 'admin', 'admin@bloodbank.com')
                )
            self.db.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup admin: {e}")

    def show_login_screen(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create centered login card with shadow effect
        login_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Modern logo/header - Use tk.Label
        logo_label = tk.Label(
            login_frame,
            text="🩸",  # Blood drop emoji
            font=('Segoe UI', 48),
            bg=self.colors['card_bg'],
            fg=self.colors['accent']
        )
        logo_label.pack(pady=(40, 0))
        
        # Use tk.Label
        title = tk.Label(
            login_frame,
            text="Blood Bank",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            pady=20
        )
        title.pack(pady=(0, 10))
        
        # Use tk.Label
        subtitle = tk.Label(
            login_frame,
            text="Management System",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        )
        subtitle.pack(pady=(0, 40))
        
        # Modern login form
        form_frame = ttk.Frame(login_frame, style='Card.TFrame')
        form_frame.pack(padx=60, pady=20)
        
        # Username field with icon
        username_frame = ttk.Frame(form_frame, style='Card.TFrame')
        username_frame.pack(fill='x', pady=(0, 20))
        
        # Use tk.Label
        username_icon = tk.Label(
            username_frame,
            text="👤",  # User icon
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        username_icon.pack(side='left', padx=(0, 10))
        
        username_entry = ttk.Entry(
            username_frame,
            font=('Segoe UI', 12),
            width=30,
            style='Modern.TEntry'
        )
        username_entry.pack(side='left', fill='x', expand=True)
        username_entry.insert(0, "Username")
        username_entry.bind('<FocusIn>', lambda e: self.on_entry_click(username_entry, "Username"))
        username_entry.bind('<FocusOut>', lambda e: self.on_focus_out(username_entry, "Username"))
        
        # Password field with icon
        password_frame = ttk.Frame(form_frame, style='Card.TFrame')
        password_frame.pack(fill='x', pady=(0, 30))
        
        # Use tk.Label
        password_icon = tk.Label(
            password_frame,
            text="🔒",  # Lock icon
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        password_icon.pack(side='left', padx=(0, 10))
        
        password_entry = ttk.Entry(
            password_frame,
            font=('Segoe UI', 12),
            width=30,
            show="•",
            style='Modern.TEntry'
        )
        password_entry.pack(side='left', fill='x', expand=True)
        
        # Show/Hide password toggle - Use tk.Label
        self.password_visible = False
        toggle_btn = tk.Label(
            password_frame,
            text="👁️",  # Eye icon
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            cursor="hand2"
        )
        toggle_btn.pack(side='right', padx=(10, 0))
        toggle_btn.bind('<Button-1>', lambda e: self.toggle_password_visibility(password_entry, toggle_btn))
        
        # Error message label (hidden by default) - Use tk.Label
        self.error_label = tk.Label(
            form_frame,
            text="",
            fg=self.colors['error'],
            bg=self.colors['card_bg'],
            font=('Segoe UI', 10)
        )
        self.error_label.pack(pady=(0, 10))
        
        # Modern login button with hover effect
        login_button = ttk.Button(
            form_frame,
            text="Login",
            style='Modern.TButton',
            command=lambda: self.validate_login(
                username_entry.get(),
                password_entry.get()
            )
        )
        login_button.pack(fill='x', pady=(0, 20))
        
        # Divider
        # divider_frame = ttk.Frame(form_frame, height=1, style='Card.TFrame')
        # divider_frame.pack(fill='x', pady=20)
        # divider_frame.configure(background=self.colors['border'])
        divider_frame = tk.Frame(form_frame, height=1, bg=self.colors['border'])
        divider_frame.pack(fill='x', pady=20)   
        # Forgot password link - Use tk.Label
        forgot_password = tk.Label(
            form_frame,
            text="Forgot Password?",
            fg=self.colors['accent'],
            bg=self.colors['card_bg'],
            font=('Segoe UI', 10, 'underline'),
            cursor="hand2"
        )
        forgot_password.pack(pady=10)
        forgot_password.bind('<Button-1>', lambda e: self.show_password_reset())
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.validate_login(
            username_entry.get(),
            password_entry.get()
        ))

    def on_entry_click(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if placeholder == "Password":
                entry.configure(show="•")

    def on_focus_out(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            if placeholder == "Password":
                entry.configure(show="")

    def toggle_password_visibility(self, password_entry, toggle_btn):
        self.password_visible = not self.password_visible
        if self.password_visible:
            password_entry.configure(show="")
            toggle_btn.configure(text="🔒")  # Closed eye icon
        else:
            password_entry.configure(show="•")
            toggle_btn.configure(text="👁️")  # Open eye icon

    def validate_login(self, username, password):
        try:
            if username == "Username" or not username.strip():
                self.show_error("Please enter your username")
                return
                
            if not password:
                self.show_error("Please enter your password")
                return
            
            self.cursor.execute(
                "SELECT password, role FROM Users WHERE username = %s",
                (username,)
            )
            result = self.cursor.fetchone()
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                self.current_user = {'username': username, 'role': result[1]}
                
                # Try to update last_login, but continue if it fails
                try:
                    self.cursor.execute(
                        "UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                        (username,)
                    )
                    self.db.commit()
                except mysql.connector.Error:
                    # Silently continue if the last_login column doesn't exist
                    self.db.rollback()
                    
                self.show_dashboard()
            else:
                self.show_error("Invalid username or password")
        except Exception as e:
            self.show_error(f"Login failed: {str(e)}")

    def show_error(self, message):
        self.error_label.configure(text=message)
        # Clear error after 3 seconds
        self.root.after(3000, lambda: self.error_label.configure(text=""))
        

    def show_dashboard(self):
        try:
            if not self.current_user:
                self.show_login_screen()
                return

            print("Starting dashboard setup")  # Debug print
            
            # Clear all widgets from main container
            for widget in self.main_container.winfo_children():
                widget.destroy()
            
            print("Creating dashboard layout")  # Debug print
            
            # Create sidebar
            sidebar = ttk.Frame(self.main_container, style='Card.TFrame')
            sidebar.pack(side='left', fill='y', padx=(0, 20))
            
            # User profile section
            print("Creating user profile")  # Debug print
            self.create_user_profile(sidebar)
            
            # Navigation menu
            print("Creating navigation menu")  # Debug print
            self.create_navigation_menu(sidebar)
            
            # Main content area
            print("Creating main content area")  # Debug print
            content_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
            content_frame.pack(side='left', fill='both', expand=True)
            
            # Force update of UI
            self.root.update_idletasks()
            
            # Dashboard header
            print("Creating dashboard header")  # Debug print
            self.create_dashboard_header(content_frame)
            
            # Quick stats
            print("Creating quick stats")  # Debug print
            self.create_quick_stats(content_frame)
            
            # Blood inventory
            print("Showing blood inventory")  # Debug print
            self.show_blood_inventory(content_frame)
            
            print("Dashboard setup complete")  # Debug print
            
        except Exception as e:
            print(f"Error in dashboard: {e}")  # Debug print
            messagebox.showerror("Dashboard Error", f"Error setting up dashboard: {str(e)}")
            self.show_simple_dashboard()
        
    def setup_dashboard_layout(self):
        # Create sidebar
        sidebar = ttk.Frame(self.main_container, style='Card.TFrame')
        sidebar.pack(side='left', fill='y', padx=(0, 20))
        
        # User profile section
        self.create_user_profile(sidebar)
        
        # Navigation menu
        self.create_navigation_menu(sidebar)
        
        # Main content area
        content_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        content_frame.pack(side='left', fill='both', expand=True)
        
        # Dashboard header
        self.create_dashboard_header(content_frame)
        
        # Quick stats
        self.create_quick_stats(content_frame)
        
        # Blood inventory
        self.show_blood_inventory(content_frame)

    def create_user_profile(self, parent):
            profile_frame = ttk.Frame(parent, style='Card.TFrame')
            profile_frame.pack(fill='x', pady=(0, 20), padx=20)
            
            # User avatar - Use tk.Label
            tk.Label(
                profile_frame,
                text="👤",  # User icon
                font=('Segoe UI', 32),
                bg=self.colors['card_bg'],
                fg=self.colors['text']
            ).pack(pady=(20, 10))
            
            # Username - Use tk.Label
            tk.Label(
                profile_frame,
                text=self.current_user['username'],
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(pady=(0, 5))
            
            # Role badge
            role_frame = ttk.Frame(profile_frame, style='Card.TFrame')
            role_frame.pack(pady=(0, 20))
            
            # Use tk.Label
            role_label = tk.Label(
                role_frame,
                text=f"🔰 {self.current_user['role'].title()}",
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Segoe UI', 10),
                padx=10,
                pady=5
            )
            role_label.pack()

    def create_navigation_menu(self, parent):
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard, "Home dashboard"),
            ("➕ New Donor", self.show_donor_registration, "Register new donors"),
            ("👥 Donors", self.show_donors_list, "View and manage donors"),  # New Donors tab!
            ("📋 Requests", self.show_blood_requests, "Manage blood requests"),
            ("📈 Analytics", self.show_analytics, "View analytics"),
            ("📄 Reports", self.generate_report, "Generate reports"),
            ("📅 History", self.show_donation_history, "View donation history"),
            ("⚙️ Settings", self.show_settings, "System settings"),
            ("🚪 Logout", self.logout, "Logout from system")
        ]
        
        for text, command, tooltip in nav_buttons:
            btn_frame = ttk.Frame(parent, style='Card.TFrame')
            btn_frame.pack(fill='x', padx=20, pady=2)
            
            btn = ttk.Button(
                btn_frame,
                text=text,
                style='Modern.TButton',
                command=command
            )
            btn.pack(fill='x')
            
            # Create tooltip
            self.create_tooltip(btn, tooltip)

    def create_dashboard_header(self, parent):
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Welcome message - Use tk.Label
        tk.Label(
            header_frame,
            text=f"Welcome back, {self.current_user['username']}!",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left')
        
        # Date and time
        time_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        time_frame.pack(side='right')
        
        current_time = datetime.now().strftime("%d %B %Y, %H:%M")
        
        # Use tk.Label
        tk.Label(
            time_frame,
            text=f"🕒 {current_time}",
            font=('Segoe UI', 16),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()

    def create_quick_stats(self, parent):
        stats_frame = ttk.Frame(parent, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Enhanced stats query to get more dynamic data
        self.cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM Donors WHERE DATE(donation_date) = CURDATE()) as today_donations,
                (SELECT COUNT(*) FROM Requests WHERE DATE(request_date) = CURDATE()) as today_requests,
                (SELECT COUNT(*) FROM BloodBank WHERE units_available < 10) as low_inventory,
                (SELECT COUNT(*) FROM Requests WHERE status = 'Pending') as pending_requests,
                (SELECT SUM(units_available) FROM BloodBank) as total_blood_units,
                (SELECT COUNT(*) FROM Donors) as total_donors
        """)
        stats = self.cursor.fetchone()
        
        # Create stat cards with dynamic data
        stat_cards = [
            ("Today's Donations", stats[0], "💉", self.colors['success']),
            ("Today's Requests", stats[1], "📝", self.colors['warning']),
            ("Low Inventory Alert", stats[2], "⚠️", self.colors['error']),
            ("Pending Requests", stats[3], "⏳", self.colors['accent'])
        ]
        
        for i, (label, value, icon, color) in enumerate(stat_cards):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            
            # Icon - Use tk.Label
            tk.Label(
                card,
                text=icon,
                font=('Segoe UI', 24),
                fg=color,
                bg=self.colors['card_bg']
            ).pack(pady=(20, 5))
            
            # Value - Use tk.Label
            tk.Label(
                card,
                text=str(value),
                font=('Segoe UI', 36, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['card_bg']
            ).pack()
            
            # Label - Use tk.Label
            tk.Label(
                card,
                text=label,
                font=('Segoe UI', 12),
                fg=self.colors['text_secondary'],
                bg=self.colors['card_bg']
            ).pack(pady=(5, 20))
        
        # Configure grid weights
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Use tk.Label instead of ttk.Label
            label = tk.Label(
                tooltip,
                text=text,
                bg=self.colors['bg_dark'],
                fg=self.colors['text'],
                font=('Segoe UI', 9),
                padx=10,
                pady=5
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            
        widget.bind('<Enter>', show_tooltip)

    def show_blood_inventory(self, parent):
        inventory_frame = ttk.Frame(parent, style='Modern.TFrame')
        inventory_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(inventory_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Blood Inventory",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left')
        
        # Refresh button
        ttk.Button(
            header_frame,
            text="🔄 Refresh",
            style='Secondary.TButton',
            command=lambda: self.refresh_inventory()
        ).pack(side='right')
        
        # Create a separate frame for the blood type cards grid
        blood_types_frame = ttk.Frame(inventory_frame, style='Modern.TFrame')
        blood_types_frame.pack(fill='both', expand=True)
        
        # Grid layout for blood type cards
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i, blood_type in enumerate(blood_types):
            self.create_blood_type_card(blood_types_frame, blood_type, i)
        
        # Configure grid weights
        for i in range(4):
            blood_types_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            blood_types_frame.grid_rowconfigure(i, weight=1)
            
            
    def show_donation_history(self):
        # Create a top-level window for donation history
        history_window = tk.Toplevel(self.root)
        history_window.title("Donation History")
        history_window.geometry("1000x700")
        history_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(history_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame with back button
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Add back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=history_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Add a header
        tk.Label(
            header_frame,
            text="Donation History",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Add date filter
        filter_frame = ttk.Frame(main_frame, style='Card.TFrame')
        filter_frame.pack(fill='x', pady=(0, 20))
        
        # Date range filter
        tk.Label(
            filter_frame,
            text="Date Range:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=10)
        
        # Date range options
        range_options = ["All Time", "Last 30 Days", "Last 3 Months", "Last Year"]
        date_range_var = tk.StringVar(value="All Time")
        
        range_combo = ttk.Combobox(
            filter_frame,
            textvariable=date_range_var,
            values=range_options,
            state='readonly',
            font=('Segoe UI', 11)
        )
        range_combo.pack(side='left', padx=10)
        
        # Blood group filter
        tk.Label(
            filter_frame,
            text="Blood Group:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=10)
        
        # Blood group options
        blood_options = ["All"] + ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group_var = tk.StringVar(value="All")
        
        blood_combo = ttk.Combobox(
            filter_frame,
            textvariable=blood_group_var,
            values=blood_options,
            state='readonly',
            font=('Segoe UI', 11)
        )
        blood_combo.pack(side='left', padx=10)
        
        # Apply filter button
        ttk.Button(
            filter_frame,
            text="Apply Filter",
            style='Modern.TButton',
            command=lambda: self.refresh_donation_history(tree, date_range_var.get(), blood_group_var.get())
        ).pack(side='left', padx=10)
        
        # Export button
        ttk.Button(
            filter_frame,
            text="Export to CSV",
            style='Modern.TButton',
            command=lambda: self.export_donation_history(tree, date_range_var.get(), blood_group_var.get())
        ).pack(side='right', padx=10)
        
        # Stats frame
        stats_frame = ttk.Frame(main_frame, style='Card.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Create a treeview to display donation history
        columns = ('id', 'donor', 'blood_group', 'date', 'units', 'status', 'time_slot', 'notes')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Define column headings
        tree.heading('id', text='ID')
        tree.heading('donor', text='Donor Name')
        tree.heading('blood_group', text='Blood Group')
        tree.heading('date', text='Donation Date')
        tree.heading('units', text='Units')
        tree.heading('status', text='Status')
        tree.heading('time_slot', text='Time Slot')
        tree.heading('notes', text='Notes')
        
        # Set column widths
        tree.column('id', width=50)
        tree.column('donor', width=150)
        tree.column('blood_group', width=80)
        tree.column('date', width=100)
        tree.column('units', width=50)
        tree.column('status', width=80)
        tree.column('time_slot', width=120)
        tree.column('notes', width=200)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Initial load of data
        self.refresh_donation_history(tree, "All Time", "All")
        
        # Bind double-click event to show donation details
        tree.bind('<Double-1>', lambda e: self.show_donation_details(tree))
        
        
    def refresh_donation_history(self, tree, date_range, blood_group):
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Prepare date filter
        today = date.today()
        date_clause = ""
        date_params = []
        
        if date_range == "Last 30 Days":
            date_clause = "AND d.donation_date >= %s"
            date_params.append(today - timedelta(days=30))
        elif date_range == "Last 3 Months":
            date_clause = "AND d.donation_date >= %s"
            date_params.append(today - timedelta(days=90))
        elif date_range == "Last Year":
            date_clause = "AND d.donation_date >= %s"
            date_params.append(today - timedelta(days=365))
        
        # Prepare blood group filter
        blood_clause = ""
        if blood_group != "All":
            blood_clause = "AND d.blood_group = %s"
            date_params.append(blood_group)
        
        # Fetch donation history from database
        try:
            query = f"""
                SELECT ds.id, d.name, d.blood_group, d.donation_date, 
                    ds.status, ds.time_slot, ds.notes
                FROM Donors d
                JOIN DonationSchedule ds ON d.id = ds.donor_id
                WHERE ds.status = 'Completed' {date_clause} {blood_clause}
                ORDER BY d.donation_date DESC
            """
            
            self.cursor.execute(query, date_params)
            
            for row in self.cursor.fetchall():
                # Format date
                date_str = row[3].strftime("%Y-%m-%d")
                # Default units to 1
                units = 1
                time_slot = row[5] if row[5] else "N/A"
                notes = row[6] if row[6] else ""
                
                tree.insert('', 'end', values=(row[0], row[1], row[2], date_str, units, row[4], time_slot, notes))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load donation history: {str(e)}")
        
    def show_donation_details(self, tree):
        try:
            # Get selected item
            selection = tree.selection()[0]
            values = tree.item(selection, 'values')
            
            if not values:
                return
            
            donation_id = values[0]
            
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Donation Details - ID: {donation_id}")
            details_window.geometry("600x500")
            details_window.configure(bg=self.colors['bg_dark'])
            
            # Main frame
            main_frame = ttk.Frame(details_window, style='Modern.TFrame')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Header
            tk.Label(
                main_frame,
                text=f"Donation Details",
                font=('Segoe UI', 24, 'bold'),
                bg=self.colors['bg_dark'],
                fg=self.colors['text'],
                pady=10
            ).pack(fill='x')
            
            # Details card
            details_frame = ttk.Frame(main_frame, style='Card.TFrame')
            details_frame.pack(fill='x', pady=20)
            
            # Query additional details
            self.cursor.execute("""
                SELECT d.id, d.name, d.blood_group, d.age, d.contact_info, d.email,
                    d.address, d.donation_date, ds.time_slot, ds.status, ds.notes
                FROM Donors d
                JOIN DonationSchedule ds ON d.id = ds.donor_id
                WHERE ds.id = %s
            """, (donation_id,))
            
            row = self.cursor.fetchone()
            if row:
                # Display all details
                details = [
                    ("Donor ID", row[0]),
                    ("Donor Name", row[1]),
                    ("Blood Group", row[2]),
                    ("Age", row[3]),
                    ("Contact", row[4]),
                    ("Email", row[5] if row[5] else "N/A"),
                    ("Address", row[6] if row[6] else "N/A"),
                    ("Donation Date", row[7].strftime("%Y-%m-%d")),
                    ("Time Slot", row[8] if row[8] else "N/A"),
                    ("Status", row[9]),
                    ("Notes", row[10] if row[10] else "N/A")
                ]
                
                for label, value in details:
                    detail_frame = ttk.Frame(details_frame, style='Card.TFrame')
                    detail_frame.pack(fill='x', padx=20, pady=5)
                    
                    # Label
                    tk.Label(
                        detail_frame,
                        text=label + ":",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'],
                        width=15,
                        anchor='w'
                    ).pack(side='left', padx=(0, 10))
                    
                    # Value
                    tk.Label(
                        detail_frame,
                        text=str(value),
                        font=('Segoe UI', 14),
                        bg=self.colors['card_bg'],
                        fg=self.colors['text_secondary'],
                        wraplength=350,
                        anchor='w'
                    ).pack(side='left', fill='x', expand=True)
            
            # Close button
            ttk.Button(
                main_frame,
                text="Close",
                style='Modern.TButton',
                command=details_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show donation details: {str(e)}")
    
    def export_donation_history(self, tree, date_range, blood_group):
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"donation_history_{timestamp}.csv")
            
            with open(filename, 'w', newline='') as file:
                file.write("ID,Donor Name,Blood Group,Donation Date,Units,Status,Time Slot,Notes\n")
                
                for item_id in tree.get_children():
                    values = tree.item(item_id, 'values')
                    # Escape quotes in values
                    escaped_values = [f'"{str(v).replace(chr(34), chr(34)+chr(34))}"' for v in values]
                    file.write(','.join(escaped_values) + '\n')
            
            # Open the file
            os.startfile(filename) if os.name == 'nt' else os.system(f'xdg-open "{filename}"')
            
            messagebox.showinfo("Export Successful", f"Donation history exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export donation history: {str(e)}")
        
    def show_request_form(self, blood_type=None):
        request_window = tk.Toplevel(self.root)
        request_window.title("Blood Request Form")
        request_window.geometry("600x700")
        request_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(request_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=request_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Add header
        tk.Label(
            header_frame,
            text="New Blood Request",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form container
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='x', pady=10)
        
        # Hospital name
        hospital_frame = ttk.Frame(form_frame, style='Card.TFrame')
        hospital_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            hospital_frame,
            text="Hospital Name*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        hospital_var = tk.StringVar()
        hospital_entry = ttk.Entry(
            hospital_frame,
            textvariable=hospital_var,
            font=('Segoe UI', 12),
            style='Modern.TEntry'
        )
        hospital_entry.pack(fill='x', pady=(5, 0))
        
        # Blood type
        blood_type_frame = ttk.Frame(form_frame, style='Card.TFrame')
        blood_type_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            blood_type_frame,
            text="Blood Type*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        blood_type_var = tk.StringVar(value=blood_type if blood_type else '')
        blood_type_combo = ttk.Combobox(
            blood_type_frame,
            textvariable=blood_type_var,
            values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            state='readonly' if blood_type else 'normal',
            font=('Segoe UI', 12)
        )
        blood_type_combo.pack(fill='x', pady=(5, 0))
        
        # Units
        units_frame = ttk.Frame(form_frame, style='Card.TFrame')
        units_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            units_frame,
            text="Units Required*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        units_var = tk.StringVar()
        units_entry = ttk.Entry(
            units_frame,
            textvariable=units_var,
            font=('Segoe UI', 12),
            style='Modern.TEntry'
        )
        units_entry.pack(fill='x', pady=(5, 0))
        
        # Priority
        priority_frame = ttk.Frame(form_frame, style='Card.TFrame')
        priority_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            priority_frame,
            text="Priority*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        priority_var = tk.StringVar(value='Normal')
        for priority in ['Normal', 'Urgent', 'Emergency']:
            ttk.Radiobutton(
                priority_frame,
                text=priority,
                variable=priority_var,
                value=priority,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Notes
        notes_frame = ttk.Frame(form_frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            notes_frame,
            text="Additional Notes",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        notes_text = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        notes_text.pack(fill='x', pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=request_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Submit Request",
            style='Modern.TButton',
            command=lambda: self.save_blood_request(
                hospital_var.get(),
                blood_type_var.get(),
                units_var.get(),
                priority_var.get(),
                notes_text.get("1.0", tk.END).strip(),
                request_window
            )
        ).pack(side='right', padx=5)

    def save_blood_request(self, hospital, blood_type, units, priority, notes, window):
        """Save blood request to database"""
        try:
            # Validate inputs
            if not all([hospital, blood_type, units]):
                raise ValueError("Please fill in all required fields")
            
            try:
                units = int(units)
                if units <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Please enter a valid number of units")
            
            # Insert request into database
            self.cursor.execute("""
                INSERT INTO Requests (
                    hospital_name, blood_group, units_requested,
                    request_date, priority, notes
                ) VALUES (%s, %s, %s, CURDATE(), %s, %s)
            """, (hospital, blood_type, units, priority, notes))
            
            self.db.commit()
            messagebox.showinfo("Success", "Blood request submitted successfully!")
            window.destroy()
            
            # Refresh blood requests view if currently displayed
            if hasattr(self, 'request_tree'):
                self.refresh_requests()
        
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))
              
    def create_blood_type_card(self, parent, blood_type, index):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.grid(row=index//4, column=index%4, padx=10, pady=10, sticky='nsew')
        
        # Get inventory data - Using a fresh query for each card
        self.cursor.execute(
            "SELECT units_available FROM BloodBank WHERE blood_group = %s",
            (blood_type,)
        )
        units = self.cursor.fetchone()[0]
        
        # Blood type label - Use tk.Label
        tk.Label(
            card,
            text=blood_type,
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(pady=(20, 10))
        
        # Units display - Use tk.Label
        tk.Label(
            card,
            text=str(units),
            font=('Segoe UI', 36, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack()
        
        # Use tk.Label
        tk.Label(
            card,
            text="units available",
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        ).pack(pady=(0, 20))
        
        # Status indicator
        status_frame = ttk.Frame(card, style='Card.TFrame')
        status_frame.pack(pady=(0, 20))
        
        status_color = self.get_status_color(units)
        status_text = self.get_status_text(units)
        
        # Use tk.Label
        tk.Label(
            status_frame,
            text=status_text,
            bg=status_color,
            fg=self.colors['text'],
            font=('Segoe UI', 10),
            padx=10,
            pady=5
        ).pack()
        
        # Action buttons
        button_frame = ttk.Frame(card, style='Card.TFrame')
        button_frame.pack(pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text="Donate",
            style='Modern.TButton',
            command=lambda bt=blood_type: self.show_donation_form(bt)
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Request",
            style='Modern.TButton',
            command=lambda bt=blood_type: self.show_request_form(bt)
        ).pack(side='left', padx=5)

    def get_status_color(self, units):
        if units < 5:
            return self.colors['error']
        elif units < 10:
            return self.colors['warning']
        else:
            return self.colors['success']

    def get_status_text(self, units):
        if units < 5:
            return "⚠️ Critical"
        elif units < 10:
            return "⚠️ Low"
        else:
            return "✅ Sufficient"

    def refresh_inventory(self):
            # Clear main container
            for widget in self.main_container.winfo_children():
                widget.destroy()
            
            # Create frame for the blood inventory
            content_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
            content_frame.pack(fill='both', expand=True)
            
            # Add back button at the top
            back_frame = ttk.Frame(content_frame, style='Modern.TFrame')
            back_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Button(
                back_frame,
                text="← Back to Dashboard",
                style='Secondary.TButton',
                command=self.show_dashboard
            ).pack(side='left', pady=5, padx=5)
            
            # Show the blood inventory
            self.show_blood_inventory(content_frame)
        
    def show_donor_registration(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Donor Registration")
        registration_window.geometry("1000x800")
        registration_window.configure(bg=self.colors['bg_dark'])
        
        # Main container
        main_frame = ttk.Frame(registration_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=registration_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label instead of ttk.Label
        tk.Label(
            header_frame,
            text="🩸 New Donor Registration",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Personal Information Tab
        personal_frame = self.create_personal_info_tab(notebook)
        notebook.add(personal_frame, text='👤 Personal Information')
        
        # Health Screening Tab
        health_frame = self.create_health_screening_tab(notebook)
        notebook.add(health_frame, text='🏥 Health Screening')
        
        # Scheduling Tab
        schedule_frame = self.create_scheduling_tab(notebook)
        notebook.add(schedule_frame, text='📅 Scheduling')
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=registration_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Register Donor",
            style='Modern.TButton',
            command=lambda: self.save_donor_registration(
                registration_window,
                notebook
            )
        ).pack(side='right', padx=5)

    def show_donors_list(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
                
        main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Header with stats
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back to Dashboard",
            style='Secondary.TButton',
            command=self.show_dashboard
        ).pack(side='left', padx=10, pady=5)
        
        # Title - Use tk.Label
        tk.Label(
            header_frame,
            text="Donors Registry",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # New donor button
        ttk.Button(
            header_frame,
            text="➕ New Donor",
            style='Modern.TButton',
            command=self.show_donor_registration
        ).pack(side='right')
        
        # Quick stats
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT blood_group) as blood_types,
                (SELECT COUNT(*) FROM Donors WHERE DATE(donation_date) = CURDATE()) as today,
                (SELECT COUNT(*) FROM Donors WHERE donation_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) as last_30_days
        """)
        stats = self.cursor.fetchone()
        
        stats_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stat_items = [
            ("Total Donors", stats[0], "👥"),
            ("Blood Types", stats[1], "🩸"),
            ("Today's Donors", stats[2], "📅", self.colors['success']),
            ("Last 30 Days", stats[3], "📊", self.colors['accent'])
        ]
        
        for i, (label, value, icon, *colors) in enumerate(stat_items):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            color = colors[0] if colors else self.colors['text']
            
            # Use tk.Label
            tk.Label(
                card,
                text=f"{icon} {value}",
                font=('Segoe UI', 20, 'bold'),
                fg=color,
                bg=self.colors['card_bg']
            ).pack(pady=(10, 5))
            
            # Use tk.Label
            tk.Label(
                card,
                text=label,
                font=('Segoe UI', 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['card_bg']
            ).pack(pady=(0, 10))
        
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Filters and search
        filter_frame = self.create_donor_filters(main_frame)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        # Donors list - create in a separate function
        self.create_donors_list(main_frame)

    def create_donor_filters(self, parent):
        filter_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Blood group filter
        blood_frame = ttk.Frame(filter_frame, style='Card.TFrame')
        blood_frame.pack(side='left', padx=20, pady=10)
        
        self.donor_blood_var = tk.StringVar(value='All')
        
        # Use tk.Label
        tk.Label(
            blood_frame,
            text="Blood Group:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=(0, 10))
        
        blood_groups = ['All', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_combo = ttk.Combobox(
            blood_frame,
            textvariable=self.donor_blood_var,
            values=blood_groups,
            state='readonly',
            style='Modern.TCombobox'
        )
        blood_combo.pack(side='left')
        blood_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_donors_list())
        
        # Date filter
        date_frame = ttk.Frame(filter_frame, style='Card.TFrame')
        date_frame.pack(side='left', padx=20, pady=10)
        
        self.donor_date_var = tk.StringVar(value='All Time')
        
        # Use tk.Label
        tk.Label(
            date_frame,
            text="Last Donation:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=(0, 10))
        
        date_options = ['All Time', 'Today', 'Last 7 Days', 'Last 30 Days', 'Last Year']
        date_combo = ttk.Combobox(
            date_frame,
            textvariable=self.donor_date_var,
            values=date_options,
            state='readonly',
            style='Modern.TCombobox'
        )
        date_combo.pack(side='left')
        date_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_donors_list())
        
        # Search
        search_frame = ttk.Frame(filter_frame, style='Card.TFrame')
        search_frame.pack(side='right', padx=20, pady=10)
        
        self.donor_search_var = tk.StringVar()
        self.donor_search_var.trace('w', lambda *args: self.refresh_donors_list())
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.donor_search_var,
            font=('Segoe UI', 11),
            width=30,
            style='Modern.TEntry'
        )
        search_entry.pack(side='right')
        
        # Use tk.Label
        tk.Label(
            search_frame,
            text="🔍",
            font=('Segoe UI', 12),
            bg=self.colors['card_bg']
        ).pack(side='right', padx=(0, 5))
        
        return filter_frame

    def create_donors_list(self, parent):
        # Create a frame to contain the treeview and scrollbar
        list_container = ttk.Frame(parent, style='Modern.TFrame')
        list_container.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = (
            'id', 'name', 'age', 'blood_group', 'contact', 
            'email', 'donation_date', 'health_status'
        )
        
        self.donors_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show='headings',
            style='Treeview'
        )
        
        # Configure columns
        column_configs = {
            'id': ('ID', 50),
            'name': ('Name', 200),
            'age': ('Age', 50),
            'blood_group': ('Blood Type', 80),
            'contact': ('Contact', 150),
            'email': ('Email', 200),
            'donation_date': ('Last Donation', 120),
            'health_status': ('Health Status', 200)
        }
        
        for col, (heading, width) in column_configs.items():
            self.donors_tree.heading(col, text=heading)
            self.donors_tree.column(col, width=width)
        
        # Add scrollbar
        y_scrollbar = ttk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.donors_tree.yview
        )
        self.donors_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # Add horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(
            list_container,
            orient="horizontal",
            command=self.donors_tree.xview
        )
        self.donors_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Pack elements
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar.pack(side='bottom', fill='x')
        self.donors_tree.pack(side='left', fill='both', expand=True)
        
        # Bind double-click event
        self.donors_tree.bind('<Double-1>', self.show_donor_details)
        
        # Bottom action buttons
        action_frame = ttk.Frame(parent, style='Modern.TFrame')
        action_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            style='Secondary.TButton',
            command=self.delete_selected_donor
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="📊 Export List",
            style='Modern.TButton',
            command=self.export_donors_list
        ).pack(side='right', padx=5)
        
        # Initial load
        self.refresh_donors_list()

    def refresh_donors_list(self):
        # Clear existing data
        for item in self.donors_tree.get_children():
            self.donors_tree.delete(item)
        
        # Get filter values
        blood_filter = self.donor_blood_var.get()
        date_filter = self.donor_date_var.get()
        search_term = self.donor_search_var.get().strip()
        
        # Build query
        query = """
            SELECT id, name, age, blood_group, contact_info, 
                email, donation_date, health_status
            FROM Donors
            WHERE 1=1
        """
        
        params = []
        
        # Apply blood group filter
        if blood_filter != 'All':
            query += " AND blood_group = %s"
            params.append(blood_filter)
        
        # Apply date filter
        if date_filter == 'Today':
            query += " AND DATE(donation_date) = CURDATE()"
        elif date_filter == 'Last 7 Days':
            query += " AND donation_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif date_filter == 'Last 30 Days':
            query += " AND donation_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        elif date_filter == 'Last Year':
            query += " AND donation_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
        
        # Apply search filter
        if search_term:
            query += """ AND (
                name LIKE %s OR
                contact_info LIKE %s OR
                email LIKE %s OR
                health_status LIKE %s
            )"""
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        # Add ordering
        query += " ORDER BY donation_date DESC"
        
        # Execute query
        self.cursor.execute(query, params)
        
        # Populate treeview
        for donor in self.cursor.fetchall():
            # Format date for display
            donor_values = list(donor)
            if donor[6]:  # donation_date
                donor_values[6] = donor[6].strftime("%Y-%m-%d")
            else:
                donor_values[6] = "Never"
                
            self.donors_tree.insert('', 'end', values=donor_values)

    def show_donor_details(self, event):
        try:
            # Get selected item
            selection = self.donors_tree.selection()[0]
            values = self.donors_tree.item(selection, 'values')
            
            if not values:
                return
            
            donor_id = values[0]
            
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Donor Details - {values[1]}")
            details_window.geometry("600x700")
            details_window.configure(bg=self.colors['bg_dark'])
            
            # Create a scrollable frame for the content
            main_canvas = tk.Canvas(details_window, bg=self.colors['bg_dark'], highlightthickness=0)
            main_scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=main_canvas.yview)
            
            # Create a frame inside the canvas for the content
            main_frame = ttk.Frame(main_canvas, style='Modern.TFrame')
            
            # Configure the canvas
            main_canvas.configure(yscrollcommand=main_scrollbar.set)
            main_canvas.pack(side='left', fill='both', expand=True, padx=20, pady=20)
            main_scrollbar.pack(side='right', fill='y')
            
            # Add the main frame to the canvas
            main_canvas_frame = main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
            
            # Make sure the frame takes the full width of the canvas
            def configure_frame(event):
                main_canvas.itemconfig(main_canvas_frame, width=event.width)
            main_canvas.bind('<Configure>', configure_frame)
            
            # Make sure the canvas can scroll the entire frame
            def configure_scroll_region(event):
                main_canvas.configure(scrollregion=main_canvas.bbox('all'))
            main_frame.bind('<Configure>', configure_scroll_region)
            
            # Header
            tk.Label(
                main_frame,
                text=f"Donor Details",
                font=('Segoe UI', 24, 'bold'),
                bg=self.colors['bg_dark'],
                fg=self.colors['text'],
                pady=10
            ).pack(fill='x')
            
            # Get donor's full details and donation history
            self.cursor.execute("""
                SELECT d.*, 
                    (SELECT COUNT(*) FROM DonationSchedule WHERE donor_id = d.id) as donation_count
                FROM Donors d
                WHERE d.id = %s
            """, (donor_id,))
            
            donor = self.cursor.fetchone()
            
            if not donor:
                tk.Label(
                    main_frame,
                    text="Donor not found",
                    fg=self.colors['error'],
                    bg=self.colors['bg_dark']
                ).pack()
                return
            
            # Personal Info Card
            self.create_donor_personal_card(main_frame, donor)
            
            # Donation History Card
            self.create_donor_history_card(main_frame, donor_id)
            
            # Action buttons
            button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
            button_frame.pack(fill='x', pady=20)
            
            ttk.Button(
                button_frame,
                text="✏️ Edit Donor",
                style='Modern.TButton',
                command=lambda: self.show_edit_donor_form(donor_id, details_window)
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="🩸 Record Donation",
                style='Modern.TButton',
                command=lambda: self.show_donation_form(donor[3], donor_id, details_window)
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="🖨️ Print Details",
                style='Secondary.TButton',
                command=lambda: self.print_donor_details(donor_id)
            ).pack(side='right', padx=5)
            
            ttk.Button(
                button_frame,
                text="Close",
                style='Secondary.TButton',
                command=details_window.destroy
            ).pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show donor details: {str(e)}")

    def create_donor_personal_card(self, parent, donor):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=10)
        
        # Card Header
        tk.Label(
            card,
            text="Personal Information",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            pady=10
        ).pack(fill='x', padx=20)
        
        # Donor details
        details = [
            ("ID", donor[0]),
            ("Name", donor[1]),
            ("Age", donor[2]),
            ("Blood Group", donor[3]),
            ("Contact", donor[4]),
            ("Email", donor[5] if donor[5] else "N/A"),
            ("Address", donor[6] if donor[6] else "N/A"),
            ("Last Donation", donor[7].strftime("%Y-%m-%d") if donor[7] else "Never"),
            ("Health Status", donor[8] if donor[8] else "N/A"),
            ("Registration Date", donor[9].strftime("%Y-%m-%d %H:%M") if donor[9] else "N/A"),
            ("Total Donations", donor[10])
        ]
        
        for label, value in details:
            detail_frame = ttk.Frame(card, style='Card.TFrame')
            detail_frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(
                detail_frame,
                text=f"{label}:",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                width=15,
                anchor='w'
            ).pack(side='left', padx=(0, 10))
            
            tk.Label(
                detail_frame,
                text=str(value),
                font=('Segoe UI', 14),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                anchor='w'
            ).pack(side='left', fill='x', expand=True)

    def create_donor_history_card(self, parent, donor_id):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=10)
        
        # Card Header
        tk.Label(
            card,
            text="Donation History",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            pady=10
        ).pack(fill='x', padx=20)
        
        # Fetch donation history
        self.cursor.execute("""
            SELECT scheduled_date, time_slot, status, notes
            FROM DonationSchedule
            WHERE donor_id = %s
            ORDER BY scheduled_date DESC
        """, (donor_id,))
        
        history = self.cursor.fetchall()
        
        if not history:
            tk.Label(
                card,
                text="No donation history found",
                font=('Segoe UI', 14),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(fill='x', padx=20)
            return
        
        # Create a small treeview for history
        history_frame = ttk.Frame(card, style='Card.TFrame')
        history_frame.pack(fill='x', padx=20, pady=10)
        
        columns = ('date', 'time', 'status', 'notes')
        history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show='headings',
            height=5  # Show only 5 rows to keep it compact
        )
        
        # Column configurations
        history_tree.heading('date', text='Date')
        history_tree.heading('time', text='Time Slot')
        history_tree.heading('status', text='Status')
        history_tree.heading('notes', text='Notes')
        
        history_tree.column('date', width=100)
        history_tree.column('time', width=150)
        history_tree.column('status', width=100)
        history_tree.column('notes', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=history_tree.yview
        )
        history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        history_tree.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate with history
        for entry in history:
            date_str = entry[0].strftime("%Y-%m-%d") if entry[0] else "N/A"
            time_slot = entry[1] if entry[1] else "N/A"
            status = entry[2] if entry[2] else "N/A"
            notes = entry[3] if entry[3] else ""
            
            history_tree.insert('', 'end', values=(date_str, time_slot, status, notes))

    def delete_selected_donor(self):
        # Get selected donor
        selection = self.donors_tree.selection()
        if not selection:
            messagebox.showinfo("Selection", "Please select a donor to delete")
            return
        
        donor_id = self.donors_tree.item(selection[0], 'values')[0]
        donor_name = self.donors_tree.item(selection[0], 'values')[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete donor '{donor_name}'?\n\nThis will also delete all donation history for this donor."
        )
        
        if not confirm:
            return
        
        try:
            # Begin transaction
            self.cursor.execute("START TRANSACTION")
            
            # Delete donation schedule entries first (foreign key constraint)
            self.cursor.execute(
                "DELETE FROM DonationSchedule WHERE donor_id = %s",
                (donor_id,)
            )
            
            # Delete donor
            self.cursor.execute(
                "DELETE FROM Donors WHERE id = %s",
                (donor_id,)
            )
            
            self.db.commit()
            messagebox.showinfo("Success", f"Donor '{donor_name}' deleted successfully")
            
            # Refresh the list
            self.refresh_donors_list()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Failed to delete donor: {str(e)}")

    def export_donors_list(self):
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"donors_list_{timestamp}.csv")
            
            # Get filtered data from tree
            with open(filename, 'w', newline='') as file:
                file.write("ID,Name,Age,Blood Group,Contact,Email,Last Donation,Health Status\n")
                
                for item_id in self.donors_tree.get_children():
                    values = self.donors_tree.item(item_id, 'values')
                    # Escape quotes in values
                    escaped_values = [f'"{str(v).replace(chr(34), chr(34)+chr(34))}"' for v in values]
                    file.write(','.join(escaped_values) + '\n')
            
            # Open the file
            os.startfile(filename) if os.name == 'nt' else os.system(f'open "{filename}"')
            
            messagebox.showinfo("Export Successful", f"Donors list exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export donors list: {str(e)}")
        
    def print_donor_details(self, donor_id):
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"donor_{donor_id}_{timestamp}.txt")
            
            # Fetch donor details
            self.cursor.execute("""
                SELECT d.*, 
                    (SELECT COUNT(*) FROM DonationSchedule WHERE donor_id = d.id) as donation_count
                FROM Donors d
                WHERE d.id = %s
            """, (donor_id,))
            
            donor = self.cursor.fetchone()
            
            if not donor:
                messagebox.showerror("Error", "Donor not found")
                return
                
            # Write to file
            with open(filename, 'w') as file:
                file.write("=========================================\n")
                file.write("          BLOOD BANK DONOR DETAILS       \n")
                file.write("=========================================\n\n")
                
                file.write(f"Donor ID: {donor[0]}\n")
                file.write(f"Name: {donor[1]}\n")
                file.write(f"Age: {donor[2]}\n")
                file.write(f"Blood Group: {donor[3]}\n")
                file.write(f"Contact: {donor[4]}\n")
                file.write(f"Email: {donor[5] if donor[5] else 'N/A'}\n")
                file.write(f"Address: {donor[6] if donor[6] else 'N/A'}\n")
                file.write(f"Last Donation: {donor[7].strftime('%Y-%m-%d') if donor[7] else 'Never'}\n")
                file.write(f"Health Status: {donor[8] if donor[8] else 'N/A'}\n")
                file.write(f"Registration Date: {donor[9].strftime('%Y-%m-%d %H:%M') if donor[9] else 'N/A'}\n")
                file.write(f"Total Donations: {donor[10]}\n\n")
                
                # Fetch donation history
                self.cursor.execute("""
                    SELECT scheduled_date, time_slot, status, notes
                    FROM DonationSchedule
                    WHERE donor_id = %s
                    ORDER BY scheduled_date DESC
                """, (donor_id,))
                
                history = self.cursor.fetchall()
                
                file.write("-----------------------------------------\n")
                file.write("             DONATION HISTORY            \n")
                file.write("-----------------------------------------\n\n")
                
                if not history:
                    file.write("No donation history found.\n")
                else:
                    for i, entry in enumerate(history, 1):
                        date_str = entry[0].strftime("%Y-%m-%d") if entry[0] else "N/A"
                        time_slot = entry[1] if entry[1] else "N/A"
                        status = entry[2] if entry[2] else "N/A"
                        notes = entry[3] if entry[3] else "None"
                        
                        file.write(f"Donation #{i}:\n")
                        file.write(f"  Date: {date_str}\n")
                        file.write(f"  Time Slot: {time_slot}\n")
                        file.write(f"  Status: {status}\n")
                        file.write(f"  Notes: {notes}\n")
                        file.write("\n")
                
                file.write("=========================================\n")
                file.write(f"Printed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=========================================\n")
            
            # Open the file
            os.startfile(filename) if os.name == 'nt' else os.system(f'open "{filename}"')
            
            messagebox.showinfo("Print", f"Donor details printed to {filename}")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print donor details: {str(e)}")

    def show_edit_donor_form(self, donor_id, parent_window=None):
        # Fetch donor information
        self.cursor.execute("""
            SELECT * FROM Donors WHERE id = %s
        """, (donor_id,))
        donor = self.cursor.fetchone()
        
        if not donor:
            messagebox.showerror("Error", "Donor not found")
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Donor")
        edit_window.geometry("800x800")
        edit_window.configure(bg=self.colors['bg_dark'])
        
        # Create a scrollable frame for the content
        main_canvas = tk.Canvas(edit_window, bg=self.colors['bg_dark'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=main_canvas.yview)
        
        # Pack the canvas and scrollbar
        main_canvas.pack(side='left', fill='both', expand=True)
        main_scrollbar.pack(side='right', fill='y')
        
        # Configure the canvas
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a frame inside the canvas for the content
        main_frame = ttk.Frame(main_canvas, style='Modern.TFrame')
        
        # Add the main frame to the canvas
        main_canvas_frame = main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
        
        # Make sure the frame takes the full width of the canvas
        def configure_frame(event):
            main_canvas.itemconfig(main_canvas_frame, width=event.width)
        main_canvas.bind('<Configure>', configure_frame)
        
        # Make sure the canvas can scroll the entire frame
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))
        main_frame.bind('<Configure>', configure_scroll_region)
        
        # Header
        tk.Label(
            main_frame,
            text=f"Edit Donor",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=10
        ).pack(fill='x', padx=20)
        
        # Form container with padding
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Form fields with pre-populated data
        fields = [
            ("Name*", "name", "text", donor[1]),
            ("Age*", "age", "number", str(donor[2])),
            ("Blood Group*", "blood_group", "combo", ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], donor[3]),
            ("Contact Number*", "contact", "text", donor[4]),
            ("Email", "email", "text", donor[5] if donor[5] else ""),
            ("Address", "address", "text", donor[6] if donor[6] else ""),
            ("Health Status", "health_status", "text", donor[8] if donor[8] else "")
        ]
        
        entries = {}
        
        for label_text, key, field_type, default, *args in fields:
            field_frame = ttk.Frame(form_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10, padx=20)
            
            tk.Label(
                field_frame,
                text=label_text,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            if field_type == "combo":
                entry = ttk.Combobox(
                    field_frame,
                    values=args[0],
                    state='readonly',
                    font=('Segoe UI', 11)
                )
                entry.set(default)
            elif field_type == "text":
                entry = ttk.Entry(
                    field_frame,
                    font=('Segoe UI', 11),
                    style='Modern.TEntry'
                )
                entry.insert(0, default)
            elif field_type == "number":
                entry = ttk.Entry(
                    field_frame,
                    font=('Segoe UI', 11),
                    style='Modern.TEntry'
                )
                entry.insert(0, default)
            
            entry.pack(fill='x', pady=(5, 0))
            entries[key] = entry
        
        # Buttons at the bottom of the form
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20, padx=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=edit_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Changes",
            style='Modern.TButton',
            command=lambda: self.update_donor(
                donor_id,
                entries,
                edit_window,
                parent_window
            )
        ).pack(side='right', padx=5)
        
        # Ensure buttons are visible by scrolling to the bottom
        edit_window.update_idletasks()
        main_canvas.yview_moveto(0.0)  # Scroll to top after loading

    def update_donor(self, donor_id, entries, edit_window, parent_window=None):
        try:
            # Validate required fields
            name = entries['name'].get().strip()
            age = entries['age'].get().strip()
            blood_group = entries['blood_group'].get()
            contact = entries['contact'].get().strip()
            email = entries['email'].get().strip()
            address = entries['address'].get().strip()
            health_status = entries['health_status'].get().strip()
            
            if not all([name, age, blood_group, contact]):
                raise ValueError("Please fill in all required fields")
            
            try:
                age = int(age)
                if age < 18 or age > 65:
                    raise ValueError("Age must be between 18 and 65")
            except ValueError:
                raise ValueError("Please enter a valid age")
            
            if email and not self.validate_email(email):
                raise ValueError("Please enter a valid email address")
            
            # Update donor in database
            self.cursor.execute("""
                UPDATE Donors
                SET name = %s, age = %s, blood_group = %s, contact_info = %s,
                    email = %s, address = %s, health_status = %s
                WHERE id = %s
            """, (name, age, blood_group, contact, email, address, health_status, donor_id))
            
            self.db.commit()
            messagebox.showinfo("Success", "Donor information updated successfully")
            
            # Close the edit window
            edit_window.destroy()
            
            # Close the parent window if provided
            if parent_window:
                parent_window.destroy()
            
            # Refresh the donors list if it's open
            if hasattr(self, 'donors_tree'):
                self.refresh_donors_list()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))

    # Function to show donation form with pre-selected donor
    def show_donation_form(self, blood_type=None, donor_id=None, parent_window=None):
        donation_window = tk.Toplevel(self.root)
        donation_window.title("New Blood Donation")
        donation_window.geometry("600x800")
        donation_window.configure(bg=self.colors['bg_dark'])
        
        # Create a scrollable frame for the content
        main_canvas = tk.Canvas(donation_window, bg=self.colors['bg_dark'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(donation_window, orient="vertical", command=main_canvas.yview)
        
        # Pack the canvas and scrollbar
        main_canvas.pack(side='left', fill='both', expand=True)
        main_scrollbar.pack(side='right', fill='y')
        
        # Configure the canvas
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a frame inside the canvas for the content
        main_frame = ttk.Frame(main_canvas, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Add the main frame to the canvas
        main_canvas_frame = main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
        
        # Make sure the frame takes the full width of the canvas
        def configure_frame(event):
            main_canvas.itemconfig(main_canvas_frame, width=event.width)
        main_canvas.bind('<Configure>', configure_frame)
        
        # Make sure the canvas can scroll the entire frame
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))
        main_frame.bind('<Configure>', configure_scroll_region)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=donation_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Header - Use tk.Label
        tk.Label(
            header_frame,
            text="New Blood Donation",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='x', pady=10)
        
        # Blood type selection
        blood_type_frame = ttk.Frame(form_frame, style='Card.TFrame')
        blood_type_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            blood_type_frame,
            text="Blood Type*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        blood_type_var = tk.StringVar(value=blood_type if blood_type else '')
        blood_type_combo = ttk.Combobox(
            blood_type_frame,
            textvariable=blood_type_var,
            values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            state='readonly' if blood_type else 'normal',
            style='Modern.TCombobox'
        )
        blood_type_combo.pack(fill='x', pady=(5, 0))
        
        # Units
        units_frame = ttk.Frame(form_frame, style='Card.TFrame')
        units_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            units_frame,
            text="Units*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        units_var = tk.StringVar(value="1")  # Default to 1 unit
        units_entry = ttk.Entry(
            units_frame,
            textvariable=units_var,
            style='Modern.TEntry'
        )
        units_entry.pack(fill='x', pady=(5, 0))
        
        # Donor Information
        donor_frame = ttk.Frame(form_frame, style='Card.TFrame')
        donor_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            donor_frame,
            text="Donor Selection",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        donor_var = tk.StringVar()
        
        # If donor_id is provided, select that donor
        if donor_id:
            self.cursor.execute(
                "SELECT id, name FROM Donors WHERE id = %s",
                (donor_id,)
            )
            selected_donor = self.cursor.fetchone()
            if selected_donor:
                donor_var.set(f"{selected_donor[0]} - {selected_donor[1]}")
        
        # Get list of donors matching blood type if specified
        filter_clause = ""
        filter_params = []
        
        if blood_type:
            filter_clause = "WHERE blood_group = %s"
            filter_params.append(blood_type)
        
        self.cursor.execute(
            f"SELECT id, name FROM Donors {filter_clause} ORDER BY name",
            filter_params
        )
        donors = self.cursor.fetchall()
        donor_list = [f"{d[0]} - {d[1]}" for d in donors]
        
        donor_combo = ttk.Combobox(
            donor_frame,
            textvariable=donor_var,
            values=donor_list,
            style='Modern.TCombobox'
        )
        donor_combo.pack(fill='x', pady=(5, 0))
        
        ttk.Button(
            donor_frame,
            text="➕ Add New Donor",
            style='Secondary.TButton',
            command=self.show_donor_registration
        ).pack(fill='x', pady=(10, 0))
        
        # Notes
        notes_frame = ttk.Frame(form_frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            notes_frame,
            text="Additional Notes",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        notes_text = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        notes_text.pack(fill='x', pady=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=donation_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Donation",
            style='Modern.TButton',
            command=lambda: self.save_donation(
                blood_type_var.get(),
                units_var.get(),
                donor_var.get(),
                notes_text.get("1.0", tk.END).strip(),
                donation_window,
                parent_window
            )
        ).pack(side='right', padx=5)
        
        # Ensure buttons are visible by scrolling to the bottom
        donation_window.update_idletasks()
        main_canvas.yview_moveto(0.0)  # Scroll to top after loading

    def create_personal_info_tab(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create scrollable canvas - Change background to bg
        canvas = tk.Canvas(
            frame,
            bg=self.colors['card_bg'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        fields = [
            ("Full Name*", "name", "text"),
            ("Age*", "age", "number"),
            ("Blood Group*", "blood_group", "combo", ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            ("Contact Number*", "contact", "text"),
            ("Email", "email", "text"),
            ("Address", "address", "text"),
            ("Emergency Contact", "emergency_contact", "text"),
            ("Occupation", "occupation", "text")
        ]
        
        self.personal_entries = {}
        
        for i, (label_text, key, field_type, *args) in enumerate(fields):
            field_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10)
            
            # Use tk.Label
            tk.Label(
                field_frame,
                text=label_text,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            if field_type == "combo":
                entry = ttk.Combobox(
                    field_frame,
                    values=args[0],
                    state='readonly',
                    font=('Segoe UI', 11)
                )
            else:
                entry = ttk.Entry(
                    field_frame,
                    font=('Segoe UI', 11),
                    style='Modern.TEntry'
                )
            
            entry.pack(fill='x', pady=(5, 0))
            self.personal_entries[key] = entry
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return frame

    def create_health_screening_tab(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Health questions
        questions = [
            ("Recent Donation", "Have you donated blood in the last 3 months?"),
            ("Chronic Disease", "Do you have any chronic diseases?"),
            ("Medications", "Are you currently taking any medications?"),
            ("Recent Surgery", "Have you had any recent surgeries?"),
            ("Infections", "Have you had any recent infections?"),
            ("Pregnancy", "Are you currently pregnant or have given birth in the last 6 months?"),
            ("Vaccinations", "Have you received any vaccinations in the last month?"),
            ("Allergies", "Do you have any severe allergies?")
        ]
        
        self.health_vars = {}
        
        for i, (key, question) in enumerate(questions):
            question_frame = ttk.Frame(frame, style='Card.TFrame')
            question_frame.pack(fill='x', padx=20, pady=10)
            
            var = tk.BooleanVar()
            self.health_vars[key] = var
            
            # Use tk.Label
            tk.Label(
                question_frame,
                text=question,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=5
            ).pack(side='left', pady=5)
            
            ttk.Checkbutton(
                question_frame,
                variable=var,
                style='Modern.TCheckbutton'
            ).pack(side='right')
            
            # Add separator
            if i < len(questions) - 1:
                # separator = ttk.Frame(frame, height=1, style='Card.TFrame')
                # separator.pack(fill='x', padx=20)
                # separator.configure(background=self.colors['border'])
                separator = tk.Frame(frame, height=1, bg=self.colors['border'])
                separator.pack(fill='x', padx=20)


        # Additional health notes
        notes_frame = ttk.Frame(frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=20)
        
        # Use tk.Label
        tk.Label(
            notes_frame,
            text="Additional Health Notes",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        self.health_notes = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.health_notes.pack(fill='x', pady=(5, 0))
        
        return frame

    def create_scheduling_tab(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Date selection
        date_frame = ttk.Frame(frame, style='Card.TFrame')
        date_frame.pack(fill='x', padx=20, pady=20)
        
        # Use tk.Label
        tk.Label(
            date_frame,
            text="Preferred Donation Date",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        # Replace DateEntry with ModernCalendar
        calendar_container = ttk.Frame(date_frame, style='Card.TFrame')
        calendar_container.pack(pady=(5, 0))
        
        self.date_entry = ModernCalendar(
            calendar_container,
            self.colors
        )
        self.date_entry.pack(fill='x')
        
        # Time slot selection
        time_frame = ttk.Frame(frame, style='Card.TFrame')
        time_frame.pack(fill='x', padx=20, pady=20)
        
        # Use tk.Label
        tk.Label(
            time_frame,
            text="Preferred Time Slot",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        # Time slots
        slots = ['Morning (9AM-12PM)', 'Afternoon (1PM-4PM)', 'Evening (5PM-8PM)']
        self.time_var = tk.StringVar()
        
        for slot in slots:
            ttk.Radiobutton(
                time_frame,
                text=slot,
                variable=self.time_var,
                value=slot,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Additional notes
        notes_frame = ttk.Frame(frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=20)
        
        # Use tk.Label
        tk.Label(
            notes_frame,
            text="Additional Notes for Scheduling",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        self.schedule_notes = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.schedule_notes.pack(fill='x', pady=(5, 0))
        
        return frame

    def save_donor_registration(self, window, notebook):
        try:
            # Validate current tab
            current_tab = notebook.select()
            tab_id = notebook.index(current_tab)
            
            if tab_id == 0:  # Personal Information
                self.validate_personal_info()
            elif tab_id == 1:  # Health Screening
                self.validate_health_screening()
            elif tab_id == 2:  # Scheduling
                self.validate_scheduling()
            
            # If all tabs are valid, save the donor
            self.save_donor_to_database(window)
            
            # After successful save, refresh dashboard
            self.show_dashboard()
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save donor: {str(e)}")

    def validate_personal_info(self):
        name = self.personal_entries['name'].get().strip()
        age = self.personal_entries['age'].get().strip()
        blood_group = self.personal_entries['blood_group'].get()
        contact = self.personal_entries['contact'].get().strip()
        email = self.personal_entries['email'].get().strip()
        
        if not all([name, age, blood_group, contact]):
            raise ValueError("Please fill in all required fields")
        
        try:
            age = int(age)
            if age < 18 or age > 65:
                raise ValueError("Age must be between 18 and 65")
        except ValueError:
            raise ValueError("Please enter a valid age")
        
        if email and not self.validate_email(email):
            raise ValueError("Please enter a valid email address")

    def validate_health_screening(self):
        if self.health_vars['Recent Donation'].get():
            raise ValueError("Cannot donate if donated in last 3 months")
        
        critical_conditions = [
            'Chronic Disease',
            'Medications',
            'Recent Surgery',
            'Infections',
            'Pregnancy'
        ]
        
        if any(self.health_vars[condition].get() for condition in critical_conditions):
            raise ValueError("Some health conditions prevent donation")

    def validate_scheduling(self):
        selected_date = self.date_entry.get_date()
        if not selected_date:
            raise ValueError("Please select a donation date")
        
        if not self.time_var.get():
            raise ValueError("Please select a time slot")
        
        # Validate that selected date is not in the past
        if selected_date < date.today():
            raise ValueError("Cannot schedule donation for past dates")

    def save_donor_to_database(self, window):
        try:
            # Insert donor information
            self.cursor.execute("""
                INSERT INTO Donors (
                    name, age, blood_group, contact_info,
                    email, address, health_status, donation_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.personal_entries['name'].get().strip(),
                int(self.personal_entries['age'].get()),
                self.personal_entries['blood_group'].get(),
                self.personal_entries['contact'].get().strip(),
                self.personal_entries['email'].get().strip(),
                self.personal_entries['address'].get().strip(),
                self.health_notes.get("1.0", tk.END).strip(),
                self.date_entry.get_date()
            ))
            
            # Get the donor ID
            donor_id = self.cursor.lastrowid
            
            # Schedule the donation
            self.cursor.execute("""
                INSERT INTO DonationSchedule (
                    donor_id, scheduled_date, time_slot, notes
                ) VALUES (%s, %s, %s, %s)
            """, (
                donor_id,
                self.date_entry.get_date(),
                self.time_var.get(),
                self.schedule_notes.get("1.0", tk.END).strip()
            ))
            
            # Update blood bank inventory - add 1 unit for the donation
            blood_group = self.personal_entries['blood_group'].get()
            self.cursor.execute("""
                UPDATE BloodBank 
                SET units_available = units_available + 1
                WHERE blood_group = %s
            """, (blood_group,))
            
            self.db.commit()
            messagebox.showinfo("Success", "Donor registered successfully!")
            window.destroy()
            
            # Refresh dashboard after donor registration to show updated stats
            self.show_dashboard()
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to save donor: {str(e)}")
    
    def show_blood_requests(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
                
        main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Header with stats
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back to Dashboard",
            style='Secondary.TButton',
            command=self.show_dashboard
        ).pack(side='left', padx=10, pady=5)
        
        # Title - Use tk.Label
        tk.Label(
            header_frame,
            text="Blood Requests",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # New request button
        ttk.Button(
            header_frame,
            text="➕ New Request",
            style='Modern.TButton',
            command=self.show_request_form
        ).pack(side='right')
        
        # Quick stats
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected
            FROM Requests
            WHERE request_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        stats = self.cursor.fetchone()
        
        stats_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stat_items = [
            ("Total Requests", stats[0], "📊"),
            ("Pending", stats[1], "⏳", self.colors['warning']),
            ("Approved", stats[2], "✅", self.colors['success']),
            ("Rejected", stats[3], "❌", self.colors['error'])
        ]
        
        for i, (label, value, icon, *colors) in enumerate(stat_items):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            color = colors[0] if colors else self.colors['text']
            
            # Use tk.Label
            tk.Label(
                card,
                text=f"{icon} {value}",
                font=('Segoe UI', 20, 'bold'),
                fg=color,
                bg=self.colors['card_bg']
            ).pack(pady=(10, 5))
            
            # Use tk.Label
            tk.Label(
                card,
                text=label,
                font=('Segoe UI', 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['card_bg']
            ).pack(pady=(0, 10))
        
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Filters and search
        filter_frame = self.create_request_filters(main_frame)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        # Request list
        self.create_request_list(main_frame)

    def create_request_header(self, parent):
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title - Use tk.Label
        tk.Label(
            header_frame,
            text="Blood Requests",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left')
        
        # New request button
        ttk.Button(
            header_frame,
            text="➕ New Request",
            style='Modern.TButton',
            command=self.show_request_form
        ).pack(side='right')
        
        # Quick stats
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected
            FROM Requests
            WHERE request_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        stats = self.cursor.fetchone()
        
        stats_frame = ttk.Frame(parent, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stat_items = [
            ("Total Requests", stats[0], "📊"),
            ("Pending", stats[1], "⏳", self.colors['warning']),
            ("Approved", stats[2], "✅", self.colors['success']),
            ("Rejected", stats[3], "❌", self.colors['error'])
        ]
        
        for i, (label, value, icon, *colors) in enumerate(stat_items):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            color = colors[0] if colors else self.colors['text']
            
            # Use tk.Label
            tk.Label(
                card,
                text=f"{icon} {value}",
                font=('Segoe UI', 20, 'bold'),
                fg=color,
                bg=self.colors['card_bg']
            ).pack(pady=(10, 5))
            
            # Use tk.Label
            tk.Label(
                card,
                text=label,
                font=('Segoe UI', 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['card_bg']
            ).pack(pady=(0, 10))
        
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

    def create_request_filters(self, parent):
        filter_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Status filter
        status_frame = ttk.Frame(filter_frame, style='Card.TFrame')
        status_frame.pack(side='left', padx=20, pady=10)
        
        self.status_var = tk.StringVar(value='All')
        
        # Use tk.Label
        tk.Label(
            status_frame,
            text="Status:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=(0, 10))
        
        for status in ['All', 'Pending', 'Approved', 'Rejected']:
            ttk.Radiobutton(
                status_frame,
                text=status,
                variable=self.status_var,
                value=status,
                command=self.refresh_requests,
                style='Modern.TRadiobutton'
            ).pack(side='left', padx=5)
        
        # Search
        search_frame = ttk.Frame(filter_frame, style='Card.TFrame')
        search_frame.pack(side='right', padx=20, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_requests())
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 11),
            width=30,
            style='Modern.TEntry'
        )
        search_entry.pack(side='right')
        
        # Use tk.Label
        tk.Label(
            search_frame,
            text="🔍",
            font=('Segoe UI', 12),
            bg=self.colors['card_bg']
        ).pack(side='right', padx=(0, 5))
        
        return filter_frame

    def create_request_list(self, parent):
        # Create Treeview
        columns = (
            'id', 'hospital', 'blood_group', 'units', 'date', 
            'priority', 'status', 'notes'
        )
        
        self.request_tree = ttk.Treeview(
            parent,
            columns=columns,
            show='headings',
            style='Modern.Treeview'
        )
        
        # Configure columns
        column_configs = {
            'id': ('ID', 50),
            'hospital': ('Hospital', 200),
            'blood_group': ('Blood Group', 100),
            'units': ('Units', 80),
            'date': ('Date', 100),
            'priority': ('Priority', 100),
            'status': ('Status', 100),
            'notes': ('Notes', 200)
        }
        
        for col, (heading, width) in column_configs.items():
            self.request_tree.heading(col, text=heading)
            self.request_tree.column(col, width=width)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.request_tree.yview
        )
        self.request_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.request_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event
        self.request_tree.bind('<Double-1>', self.show_request_details)
        
        # Initial load
        self.refresh_requests()

    def refresh_requests(self):
        self.request_tree.delete(*self.request_tree.get_children())
        
        status_filter = self.status_var.get()
        search_term = self.search_var.get().strip()
        
        query = """
            SELECT id, hospital_name, blood_group, units_requested,
                request_date, priority, status, notes
            FROM Requests
            WHERE (status = %s OR %s = 'All')
            AND (
                hospital_name LIKE %s
                OR blood_group LIKE %s
                OR notes LIKE %s
            )
            ORDER BY request_date DESC
        """
        
        search_pattern = f"%{search_term}%" if search_term else "%"
        self.cursor.execute(query, (
            status_filter, status_filter,
            search_pattern, search_pattern, search_pattern
        ))
        
        for row in self.cursor.fetchall():
            # Format date
            row = list(row)
            row[4] = row[4].strftime("%Y-%m-%d")
            
            # Add status color tags
            status = row[6]
            tag = f'status_{status.lower()}'
            
            self.request_tree.insert('', 'end', values=row, tags=(tag,))
        
        # Configure status colors
        self.request_tree.tag_configure(
            'status_pending',
            foreground=self.colors['warning']
        )
        self.request_tree.tag_configure(
            'status_approved',
            foreground=self.colors['success']
        )
        self.request_tree.tag_configure(
            'status_rejected',
            foreground=self.colors['error']
        )

    def show_request_details(self, event):
        item = self.request_tree.selection()[0]
        request_id = self.request_tree.item(item)['values'][0]
        
        details_window = tk.Toplevel(self.root)
        details_window.title("Request Details")
        details_window.geometry("600x800")
        details_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(details_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Fetch request details
        self.cursor.execute("""
            SELECT r.*, 
                b.units_available,
                (SELECT COUNT(*) FROM Requests 
                    WHERE hospital_name = r.hospital_name) as total_requests
            FROM Requests r
            LEFT JOIN BloodBank b ON r.blood_group = b.blood_group
            WHERE r.id = %s
        """, (request_id,))
        
        request = self.cursor.fetchone()
        
        # Header - Use tk.Label
        tk.Label(
            main_frame,
            text=f"Request #{request_id}",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(pady=(0, 20))
        
        # Create details card
        self.create_request_detail_card(main_frame, request)
        
        # Create action buttons
        self.create_request_action_buttons(main_frame, request)
        
        # Add Edit button
        edit_button = ttk.Button(
            main_frame,
            text="✏️ Edit Request",
            style='Modern.TButton',
            command=lambda: self.show_edit_request_form(request_id, details_window)
        )
        edit_button.pack(fill='x', pady=10)

    def create_request_detail_card(self, parent, request):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=10)
        
        details = [
            ("Hospital", request[1]),
            ("Blood Group", request[2]),
            ("Units Requested", request[3]),
            ("Request Date", request[4].strftime("%Y-%m-%d")),
            ("Priority", request[5]),
            ("Status", request[6]),
            ("Available Units", request[8]),
            ("Total Hospital Requests", request[9])
        ]
        
        for label, value in details:
            detail_frame = ttk.Frame(card, style='Card.TFrame')
            detail_frame.pack(fill='x', padx=20, pady=5)
            
            # Use tk.Label
            tk.Label(
                detail_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(side='left')
            
            value_color = self.get_value_color(label, value)
            
            # Use tk.Label
            tk.Label(
                detail_frame,
                text=str(value),
                font=('Segoe UI', 12, 'bold'),
                fg=value_color,
                bg=self.colors['card_bg']
            ).pack(side='right')
        
        if request[7]:  # Notes
            notes_frame = ttk.Frame(card, style='Card.TFrame')
            notes_frame.pack(fill='x', padx=20, pady=10)
            
            # Use tk.Label
            tk.Label(
                notes_frame,
                text="Notes:",
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            # Use tk.Label
            tk.Label(
                notes_frame,
                text=request[7],
                wraplength=500,
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['card_bg']
            ).pack(pady=(5, 0))

    def get_value_color(self, label, value):
        if label == "Status":
            status_colors = {
                'Pending': self.colors['warning'],
                'Approved': self.colors['success'],
                'Rejected': self.colors['error']
            }
            return status_colors.get(value, self.colors['text'])
        elif label == "Priority":
            priority_colors = {
                'Normal': self.colors['text'],
                'Urgent': self.colors['warning'],
                'Emergency': self.colors['error']
            }
            return priority_colors.get(value, self.colors['text'])
        elif label == "Available Units":
            if value < 5:
                return self.colors['error']
            elif value < 10:
                return self.colors['warning']
            return self.colors['success']
        
        return self.colors['text']

    def create_request_action_buttons(self, parent, request):
        button_frame = ttk.Frame(parent, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        if request[6] == 'Pending':
            ttk.Button(
                button_frame,
                text="✅ Approve",
                style='Modern.TButton',
                command=lambda: self.update_request_status(request[0], 'Approved')
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="❌ Reject",
                style='Modern.TButton',
                command=lambda: self.update_request_status(request[0], 'Rejected')
            ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="🖨️ Print",
            style='Secondary.TButton',
            command=lambda: self.print_request(request[0])
        ).pack(side='right', padx=5)

    def update_request_status(self, request_id, status):
        try:
            self.cursor.execute("""
                UPDATE Requests 
                SET status = %s 
                WHERE id = %s
            """, (status, request_id))
            
            if status == 'Approved':
                # Update blood bank inventory
                self.cursor.execute("""
                    UPDATE BloodBank b
                    JOIN Requests r ON b.blood_group = r.blood_group
                    SET b.units_available = b.units_available - r.units_requested
                    WHERE r.id = %s
                """, (request_id,))
            
            self.db.commit()
            messagebox.showinfo("Success", f"Request {status.lower()} successfully")
            self.refresh_requests()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Failed to update request: {str(e)}")
            
    def print_request(self, request_id):
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"request_{request_id}_{timestamp}.txt")
            
            # Fetch request details
            self.cursor.execute("""
                SELECT r.*, b.units_available
                FROM Requests r
                LEFT JOIN BloodBank b ON r.blood_group = b.blood_group
                WHERE r.id = %s
            """, (request_id,))
            
            request = self.cursor.fetchone()
            
            if not request:
                messagebox.showerror("Error", "Request not found")
                return
                
            # Write to file
            with open(filename, 'w') as file:
                file.write("=========================================\n")
                file.write("        BLOOD BANK REQUEST DETAILS       \n")
                file.write("=========================================\n\n")
                
                file.write(f"Request ID: {request_id}\n")
                file.write(f"Hospital: {request[1]}\n")
                file.write(f"Blood Group: {request[2]}\n")
                file.write(f"Units Requested: {request[3]}\n")
                file.write(f"Request Date: {request[4].strftime('%Y-%m-%d')}\n")
                file.write(f"Priority: {request[5]}\n")
                file.write(f"Status: {request[6]}\n")
                
                if request[7]:  # Notes
                    file.write(f"\nNotes:\n{request[7]}\n")
                    
                file.write("\n-----------------------------------------\n")
                file.write(f"Current Inventory for {request[2]}: {request[8]} units\n")
                file.write(f"Printed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=========================================\n")
            
            # Open the file
            os.startfile(filename) if os.name == 'nt' else os.system(f'open "{filename}"')
            
            messagebox.showinfo("Print", f"Request details printed to {filename}")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print request: {str(e)}")
        
    def show_analytics(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
                
        main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back to Dashboard",
            style='Secondary.TButton',
            command=self.show_dashboard
        ).pack(side='left', padx=10, pady=5)
        
        # Title
        tk.Label(
            header_frame,
            text="Analytics Dashboard",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Create date range selector
        date_range_frame = ttk.Frame(header_frame, style='Card.TFrame')
        date_range_frame.pack(side='right')
        
        # Use tk.Label
        tk.Label(
            date_range_frame,
            text="Date Range:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=(0, 10))
        
        ranges = ['Last 7 Days', 'Last 30 Days', 'Last 3 Months', 'Last Year']
        self.date_range_var = tk.StringVar(value='Last 30 Days')
        
        range_combo = ttk.Combobox(
            date_range_frame,
            textvariable=self.date_range_var,
            values=ranges,
            state='readonly',
            style='Modern.TCombobox'
        )
        range_combo.pack(side='left')
        range_combo.bind('<<ComboboxSelected>>', self.update_analytics)
        
        # Create charts grid
        charts_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        charts_frame.pack(fill='both', expand=True)
        
        # Configure grid
        for i in range(2):
            charts_frame.grid_columnconfigure(i, weight=1)
            charts_frame.grid_rowconfigure(i, weight=1)
        
        # Create charts
        self.create_donation_trend_chart(charts_frame, 0, 0)
        self.create_blood_type_distribution_chart(charts_frame, 0, 1)
        self.create_request_status_chart(charts_frame, 1, 0)
        self.create_inventory_levels_chart(charts_frame, 1, 1)

    def create_donation_trend_chart(self, parent, row, col):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Use tk.Label
        tk.Label(
            frame,
            text="Donation Trends",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=20,
            pady=10
        ).pack(pady=(10, 20))
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        # Get donation data
        date_range = self.get_date_range()
        self.cursor.execute("""
            SELECT DATE(donation_date) as date, COUNT(*) as count
            FROM Donors
            WHERE donation_date >= %s
            GROUP BY DATE(donation_date)
            ORDER BY date
        """, (date_range,))
        
        dates = []
        counts = []
        for date, count in self.cursor.fetchall():
            dates.append(date)
            counts.append(count)
        
        # Plot data
        ax.plot(dates, counts, color=self.colors['accent'], marker='o')
        ax.set_facecolor(self.colors['chart_bg'])
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, color=self.colors['grid'], linestyle='--', alpha=0.7)
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def create_blood_type_distribution_chart(self, parent, row, col):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Use tk.Label
        tk.Label(
            frame,
            text="Blood Type Distribution",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=20,
            pady=10
        ).pack(pady=(10, 20))
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        # Get blood type data
        self.cursor.execute("""
            SELECT blood_group, units_available
            FROM BloodBank
            ORDER BY blood_group
        """)
        
        blood_types = []
        units = []
        for blood_type, unit in self.cursor.fetchall():
            blood_types.append(blood_type)
            units.append(unit)
        
        # Create pie chart
        colors = [self.colors['accent'], self.colors['success'], 
                self.colors['warning'], self.colors['error']]
        ax.pie(units, labels=blood_types, colors=colors, autopct='%1.1f%%')
        ax.set_facecolor(self.colors['chart_bg'])
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def create_request_status_chart(self, parent, row, col):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Use tk.Label
        tk.Label(
            frame,
            text="Request Status Distribution",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=20,
            pady=10
        ).pack(pady=(10, 20))
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        # Get request status data
        date_range = self.get_date_range()
        self.cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM Requests
            WHERE request_date >= %s
            GROUP BY status
        """, (date_range,))
        
        statuses = []
        counts = []
        for status, count in self.cursor.fetchall():
            statuses.append(status)
            counts.append(count)
        
        # Create bar chart
        status_colors = {
            'Pending': self.colors['warning'],
            'Approved': self.colors['success'],
            'Rejected': self.colors['error']
        }
        
        colors = [status_colors.get(status, self.colors['accent']) for status in statuses]
        
        ax.bar(statuses, counts, color=colors)
        ax.set_facecolor(self.colors['chart_bg'])
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, color=self.colors['grid'], linestyle='--', alpha=0.7)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def create_inventory_levels_chart(self, parent, row, col):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Use tk.Label
        tk.Label(
            frame,
            text="Current Inventory Levels",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=20,
            pady=10
        ).pack(pady=(10, 20))
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        # Get inventory data
        self.cursor.execute("""
            SELECT blood_group, units_available
            FROM BloodBank
            ORDER BY blood_group
        """)
        
        blood_types = []
        units = []
        for blood_type, unit in self.cursor.fetchall():
            blood_types.append(blood_type)
            units.append(unit)
        
        # Create horizontal bar chart
        bars = ax.barh(blood_types, units, color=self.colors['accent'])
        ax.set_facecolor(self.colors['chart_bg'])
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, color=self.colors['grid'], linestyle='--', alpha=0.7)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                f'{int(width):,}',
                ha='left', va='center', color=self.colors['text'])
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def get_date_range(self):
        range_text = self.date_range_var.get()
        today = date.today()
        
        if range_text == 'Last 7 Days':
            return today - timedelta(days=7)
        elif range_text == 'Last 30 Days':
            return today - timedelta(days=30)
        elif range_text == 'Last 3 Months':
            return today - timedelta(days=90)
        else:  # Last Year
            return today - timedelta(days=365)

    def show_edit_request_form(self, request_id, parent_window):
        # Fetch the current request data
        self.cursor.execute("""
            SELECT * FROM Requests WHERE id = %s
        """, (request_id,))
        request = self.cursor.fetchone()
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Request")
        edit_window.geometry("600x700")
        edit_window.configure(bg=self.colors['bg_dark'])
        
        # Create a scrollable canvas
        main_canvas = tk.Canvas(edit_window, bg=self.colors['bg_dark'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=main_canvas.yview)
        
        # Pack the canvas and scrollbar
        main_canvas.pack(side='left', fill='both', expand=True)
        main_scrollbar.pack(side='right', fill='y')
        
        # Configure the canvas
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a frame inside the canvas for the content
        main_frame = ttk.Frame(main_canvas, style='Modern.TFrame')
        
        # Add the main frame to the canvas
        main_canvas_frame = main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
        
        # Make sure the frame takes the full width of the canvas
        def configure_frame(event):
            main_canvas.itemconfig(main_canvas_frame, width=event.width)
        main_canvas.bind('<Configure>', configure_frame)
        
        # Make sure the canvas can scroll the entire frame
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))
        main_frame.bind('<Configure>', configure_scroll_region)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=edit_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Add header
        tk.Label(
            header_frame,
            text=f"Edit Request #{request_id}",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form container
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='x', pady=10)
        
        # Hospital name
        hospital_frame = ttk.Frame(form_frame, style='Card.TFrame')
        hospital_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            hospital_frame,
            text="Hospital Name*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        hospital_var = tk.StringVar(value=request[1])  # Pre-fill with current value
        hospital_entry = ttk.Entry(
            hospital_frame,
            textvariable=hospital_var,
            font=('Segoe UI', 12),
            style='Modern.TEntry'
        )
        hospital_entry.pack(fill='x', pady=(5, 0))
        
        # Blood type
        blood_type_frame = ttk.Frame(form_frame, style='Card.TFrame')
        blood_type_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            blood_type_frame,
            text="Blood Type*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        blood_type_var = tk.StringVar(value=request[2])  # Pre-fill with current value
        blood_type_combo = ttk.Combobox(
            blood_type_frame,
            textvariable=blood_type_var,
            values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            state='readonly',
            font=('Segoe UI', 12)
        )
        blood_type_combo.pack(fill='x', pady=(5, 0))
        
        # Units
        units_frame = ttk.Frame(form_frame, style='Card.TFrame')
        units_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            units_frame,
            text="Units Required*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        units_var = tk.StringVar(value=str(request[3]))  # Pre-fill with current value
        units_entry = ttk.Entry(
            units_frame,
            textvariable=units_var,
            font=('Segoe UI', 12),
            style='Modern.TEntry'
        )
        units_entry.pack(fill='x', pady=(5, 0))
        
        # Priority
        priority_frame = ttk.Frame(form_frame, style='Card.TFrame')
        priority_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            priority_frame,
            text="Priority*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        priority_var = tk.StringVar(value=request[5])  # Pre-fill with current value
        for priority in ['Normal', 'Urgent', 'Emergency']:
            ttk.Radiobutton(
                priority_frame,
                text=priority,
                variable=priority_var,
                value=priority,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Status
        status_frame = ttk.Frame(form_frame, style='Card.TFrame')
        status_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            status_frame,
            text="Status*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        status_var = tk.StringVar(value=request[6])  # Pre-fill with current value
        for status in ['Pending', 'Approved', 'Rejected']:
            ttk.Radiobutton(
                status_frame,
                text=status,
                variable=status_var,
                value=status,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Notes
        notes_frame = ttk.Frame(form_frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            notes_frame,
            text="Additional Notes",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        notes_text = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        notes_text.pack(fill='x', pady=(5, 0))
        # Pre-fill with current notes if any
        if request[7]:
            notes_text.insert("1.0", request[7])
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=edit_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Changes",
            style='Modern.TButton',
            command=lambda: self.update_request(
                request_id,
                hospital_var.get(),
                blood_type_var.get(),
                units_var.get(),
                priority_var.get(),
                status_var.get(),
                notes_text.get("1.0", tk.END).strip(),
                edit_window,
                parent_window
            )
        ).pack(side='right', padx=5)
        
        # Ensure buttons are visible by scrolling to the top
        edit_window.update_idletasks()
        main_canvas.yview_moveto(0.0)  # Start scrolled to the top

    def update_request(self, request_id, hospital, blood_type, units, priority, status, notes, edit_window, parent_window=None):
        try:
            # Validate inputs
            if not all([hospital, blood_type, units]):
                raise ValueError("Please fill in all required fields")
            
            try:
                units = int(units)
                if units <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Please enter a valid number of units")
            
            # Get the original request data for comparison
            self.cursor.execute("""
                SELECT blood_group, units_requested, status 
                FROM Requests 
                WHERE id = %s
            """, (request_id,))
            original = self.cursor.fetchone()
            orig_blood_group, orig_units, orig_status = original
            
            # Begin transaction
            self.cursor.execute("START TRANSACTION")
            
            # Update request in database
            self.cursor.execute("""
                UPDATE Requests 
                SET hospital_name = %s, blood_group = %s, units_requested = %s,
                    priority = %s, status = %s, notes = %s
                WHERE id = %s
            """, (hospital, blood_type, units, priority, status, notes, request_id))
            
            # Handle status changes from Pending to Approved or Rejected
            if orig_status != status:
                if status == 'Approved' and orig_status != 'Approved':
                    # If approved, decrease blood bank inventory
                    self.cursor.execute("""
                        UPDATE BloodBank
                        SET units_available = units_available - %s
                        WHERE blood_group = %s
                    """, (units, blood_type))
                elif orig_status == 'Approved' and status != 'Approved':
                    # If un-approving, restore the blood bank inventory
                    self.cursor.execute("""
                        UPDATE BloodBank
                        SET units_available = units_available + %s
                        WHERE blood_group = %s
                    """, (orig_units, orig_blood_group))
            
            # If still approved but changed units or blood type
            elif status == 'Approved' and orig_status == 'Approved':
                if blood_type != orig_blood_group:
                    # Different blood group - restore original and reduce new
                    self.cursor.execute("""
                        UPDATE BloodBank
                        SET units_available = units_available + %s
                        WHERE blood_group = %s
                    """, (orig_units, orig_blood_group))
                    
                    self.cursor.execute("""
                        UPDATE BloodBank
                        SET units_available = units_available - %s
                        WHERE blood_group = %s
                    """, (units, blood_type))
                elif units != orig_units:
                    # Same blood group but different units
                    difference = orig_units - units
                    self.cursor.execute("""
                        UPDATE BloodBank
                        SET units_available = units_available + %s
                        WHERE blood_group = %s
                    """, (difference, blood_type))
            
            self.db.commit()
            messagebox.showinfo("Success", "Request updated successfully!")
            
            # Close windows
            edit_window.destroy()
            if parent_window:
                parent_window.destroy()
            
            # Refresh the requests view and dashboard
            self.refresh_requests()
            self.show_dashboard()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))

    def save_donation(self, blood_type, units, donor, notes, window, parent_window=None):
        try:
            if not all([blood_type, units, donor]):
                raise ValueError("Please fill in all required fields")
            
            try:
                units = int(units)
                if units <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Please enter a valid number of units")
            
            # Extract donor ID
            donor_id = int(donor.split(" - ")[0])
            
            # Begin transaction
            self.cursor.execute("START TRANSACTION")
            
            # Update blood bank inventory
            self.cursor.execute("""
                UPDATE BloodBank 
                SET units_available = units_available + %s 
                WHERE blood_group = %s
            """, (units, blood_type))
            
            # Record donation
            self.cursor.execute("""
                UPDATE Donors 
                SET donation_date = CURDATE()
                WHERE id = %s
            """, (donor_id,))
            
            # Add to donation schedule
            self.cursor.execute("""
                INSERT INTO DonationSchedule (
                    donor_id, scheduled_date, time_slot, status, notes
                ) VALUES (%s, CURDATE(), NOW(), 'Completed', %s)
            """, (donor_id, notes))
            
            self.db.commit()
            messagebox.showinfo("Success", "Donation recorded successfully!")
            
            # Close windows
            window.destroy()
            if parent_window:
                parent_window.destroy()
            
            # Refresh dashboard to reflect changes
            self.show_dashboard()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))

    def update_analytics(self, event=None):
        """Refresh all analytics charts based on current date range"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
                    
        main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back to Dashboard",
            style='Secondary.TButton',
            command=self.show_dashboard
        ).pack(side='left', padx=10, pady=5)
        
        # Title
        tk.Label(
            header_frame,
            text="Analytics Dashboard",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Create date range selector
        date_range_frame = ttk.Frame(header_frame, style='Card.TFrame')
        date_range_frame.pack(side='right')
        
        # Use tk.Label
        tk.Label(
            date_range_frame,
            text="Date Range:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(side='left', padx=(0, 10))
        
        ranges = ['Last 7 Days', 'Last 30 Days', 'Last 3 Months', 'Last Year']
        self.date_range_var = tk.StringVar(value='Last 30 Days')
        
        range_combo = ttk.Combobox(
            date_range_frame,
            textvariable=self.date_range_var,
            values=ranges,
            state='readonly',
            style='Modern.TCombobox'
        )
        range_combo.pack(side='left')
        range_combo.bind('<<ComboboxSelected>>', lambda e: self.update_analytics())
        
        # Create charts grid
        charts_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        charts_frame.pack(fill='both', expand=True)
        
        # Configure grid
        for i in range(2):
            charts_frame.grid_columnconfigure(i, weight=1)
            charts_frame.grid_rowconfigure(i, weight=1)
        
        # Create overview stats
        stats_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Create charts with real data
        self.create_donation_trend_chart(charts_frame, 0, 0)
        self.create_blood_type_distribution_chart(charts_frame, 0, 1)
        self.create_request_status_chart(charts_frame, 1, 0)
        self.create_inventory_levels_chart(charts_frame, 1, 1)

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("800x600")
        settings_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(settings_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=settings_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Header - Use tk.Label
        tk.Label(
            header_frame,
            text="System Settings",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Settings sections
        sections = [
            ("User Management", "👥", self.show_user_management),
            ("Notification Settings", "🔔", self.show_notification_settings),
            ("Database Backup", "💾", self.backup_database),
            ("Theme Settings", "🎨", self.show_theme_settings),
            ("System Logs", "📋", self.show_system_logs)
        ]
        
        for title, icon, command in sections:
            section_frame = ttk.Frame(main_frame, style='Card.TFrame')
            section_frame.pack(fill='x', pady=5)
            
            # Use tk.Label
            tk.Label(
                section_frame,
                text=f"{icon} {title}",
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(side='left', padx=20, pady=15)
            
            ttk.Button(
                section_frame,
                text="Configure",
                style='Modern.TButton',
                command=command
            ).pack(side='right', padx=20)

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def show_donation_form(self, blood_type=None):
        donation_window = tk.Toplevel(self.root)
        donation_window.title("New Blood Donation")
        donation_window.geometry("600x800")
        donation_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(donation_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=donation_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Header - Use tk.Label
        tk.Label(
            header_frame,
            text="New Blood Donation",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='x', pady=10)
        
        # Blood type selection
        blood_type_frame = ttk.Frame(form_frame, style='Card.TFrame')
        blood_type_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            blood_type_frame,
            text="Blood Type*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        blood_type_var = tk.StringVar(value=blood_type if blood_type else '')
        blood_type_combo = ttk.Combobox(
            blood_type_frame,
            textvariable=blood_type_var,
            values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            state='readonly' if blood_type else 'normal',
            style='Modern.TCombobox'
        )
        blood_type_combo.pack(fill='x', pady=(5, 0))
        
        # Units
        units_frame = ttk.Frame(form_frame, style='Card.TFrame')
        units_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            units_frame,
            text="Units*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        units_var = tk.StringVar()
        units_entry = ttk.Entry(
            units_frame,
            textvariable=units_var,
            style='Modern.TEntry'
        )
        units_entry.pack(fill='x', pady=(5, 0))
        
        # Donor Information
        donor_frame = ttk.Frame(form_frame, style='Card.TFrame')
        donor_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            donor_frame,
            text="Donor Selection",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        donor_var = tk.StringVar()
        self.cursor.execute(
            "SELECT id, name FROM Donors WHERE blood_group = %s",
            (blood_type if blood_type else 'A+',)
        )
        donors = self.cursor.fetchall()
        donor_list = [f"{d[0]} - {d[1]}" for d in donors]
        
        donor_combo = ttk.Combobox(
            donor_frame,
            textvariable=donor_var,
            values=donor_list,
            style='Modern.TCombobox'
        )
        donor_combo.pack(fill='x', pady=(5, 0))
        
        ttk.Button(
            donor_frame,
            text="➕ Add New Donor",
            style='Secondary.TButton',
            command=self.show_donor_registration
        ).pack(fill='x', pady=(10, 0))
        
        # Notes
        notes_frame = ttk.Frame(form_frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=10)
        
        # Use tk.Label
        tk.Label(
            notes_frame,
            text="Additional Notes",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        notes_text = tk.Text(
            notes_frame,
            height=4,
            font=('Segoe UI', 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        notes_text.pack(fill='x', pady=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=donation_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Donation",
            style='Modern.TButton',
            command=lambda: self.save_donation(
                blood_type_var.get(),
                units_var.get(),
                donor_var.get(),
                notes_text.get("1.0", tk.END).strip(),
                donation_window
            )
        ).pack(side='right', padx=5)

    def save_donation(self, blood_type, units, donor, notes, window):
        try:
            if not all([blood_type, units, donor]):
                raise ValueError("Please fill in all required fields")
            
            try:
                units = int(units)
                if units <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Please enter a valid number of units")
            
            # Extract donor ID
            donor_id = int(donor.split(" - ")[0])
            
            # Begin transaction
            self.cursor.execute("START TRANSACTION")
            
            # Update blood bank inventory
            self.cursor.execute("""
                UPDATE BloodBank 
                SET units_available = units_available + %s 
                WHERE blood_group = %s
            """, (units, blood_type))
            
            # Record donation
            self.cursor.execute("""
                UPDATE Donors 
                SET donation_date = CURDATE()
                WHERE id = %s
            """, (donor_id,))
            
            # Add to donation schedule
            self.cursor.execute("""
                INSERT INTO DonationSchedule (
                    donor_id, scheduled_date, time_slot, status, notes
                ) VALUES (%s, CURDATE(), NOW(), 'Completed', %s)
            """, (donor_id, notes))
            
            self.db.commit()
            messagebox.showinfo("Success", "Donation recorded successfully!")
            window.destroy()
            self.show_dashboard()  # Refresh dashboard
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))

    def backup_database(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.sql"
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Backup in Progress")
            progress_window.geometry("300x150")
            progress_window.configure(bg=self.colors['bg_dark'])
            
            # Use tk.Label
            tk.Label(
                progress_window,
                text="Creating Database Backup...",
                font=('Segoe UI', 16),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(pady=20)
            
            progress = ttk.Progressbar(
                progress_window,
                mode='indeterminate'
            )
            progress.pack(fill='x', padx=20)
            progress.start()
            
            # Perform backup
            os.system(f"mysqldump -u bloodbank_user -pBloodBank@123 blood_bank > {backup_path}")
            
            progress_window.destroy()
            messagebox.showinfo("Success", f"Database backed up successfully to {backup_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def show_notification_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Notification Settings")
        settings_window.geometry("500x600")
        settings_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(settings_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=settings_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Notification Settings",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Notification options
        options = [
            ("Low Inventory Alerts", "low_inventory"),
            ("New Donation Notifications", "new_donation"),
            ("Request Status Updates", "request_status"),
            ("Donation Schedule Reminders", "schedule_reminder"),
            ("System Updates", "system_updates")
        ]
        
        for label, key in options:
            option_frame = ttk.Frame(main_frame, style='Card.TFrame')
            option_frame.pack(fill='x', pady=5)
            
            # Use tk.Label
            tk.Label(
                option_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(side='left', padx=20, pady=10)
            
            tk.BooleanVar(value=True)  # Default to enabled
            ttk.Checkbutton(
                option_frame,
                style='Modern.TCheckbutton'
            ).pack(side='right', padx=20)

    def show_theme_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Theme Settings")
        settings_window.geometry("500x600")
        settings_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(settings_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=settings_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Theme Settings",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Theme options
        themes = [
            ("Dark Theme", "dark"),
            ("Light Theme", "light"),
            ("Blue Theme", "blue"),
            ("Green Theme", "green")
        ]
        
        theme_var = tk.StringVar(value="dark")
        
        for label, value in themes:
            theme_frame = ttk.Frame(main_frame, style='Card.TFrame')
            theme_frame.pack(fill='x', pady=5)
            
            ttk.Radiobutton(
                theme_frame,
                text=label,
                variable=theme_var,
                value=value,
                style='Modern.TRadiobutton'
            ).pack(pady=10)

    def show_system_logs(self):
        logs_window = tk.Toplevel(self.root)
        logs_window.title("System Logs")
        logs_window.geometry("800x600")
        logs_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(logs_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=logs_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="System Logs",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Create Treeview for logs
        columns = ('timestamp', 'action', 'user', 'details')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        tree.heading('timestamp', text='Timestamp')
        tree.heading('action', text='Action')
        tree.heading('user', text='User')
        tree.heading('details', text='Details')
        
        tree.pack(fill='both', expand=True)
        
        # Add sample log entries
        sample_logs = [
            (datetime.now(), "Login", "admin", "Successful login"),
            (datetime.now(), "Donation", "staff", "New donation recorded"),
            (datetime.now(), "Request", "admin", "Blood request approved")
        ]
        
        for log in sample_logs:
            tree.insert('', 'end', values=log)

    def show_user_management(self):
        users_window = tk.Toplevel(self.root)
        users_window.title("User Management")
        users_window.geometry("800x600")
        users_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(users_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header with add user button
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=users_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="User Management",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        ttk.Button(
            header_frame,
            text="➕ Add User",
            style='Modern.TButton',
            command=self.show_add_user_form
        ).pack(side='right')
        
        # User list
        columns = ('username', 'role', 'email', 'last_login')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        tree.heading('username', text='Username')
        tree.heading('role', text='Role')
        tree.heading('email', text='Email')
        tree.heading('last_login', text='Last Login')
        
        tree.pack(fill='both', expand=True)
        
        # Load users
        self.cursor.execute(
            "SELECT username, role, email, last_login FROM Users"
        )
        
        for user in self.cursor.fetchall():
            tree.insert('', 'end', values=user)

    def show_add_user_form(self):
        user_window = tk.Toplevel(self.root)
        user_window.title("Add New User")
        user_window.geometry("500x600")
        user_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(user_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Use tk.Label
        tk.Label(
            main_frame,
            text="Add New User",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Username*", "username"),
            ("Password*", "password"),
            ("Confirm Password*", "confirm_password"),
            ("Email*", "email")
        ]
        
        entries = {}
        for label, key in fields:
            field_frame = ttk.Frame(main_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10)
            
            # Use tk.Label
            tk.Label(
                field_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            entry = ttk.Entry(
                field_frame,
                style='Modern.TEntry',
                show="•" if 'password' in key else ""
            )
            entry.pack(fill='x', pady=(5, 0))
            entries[key] = entry
        
        # Role selection
        role_frame = ttk.Frame(main_frame, style='Card.TFrame')
        role_frame.pack(fill='x', pady=10)
        
        # Use tk.Label
        tk.Label(
            role_frame,
            text="Role*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        role_var = tk.StringVar(value='staff')
        roles = [('Admin', 'admin'), ('Staff', 'staff')]
        
        for role_text, role_value in roles:
            ttk.Radiobutton(
                role_frame,
                text=role_text,
                variable=role_var,
                value=role_value,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=user_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Create User",
            style='Modern.TButton',
            command=lambda: self.create_user(
                entries['username'].get(),
                entries['password'].get(),
                entries['confirm_password'].get(),
                entries['email'].get(),
                role_var.get(),
                user_window
            )
        ).pack(side='right', padx=5)

    def show_password_reset(self):
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("400x500")
        reset_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(reset_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=reset_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Reset Password",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form fields
        fields = [
            ("Username*", "username"),
            ("Email*", "email"),
            ("New Password*", "password"),
            ("Confirm Password*", "confirm")
        ]
        
        entries = {}
        for label, key in fields:
            field_frame = ttk.Frame(main_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10)
            
            # Use tk.Label
            tk.Label(
                field_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            entry = ttk.Entry(
                field_frame,
                style='Modern.TEntry',
                show="•" if 'password' in key else ""
            )
            entry.pack(fill='x', pady=(5, 0))
            entries[key] = entry
        
        ttk.Button(
            main_frame,
            text="Reset Password",
            style='Modern.TButton',
            command=lambda: self.reset_password(
                entries['username'].get(),
                entries['email'].get(),
                entries['password'].get(),
                entries['confirm'].get(),
                reset_window
            )
        ).pack(fill='x', pady=20)

    def generate_report(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Report")
        report_window.geometry("800x800")  # Made taller to accommodate calendars
        report_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(report_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=report_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Generate Report",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Date range selection
        date_frame = ttk.Frame(main_frame, style='Card.TFrame')
        date_frame.pack(fill='x', pady=10)
        
        # Use tk.Label
        tk.Label(
            date_frame,
            text="Date Range",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w', padx=20)
        
        # Calendar container
        calendars_frame = ttk.Frame(date_frame, style='Card.TFrame')
        calendars_frame.pack(fill='x', padx=20, pady=10)
        
        # Start date
        start_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        start_frame.pack(side='left', padx=10)
        
        # Use tk.Label
        tk.Label(
            start_frame,
            text="From:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()
        
        start_date = ModernCalendar(
            start_frame,
            self.colors
        )
        start_date.pack()
        
        # End date
        end_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        end_frame.pack(side='left', padx=10)
        
        # Use tk.Label
        tk.Label(
            end_frame,
            text="To:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()
        
        end_date = ModernCalendar(
            end_frame,
            self.colors
        )
        end_date.pack()
        
        # Report type selection
        report_frame = ttk.Frame(main_frame, style='Card.TFrame')
        report_frame.pack(fill='x', pady=20)
        
        # Use tk.Label
        tk.Label(
            report_frame,
            text="Report Type",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w', padx=20)
        
        report_var = tk.StringVar(value="donation")
        for report_type, label in [
            ("donation", "Donation Report"),
            ("inventory", "Inventory Report"),
            ("requests", "Requests Report"),
            ("users", "Users Activity Report")
        ]:
            ttk.Radiobutton(
                report_frame,
                text=label,
                variable=report_var,
                value=report_type,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', padx=40, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Generate PDF",
            style='Modern.TButton',
            command=lambda: self.generate_pdf_report(
                start_date, 
                end_date,
                report_var.get()
            )
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Export to Excel",
            style='Modern.TButton',
            command=lambda: self.export_excel_report(
                start_date,
                end_date,
                report_var.get()
            )
        ).pack(side='right', padx=5)

    def show_add_user_form(self):
        user_window = tk.Toplevel(self.root)
        user_window.title("Add New User")
        user_window.geometry("500x600")
        user_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(user_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        ttk.Button(
            header_frame,
            text="← Back",
            style='Secondary.TButton',
            command=user_window.destroy
        ).pack(side='left', pady=5, padx=5)
        
        # Use tk.Label
        tk.Label(
            header_frame,
            text="Add New User",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(side='left', padx=20)
        
        # Form fields
        fields = [
            ("Username*", "username"),
            ("Password*", "password"),
            ("Confirm Password*", "confirm_password"),
            ("Email*", "email")
        ]
        
        entries = {}
        for label, key in fields:
            field_frame = ttk.Frame(main_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10)
            
            # Use tk.Label
            tk.Label(
                field_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            entry = ttk.Entry(
                field_frame,
                style='Modern.TEntry',
                show="•" if 'password' in key else ""
            )
            entry.pack(fill='x', pady=(5, 0))
            entries[key] = entry
        
        # Role selection
        role_frame = ttk.Frame(main_frame, style='Card.TFrame')
        role_frame.pack(fill='x', pady=10)
        
        # Use tk.Label
        tk.Label(
            role_frame,
            text="Role*",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w')
        
        role_var = tk.StringVar(value='staff')
        roles = [('Admin', 'admin'), ('Staff', 'staff')]
        
        for role_text, role_value in roles:
            ttk.Radiobutton(
                role_frame,
                text=role_text,
                variable=role_var,
                value=role_value,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=user_window.destroy
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Create User",
            style='Modern.TButton',
            command=lambda: self.create_user(
                entries['username'].get(),
                entries['password'].get(),
                entries['confirm_password'].get(),
                entries['email'].get(),
                role_var.get(),
                user_window
            )
        ).pack(side='right', padx=5)

    def create_user(self, username, password, confirm_password, email, role, window):
        try:
            # Validate inputs
            if not all([username, password, confirm_password, email, role]):
                raise ValueError("All fields are required")
            
            if password != confirm_password:
                raise ValueError("Passwords do not match")
            
            if not self.validate_email(email):
                raise ValueError("Invalid email format")
            
            # Check if username exists
            self.cursor.execute(
                "SELECT COUNT(*) FROM Users WHERE username = %s",
                (username,)
            )
            if self.cursor.fetchone()[0] > 0:
                raise ValueError("Username already exists")
            
            # Create user
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute("""
                INSERT INTO Users (username, password, role, email)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed, role, email))
            
            self.db.commit()
            messagebox.showinfo("Success", "User created successfully!")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_password_reset(self):
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("400x500")
        reset_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(reset_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Use tk.Label
        tk.Label(
            main_frame,
            text="Reset Password",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Username*", "username"),
            ("Email*", "email"),
            ("New Password*", "password"),
            ("Confirm Password*", "confirm")
        ]
        
        entries = {}
        for label, key in fields:
            field_frame = ttk.Frame(main_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=10)
            
            # Use tk.Label
            tk.Label(
                field_frame,
                text=label,
                font=('Segoe UI', 16),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                pady=10
            ).pack(anchor='w')
            
            entry = ttk.Entry(
                field_frame,
                style='Modern.TEntry',
                show="•" if 'password' in key else ""
            )
            entry.pack(fill='x', pady=(5, 0))
            entries[key] = entry
        
        ttk.Button(
            main_frame,
            text="Reset Password",
            style='Modern.TButton',
            command=lambda: self.reset_password(
                entries['username'].get(),
                entries['email'].get(),
                entries['password'].get(),
                entries['confirm'].get(),
                reset_window
            )
        ).pack(fill='x', pady=20)

    def reset_password(self, username, email, password, confirm, window):
        try:
            if not all([username, email, password, confirm]):
                raise ValueError("All fields are required")
            
            if password != confirm:
                raise ValueError("Passwords do not match")
            
            if not self.validate_email(email):
                raise ValueError("Invalid email format")
            
            # Verify user exists and email matches
            self.cursor.execute(
                "SELECT id FROM Users WHERE username = %s AND email = %s",
                (username, email)
            )
            
            if not self.cursor.fetchone():
                raise ValueError("Invalid username or email")
            
            # Update password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute(
                "UPDATE Users SET password = %s WHERE username = %s",
                (hashed, username)
            )
            
            self.db.commit()
            messagebox.showinfo("Success", "Password reset successfully!")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_report(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Report")
        report_window.geometry("800x800")  # Made taller to accommodate calendars
        report_window.configure(bg=self.colors['bg_dark'])
        
        main_frame = ttk.Frame(report_window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Use tk.Label
        tk.Label(
            main_frame,
            text="Generate Report",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            pady=20
        ).pack(pady=(0, 20))
        
        # Date range selection
        date_frame = ttk.Frame(main_frame, style='Card.TFrame')
        date_frame.pack(fill='x', pady=10)
        
        # Use tk.Label
        tk.Label(
            date_frame,
            text="Date Range",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w', padx=20)
        
        # Calendar container
        calendars_frame = ttk.Frame(date_frame, style='Card.TFrame')
        calendars_frame.pack(fill='x', padx=20, pady=10)
        
        # Start date
        start_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        start_frame.pack(side='left', padx=10)
        
        # Use tk.Label
        tk.Label(
            start_frame,
            text="From:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()
        
        start_date = ModernCalendar(
            start_frame,
            self.colors
        )
        start_date.pack()
        
        # End date
        end_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        end_frame.pack(side='left', padx=10)
        
        # Use tk.Label
        tk.Label(
            end_frame,
            text="To:",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()
        
        end_date = ModernCalendar(
            end_frame,
            self.colors
        )
        end_date.pack()
        
        # Report type selection
        report_frame = ttk.Frame(main_frame, style='Card.TFrame')
        report_frame.pack(fill='x', pady=20)
        
        # Use tk.Label
        tk.Label(
            report_frame,
            text="Report Type",
            font=('Segoe UI', 16),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack(anchor='w', padx=20)
        
        report_var = tk.StringVar(value="donation")
        for report_type, label in [
            ("donation", "Donation Report"),
            ("inventory", "Inventory Report"),
            ("requests", "Requests Report"),
            ("users", "Users Activity Report")
        ]:
            ttk.Radiobutton(
                report_frame,
                text=label,
                variable=report_var,
                value=report_type,
                style='Modern.TRadiobutton'
            ).pack(anchor='w', padx=40, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Generate PDF",
            style='Modern.TButton',
            command=lambda: self.generate_pdf_report(
                start_date, 
                end_date,
                report_var.get()
            )
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Export to Excel",
            style='Modern.TButton',
            command=lambda: self.export_excel_report(
                start_date,
                end_date,
                report_var.get()
            )
        ).pack(side='right', padx=5)

    def generate_pdf_report(self, start_date, end_date, report_type):
        start_date = start_date.get_date()  # Get date from ModernCalendar
        end_date = end_date.get_date()      # Get date from ModernCalendar
        
        try:
            # Create a reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                
            # Generate filename with full path
            filename = os.path.join(reports_dir, f"{report_type}_report_{start_date}_to_{end_date}.txt")
            
            # Fetch data based on report type
            if report_type == "donation":
                self.cursor.execute("""
                    SELECT d.name, d.blood_group, d.donation_date, d.contact_info
                    FROM Donors d
                    WHERE d.donation_date BETWEEN %s AND %s
                    ORDER BY d.donation_date
                """, (start_date, end_date))
                
                data = self.cursor.fetchall()
                
                # Write to a text file (simplified version of a PDF)
                with open(filename, 'w') as file:
                    file.write(f"Blood Bank Management System - Donation Report\n")
                    file.write(f"Report Period: {start_date} to {end_date}\n")
                    file.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write("-" * 80 + "\n\n")
                    file.write("{:<30} {:<10} {:<15} {:<25}\n".format(
                        "Donor Name", "Blood Type", "Donation Date", "Contact"))
                    file.write("-" * 80 + "\n")
                    
                    for row in data:
                        date_str = row[2].strftime("%Y-%m-%d")
                        file.write("{:<30} {:<10} {:<15} {:<25}\n".format(
                            row[0], row[1], date_str, row[3]))
                    
                    file.write("\n" + "-" * 80 + "\n")
                    file.write(f"Total Donations: {len(data)}\n")
                    
            elif report_type == "inventory":
                self.cursor.execute("""
                    SELECT blood_group, units_available, last_updated
                    FROM BloodBank
                    ORDER BY blood_group
                """)
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w') as file:
                    file.write(f"Blood Bank Management System - Inventory Report\n")
                    file.write(f"Report Period: {start_date} to {end_date}\n")
                    file.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write("-" * 80 + "\n\n")
                    file.write("{:<15} {:<20} {:<30}\n".format(
                        "Blood Type", "Units Available", "Last Updated"))
                    file.write("-" * 80 + "\n")
                    
                    total_units = 0
                    for row in data:
                        update_str = row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "N/A"
                        file.write("{:<15} {:<20} {:<30}\n".format(
                            row[0], row[1], update_str))
                        total_units += row[1]
                    
                    file.write("\n" + "-" * 80 + "\n")
                    file.write(f"Total Blood Units Available: {total_units}\n")
            
            elif report_type == "requests":
                self.cursor.execute("""
                    SELECT hospital_name, blood_group, units_requested, request_date, 
                        priority, status, notes
                    FROM Requests
                    WHERE request_date BETWEEN %s AND %s
                    ORDER BY request_date DESC
                """, (start_date, end_date))
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w') as file:
                    file.write(f"Blood Bank Management System - Blood Requests Report\n")
                    file.write(f"Report Period: {start_date} to {end_date}\n")
                    file.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write("-" * 100 + "\n\n")
                    file.write("{:<30} {:<10} {:<10} {:<15} {:<15} {:<15}\n".format(
                        "Hospital", "Blood Type", "Units", "Date", "Priority", "Status"))
                    file.write("-" * 100 + "\n")
                    
                    total_requests = 0
                    approved_count = 0
                    pending_count = 0
                    rejected_count = 0
                    
                    for row in data:
                        date_str = row[3].strftime("%Y-%m-%d")
                        file.write("{:<30} {:<10} {:<10} {:<15} {:<15} {:<15}\n".format(
                            row[0], row[1], row[2], date_str, row[4], row[5]))
                        
                        if row[6]:  # Notes
                            file.write(f"Notes: {row[6]}\n")
                            file.write("-" * 100 + "\n")
                        
                        total_requests += 1
                        if row[5] == 'Approved':
                            approved_count += 1
                        elif row[5] == 'Pending':
                            pending_count += 1
                        elif row[5] == 'Rejected':
                            rejected_count += 1
                    
                    file.write("\n" + "-" * 100 + "\n")
                    file.write(f"Total Requests: {total_requests}\n")
                    file.write(f"Approved: {approved_count}\n")
                    file.write(f"Pending: {pending_count}\n")
                    file.write(f"Rejected: {rejected_count}\n")
                    
            elif report_type == "users":
                self.cursor.execute("""
                    SELECT username, role, email, last_login, created_at
                    FROM Users
                    ORDER BY created_at DESC
                """)
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w') as file:
                    file.write(f"Blood Bank Management System - Users Activity Report\n")
                    file.write(f"Report Period: {start_date} to {end_date}\n")
                    file.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write("-" * 100 + "\n\n")
                    file.write("{:<20} {:<15} {:<30} {:<20} {:<20}\n".format(
                        "Username", "Role", "Email", "Last Login", "Created At"))
                    file.write("-" * 100 + "\n")
                    
                    for row in data:
                        last_login = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "Never"
                        created_at = row[4].strftime("%Y-%m-%d %H:%M") if row[4] else "Unknown"
                        
                        file.write("{:<20} {:<15} {:<30} {:<20} {:<20}\n".format(
                            row[0], row[1], row[2], last_login, created_at))
                    
                    file.write("\n" + "-" * 100 + "\n")
                    file.write(f"Total Users: {len(data)}\n")
            
            # Open the generated file
            os.startfile(filename) if os.name == 'nt' else os.system(f'xdg-open "{filename}"')
            
            messagebox.showinfo("Report Generated", f"Report saved to {filename}\nThe file has been opened for you.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")


    def export_excel_report(self, start_date, end_date, report_type):
        start_date = start_date.get_date()  # Get date from ModernCalendar
        end_date = end_date.get_date()      # Get date from ModernCalendar
        
        try:
            # Create a reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                
            # Generate filename with full path
            filename = os.path.join(reports_dir, f"{report_type}_report_{start_date}_to_{end_date}.csv")
            
            # Fetch data based on report type
            if report_type == "donation":
                self.cursor.execute("""
                    SELECT d.name, d.blood_group, d.donation_date, d.contact_info, d.email,
                        ds.time_slot, ds.status
                    FROM Donors d
                    LEFT JOIN DonationSchedule ds ON d.id = ds.donor_id
                    WHERE d.donation_date BETWEEN %s AND %s
                    ORDER BY d.donation_date
                """, (start_date, end_date))
                
                data = self.cursor.fetchall()
                
                # Write to a CSV file (Excel compatible)
                with open(filename, 'w', newline='') as file:
                    file.write("Name,Blood Group,Donation Date,Contact,Email,Time Slot,Status\n")
                    
                    for row in data:
                        # Format date
                        date_str = row[2].strftime("%Y-%m-%d") if row[2] else ""
                        email = row[4] if row[4] else ""
                        time_slot = row[5] if row[5] else ""
                        status = row[6] if row[6] else ""
                        
                        file.write(f'"{row[0]}","{row[1]}","{date_str}","{row[3]}","{email}","{time_slot}","{status}"\n')
                        
            elif report_type == "inventory":
                self.cursor.execute("""
                    SELECT blood_group, units_available, last_updated
                    FROM BloodBank
                    ORDER BY blood_group
                """)
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w', newline='') as file:
                    file.write("Blood Group,Units Available,Last Updated\n")
                    
                    for row in data:
                        update_str = row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else ""
                        file.write(f'"{row[0]}",{row[1]},"{update_str}"\n')
            
            elif report_type == "requests":
                self.cursor.execute("""
                    SELECT hospital_name, blood_group, units_requested, request_date, 
                        priority, status, notes, created_at
                    FROM Requests
                    WHERE request_date BETWEEN %s AND %s
                    ORDER BY request_date DESC
                """, (start_date, end_date))
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w', newline='') as file:
                    file.write("Hospital,Blood Group,Units,Request Date,Priority,Status,Notes,Created At\n")
                    
                    for row in data:
                        date_str = row[3].strftime("%Y-%m-%d") if row[3] else ""
                        created_str = row[7].strftime("%Y-%m-%d %H:%M:%S") if row[7] else ""
                        notes = row[6].replace('"', '""') if row[6] else ""  # Escape quotes for CSV
                        
                        file.write(f'"{row[0]}","{row[1]}",{row[2]},"{date_str}","{row[4]}","{row[5]}","{notes}","{created_str}"\n')
            
            elif report_type == "users":
                self.cursor.execute("""
                    SELECT username, role, email, last_login, created_at
                    FROM Users
                    ORDER BY created_at DESC
                """)
                
                data = self.cursor.fetchall()
                
                with open(filename, 'w', newline='') as file:
                    file.write("Username,Role,Email,Last Login,Created At\n")
                    
                    for row in data:
                        last_login = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "Never"
                        created_at = row[4].strftime("%Y-%m-%d %H:%M") if row[4] else ""
                        
                        file.write(f'"{row[0]}","{row[1]}","{row[2]}","{last_login}","{created_at}"\n')
            
            # Open the generated file with default spreadsheet application
            os.startfile(filename) if os.name == 'nt' else os.system(f'xdg-open "{filename}"')
            
            messagebox.showinfo("Report Exported", f"Report exported to {filename}\nThe file has been opened for you.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def logout(self):
        self.current_user = None
        self.show_login_screen()
    
    def run(self):
        """Start the Tkinter main event loop"""
        self.root.mainloop()
    
if __name__ == "__main__":
    try:
        app = ModernBloodBankSystem()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Application Error",
            f"An error occurred while starting the application: {str(e)}"
        )