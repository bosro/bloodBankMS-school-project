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

        # Previous month button
        self.prev_btn = ttk.Label(
            nav_frame,
            text="◀",
            background=self.colors['card_bg'],
            foreground=self.colors['accent'],
            font=('Segoe UI', 10),
            cursor="hand2"
        )
        self.prev_btn.pack(side='left', padx=10)
        self.prev_btn.bind('<Button-1>', lambda e: self.change_month(-1))

        # Month and year label
        self.header_label = ttk.Label(
            nav_frame,
            text=self.selected_date.strftime("%B %Y"),
            background=self.colors['card_bg'],
            foreground=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        self.header_label.pack(side='left', expand=True)

        # Next month button
        self.next_btn = ttk.Label(
            nav_frame,
            text="▶",
            background=self.colors['card_bg'],
            foreground=self.colors['accent'],
            font=('Segoe UI', 10),
            cursor="hand2"
        )
        self.next_btn.pack(side='right', padx=10)
        self.next_btn.bind('<Button-1>', lambda e: self.change_month(1))

        # Weekday headers
        days_frame = ttk.Frame(self, style='Card.TFrame')
        days_frame.pack(fill='x', pady=5)

        for i, day in enumerate(['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']):
            ttk.Label(
                days_frame,
                text=day,
                background=self.colors['card_bg'],
                foreground=self.colors['text_secondary'],
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

                date_label = ttk.Label(
                    date_frame,
                    text=str(day),
                    background=bg_color,
                    foreground=fg_color,
                    font=('Segoe UI', 10),
                    padding=5,
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

    def configure_custom_styles(self):
        # Modern frame styles
        self.style.configure('Modern.TFrame', 
                           background=self.colors['bg_dark'])
        
        self.style.configure('Card.TFrame', 
                           background=self.colors['card_bg'],
                           relief='flat')
        
        self.style.configure('DateEntry',
                            fieldbackground=self.colors['bg_light'],
                            selectbackground=self.colors['accent'],
                            arrowcolor=self.colors['text'])

        # Modern button styles
        self.style.configure('Modern.TButton',
                           background=self.colors['accent'],
                           foreground=self.colors['text'],
                           padding=(30, 15),
                           font=('Segoe UI', 11),
                           borderwidth=0)
        
        self.style.map('Modern.TButton',
                      background=[('active', self.colors['accent_hover'])])
        
        # Secondary button style
        self.style.configure('Secondary.TButton',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text'],
                           padding=(30, 15),
                           font=('Segoe UI', 11),
                           borderwidth=0)
        
        # Header styles
        self.style.configure('Header.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 32, 'bold'),
                           padding=(0, 20))
        
        self.style.configure('Subheader.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 16),
                           padding=(0, 10))
        
        # Card header style
        self.style.configure('CardHeader.TLabel',
                           background=self.colors['card_bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 18, 'bold'),
                           padding=(20, 10))
        
        # Modern entry style
        self.style.configure('Modern.TEntry',
                           fieldbackground=self.colors['bg_light'],
                           foreground=self.colors['text'],
                           padding=(15, 10))
        
        # Treeview styling
        self.style.configure('Treeview',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['bg_light'],
                           borderwidth=0)
        
        self.style.configure('Treeview.Heading',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text'],
                           padding=(10, 5))
        
        # Combobox styling
        self.style.configure('TCombobox',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text'],
                           selectbackground=self.colors['accent'])

    def init_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="bloodbank_user",
                password="BloodBank@123",
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
        
        # Modern logo/header
        logo_label = ttk.Label(
            login_frame,
            text="🩸",  # Blood drop emoji
            font=('Segoe UI', 48),
            background=self.colors['card_bg'],
            foreground=self.colors['accent']
        )
        logo_label.pack(pady=(40, 0))
        
        title = ttk.Label(
            login_frame,
            text="Blood Bank",
            style='Header.TLabel'
        )
        title.pack(pady=(0, 10))
        
        subtitle = ttk.Label(
            login_frame,
            text="Management System",
            style='Subheader.TLabel'
        )
        subtitle.pack(pady=(0, 40))
        
        # Modern login form
        form_frame = ttk.Frame(login_frame, style='Card.TFrame')
        form_frame.pack(padx=60, pady=20)
        
        # Username field with icon
        username_frame = ttk.Frame(form_frame, style='Card.TFrame')
        username_frame.pack(fill='x', pady=(0, 20))
        
        username_icon = ttk.Label(
            username_frame,
            text="👤",  # User icon
            font=('Segoe UI', 16),
            background=self.colors['card_bg'],
            foreground=self.colors['text_secondary']
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
        
        password_icon = ttk.Label(
            password_frame,
            text="🔒",  # Lock icon
            font=('Segoe UI', 16),
            background=self.colors['card_bg'],
            foreground=self.colors['text_secondary']
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
        
        # Show/Hide password toggle
        self.password_visible = False
        toggle_btn = ttk.Label(
            password_frame,
            text="👁️",  # Eye icon
            font=('Segoe UI', 16),
            background=self.colors['card_bg'],
            foreground=self.colors['text_secondary'],
            cursor="hand2"
        )
        toggle_btn.pack(side='right', padx=(10, 0))
        toggle_btn.bind('<Button-1>', lambda e: self.toggle_password_visibility(password_entry, toggle_btn))
        
        # Error message label (hidden by default)
        self.error_label = ttk.Label(
            form_frame,
            text="",
            foreground=self.colors['error'],
            background=self.colors['card_bg'],
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
        divider_frame = ttk.Frame(form_frame, height=1, style='Card.TFrame')
        divider_frame.pack(fill='x', pady=20)
        divider_frame.configure(background=self.colors['border'])
        
        # Forgot password link
        forgot_password = ttk.Label(
            form_frame,
            text="Forgot Password?",
            foreground=self.colors['accent'],
            background=self.colors['card_bg'],
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
                # Update last login
                self.cursor.execute(
                    "UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                    (username,)
                )
                self.db.commit()
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
        if not self.current_user:
            self.show_login_screen()
            return

        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create main layout with sidebar and content area
        self.setup_dashboard_layout()
        
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
        
        # User avatar
        ttk.Label(
            profile_frame,
            text="👤",  # User icon
            font=('Segoe UI', 32),
            background=self.colors['card_bg'],
            foreground=self.colors['text']
        ).pack(pady=(20, 10))
        
        # Username
        ttk.Label(
            profile_frame,
            text=self.current_user['username'],
            style='Subheader.TLabel'
        ).pack(pady=(0, 5))
        
        # Role badge
        role_frame = ttk.Frame(profile_frame, style='Card.TFrame')
        role_frame.pack(pady=(0, 20))
        
        role_label = ttk.Label(
            role_frame,
            text=f"🔰 {self.current_user['role'].title()}",
            background=self.colors['accent'],
            foreground=self.colors['text'],
            font=('Segoe UI', 10),
            padding=(10, 5)
        )
        role_label.pack()

    def create_navigation_menu(self, parent):
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard, "Home dashboard"),
            ("➕ New Donor", self.show_donor_registration, "Register new donors"),
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
        
        # Welcome message
        ttk.Label(
            header_frame,
            text=f"Welcome back, {self.current_user['username']}!",
            style='Header.TLabel'
        ).pack(side='left')
        
        # Date and time
        time_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        time_frame.pack(side='right')
        
        current_time = datetime.now().strftime("%d %B %Y, %H:%M")
        ttk.Label(
            time_frame,
            text=f"🕒 {current_time}",
            style='Subheader.TLabel'
        ).pack()

    def create_quick_stats(self, parent):
        stats_frame = ttk.Frame(parent, style='Modern.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Fetch statistics
        self.cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM Donors WHERE DATE(donation_date) = CURDATE()) as today_donations,
                (SELECT COUNT(*) FROM Requests WHERE DATE(request_date) = CURDATE()) as today_requests,
                (SELECT COUNT(*) FROM BloodBank WHERE units_available < 10) as low_inventory,
                (SELECT COUNT(*) FROM Requests WHERE status = 'Pending') as pending_requests
        """)
        stats = self.cursor.fetchone()
        
        # Create stat cards
        stat_cards = [
            ("Today's Donations", stats[0], "💉", self.colors['success']),
            ("Today's Requests", stats[1], "📝", self.colors['warning']),
            ("Low Inventory Alert", stats[2], "⚠️", self.colors['error']),
            ("Pending Requests", stats[3], "⏳", self.colors['accent'])
        ]
        
        for i, (label, value, icon, color) in enumerate(stat_cards):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            
            # Icon
            ttk.Label(
                card,
                text=icon,
                font=('Segoe UI', 24),
                foreground=color,
                background=self.colors['card_bg']
            ).pack(pady=(20, 5))
            
            # Value
            ttk.Label(
                card,
                text=str(value),
                font=('Segoe UI', 36, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['card_bg']
            ).pack()
            
            # Label
            ttk.Label(
                card,
                text=label,
                font=('Segoe UI', 12),
                foreground=self.colors['text_secondary'],
                background=self.colors['card_bg']
            ).pack(pady=(5, 20))
        
        # Configure grid weights
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(
                tooltip,
                text=text,
                background=self.colors['bg_dark'],
                foreground=self.colors['text'],
                font=('Segoe UI', 9),
                padding=(10, 5)
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
        
        ttk.Label(
            header_frame,
            text="Blood Inventory",
            style='Header.TLabel'
        ).pack(side='left')
        
        # Refresh button
        ttk.Button(
            header_frame,
            text="🔄 Refresh",
            style='Secondary.TButton',
            command=lambda: self.refresh_inventory()
        ).pack(side='right')
        
        # Grid layout for blood type cards
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i, blood_type in enumerate(blood_types):
            self.create_blood_type_card(inventory_frame, blood_type, i)
        
        # Configure grid weights
        for i in range(4):
            inventory_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            inventory_frame.grid_rowconfigure(i, weight=1)

    def create_blood_type_card(self, parent, blood_type, index):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.grid(row=index//4, column=index%4, padx=10, pady=10, sticky='nsew')
        
        # Get inventory data
        self.cursor.execute(
            "SELECT units_available FROM BloodBank WHERE blood_group = %s",
            (blood_type,)
        )
        units = self.cursor.fetchone()[0]
        
        # Blood type label
        ttk.Label(
            card,
            text=blood_type,
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['accent'],
            background=self.colors['card_bg']
        ).pack(pady=(20, 10))
        
        # Units display
        ttk.Label(
            card,
            text=str(units),
            font=('Segoe UI', 36, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['card_bg']
        ).pack()
        
        ttk.Label(
            card,
            text="units available",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary'],
            background=self.colors['card_bg']
        ).pack(pady=(0, 20))
        
        # Status indicator
        status_frame = ttk.Frame(card, style='Card.TFrame')
        status_frame.pack(pady=(0, 20))
        
        status_color = self.get_status_color(units)
        status_text = self.get_status_text(units)
        
        ttk.Label(
            status_frame,
            text=status_text,
            background=status_color,
            foreground=self.colors['text'],
            font=('Segoe UI', 10),
            padding=(10, 5)
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
        for widget in self.main_container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_name() != 'sidebar':
                widget.destroy()
        self.show_blood_inventory(self.main_container)
        
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
        
        ttk.Label(
            header_frame,
            text="🩸 New Donor Registration",
            style='Header.TLabel'
        ).pack(side='left')
        
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

    def create_personal_info_tab(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create scrollable canvas
        canvas = tk.Canvas(
            frame,
            background=self.colors['card_bg'],
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
            
            ttk.Label(
                field_frame,
                text=label_text,
                style='Subheader.TLabel'
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
            
            ttk.Label(
                question_frame,
                text=question,
                style='Subheader.TLabel'
            ).pack(side='left', pady=5)
            
            ttk.Checkbutton(
                question_frame,
                variable=var,
                style='Modern.TCheckbutton'
            ).pack(side='right')
            
            # Add separator
            if i < len(questions) - 1:
                separator = ttk.Frame(frame, height=1, style='Card.TFrame')
                separator.pack(fill='x', padx=20)
                separator.configure(background=self.colors['border'])
        
        # Additional health notes
        notes_frame = ttk.Frame(frame, style='Card.TFrame')
        notes_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(
            notes_frame,
            text="Additional Health Notes",
            style='Subheader.TLabel'
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
        
        ttk.Label(
            date_frame,
            text="Preferred Donation Date",
            style='Subheader.TLabel'
        ).pack(anchor='w')
        
        # Replace DateEntry with ModernCalendar
        calendar_container = ttk.Frame(date_frame, style='Card.TFrame')
        calendar_container.pack(pady=(5, 0))
        
        self.date_entry = ModernCalendar(
            calendar_container,
            self.colors
        )
        self.date_entry.pack(fill='x')

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
                
                self.db.commit()
                messagebox.showinfo("Success", "Donor registered successfully!")
                window.destroy()
                
            except Exception as e:
                self.db.rollback()
                raise Exception(f"Failed to save donor: {str(e)}")
        def show_blood_requests(self):
            for widget in self.main_container.winfo_children():
                widget.destroy()
                
            main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
            main_frame.pack(fill='both', expand=True)
            
            # Header with stats
            self.create_request_header(main_frame)
            
            # Filters and search
            filter_frame = self.create_request_filters(main_frame)
            filter_frame.pack(fill='x', pady=(0, 20))
            
            # Request list
            self.create_request_list(main_frame)

        def create_request_header(self, parent):
            header_frame = ttk.Frame(parent, style='Modern.TFrame')
            header_frame.pack(fill='x', pady=(0, 20))
            
            # Title
            ttk.Label(
                header_frame,
                text="Blood Requests",
                style='Header.TLabel'
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
                
                ttk.Label(
                    card,
                    text=f"{icon} {value}",
                    font=('Segoe UI', 20, 'bold'),
                    foreground=color,
                    background=self.colors['card_bg']
                ).pack(pady=(10, 5))
                
                ttk.Label(
                    card,
                    text=label,
                    font=('Segoe UI', 10),
                    foreground=self.colors['text_secondary'],
                    background=self.colors['card_bg']
                ).pack(pady=(0, 10))
            
            stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

        def create_request_filters(self, parent):
            filter_frame = ttk.Frame(parent, style='Card.TFrame')
            
            # Status filter
            status_frame = ttk.Frame(filter_frame, style='Card.TFrame')
            status_frame.pack(side='left', padx=20, pady=10)
            
            self.status_var = tk.StringVar(value='All')
            
            ttk.Label(
                status_frame,
                text="Status:",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                search_frame,
                text="🔍",
                font=('Segoe UI', 12),
                background=self.colors['card_bg']
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
            
            search_pattern = f"%{search_term}%"
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
            
            # Header
            ttk.Label(
                main_frame,
                text=f"Request #{request_id}",
                style='Header.TLabel'
            ).pack(pady=(0, 20))
            
            # Create details card
            self.create_request_detail_card(main_frame, request)
            
            # Create action buttons
            self.create_request_action_buttons(main_frame, request)

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
                
                ttk.Label(
                    detail_frame,
                    text=label,
                    style='Subheader.TLabel'
                ).pack(side='left')
                
                value_color = self.get_value_color(label, value)
                
                ttk.Label(
                    detail_frame,
                    text=str(value),
                    font=('Segoe UI', 12, 'bold'),
                    foreground=value_color,
                    background=self.colors['card_bg']
                ).pack(side='right')
            
            if request[7]:  # Notes
                notes_frame = ttk.Frame(card, style='Card.TFrame')
                notes_frame.pack(fill='x', padx=20, pady=10)
                
                ttk.Label(
                    notes_frame,
                    text="Notes:",
                    style='Subheader.TLabel'
                ).pack(anchor='w')
                
                ttk.Label(
                    notes_frame,
                    text=request[7],
                    wraplength=500,
                    font=('Segoe UI', 11),
                    foreground=self.colors['text'],
                    background=self.colors['card_bg']
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
            # Implement printing functionality
            messagebox.showinfo("Print", "Printing request details...")
            
        def show_analytics(self):
            for widget in self.main_container.winfo_children():
                widget.destroy()
                
            main_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
            main_frame.pack(fill='both', expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
            header_frame.pack(fill='x', pady=(0, 20))
            
            ttk.Label(
                header_frame,
                text="Analytics Dashboard",
                style='Header.TLabel'
            ).pack(side='left')
            
            # Create date range selector
            date_range_frame = ttk.Frame(header_frame, style='Card.TFrame')
            date_range_frame.pack(side='right')
            
            ttk.Label(
                date_range_frame,
                text="Date Range:",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                frame,
                text="Donation Trends",
                style='CardHeader.TLabel'
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
            
            ttk.Label(
                frame,
                text="Blood Type Distribution",
                style='CardHeader.TLabel'
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
            
            ttk.Label(
                frame,
                text="Request Status Distribution",
                style='CardHeader.TLabel'
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
            
            ttk.Label(
                frame,
                text="Current Inventory Levels",
                style='CardHeader.TLabel'
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

        def update_analytics(self, event=None):
            self.show_analytics()

        def show_settings(self):
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Settings")
            settings_window.geometry("800x600")
            settings_window.configure(bg=self.colors['bg_dark'])
            
            main_frame = ttk.Frame(settings_window, style='Modern.TFrame')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Header
            ttk.Label(
                main_frame,
                text="System Settings",
                style='Header.TLabel'
            ).pack(pady=(0, 30))
            
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
                
                ttk.Label(
                    section_frame,
                    text=f"{icon} {title}",
                    style='Subheader.TLabel'
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
            
            # Header
            ttk.Label(
                main_frame,
                text="New Blood Donation",
                style='Header.TLabel'
            ).pack(pady=(0, 20))
            
            # Form
            form_frame = ttk.Frame(main_frame, style='Card.TFrame')
            form_frame.pack(fill='x', pady=10)
            
            # Blood type selection
            blood_type_frame = ttk.Frame(form_frame, style='Card.TFrame')
            blood_type_frame.pack(fill='x', padx=20, pady=10)
            
            ttk.Label(
                blood_type_frame,
                text="Blood Type*",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                units_frame,
                text="Units*",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                donor_frame,
                text="Donor Selection",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                notes_frame,
                text="Additional Notes",
                style='Subheader.TLabel'
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
            
            ttk.Label(
                progress_window,
                text="Creating Database Backup...",
                style='Subheader.TLabel'
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
        
        ttk.Label(
            main_frame,
            text="Notification Settings",
            style='Header.TLabel'
        ).pack(pady=(0, 20))
        
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
            
            ttk.Label(
                option_frame,
                text=label,
                style='Subheader.TLabel'
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
        
        ttk.Label(
            main_frame,
            text="Theme Settings",
            style='Header.TLabel'
        ).pack(pady=(0, 20))
        
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
        
        ttk.Label(
            main_frame,
            text="System Logs",
            style='Header.TLabel'
        ).pack(pady=(0, 20))
        
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
        
        ttk.Label(
            header_frame,
            text="User Management",
            style='Header.TLabel'
        ).pack(side='left')
        
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
        # Implementation will be in the next part
        pass

    def show_password_reset(self):
        # Implementation will be in the next part
        pass

    def show_add_user_form(self):
            user_window = tk.Toplevel(self.root)
            user_window.title("Add New User")
            user_window.geometry("500x600")
            user_window.configure(bg=self.colors['bg_dark'])
            
            main_frame = ttk.Frame(user_window, style='Modern.TFrame')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            ttk.Label(
                main_frame,
                text="Add New User",
                style='Header.TLabel'
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
                
                ttk.Label(
                    field_frame,
                    text=label,
                    style='Subheader.TLabel'
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
            
            ttk.Label(
                role_frame,
                text="Role*",
                style='Subheader.TLabel'
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
        
        ttk.Label(
            main_frame,
            text="Reset Password",
            style='Header.TLabel'
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
            
            ttk.Label(
                field_frame,
                text=label,
                style='Subheader.TLabel'
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
        
        ttk.Label(
            main_frame,
            text="Generate Report",
            style='Header.TLabel'
        ).pack(pady=(0, 20))
        
        # Date range selection
        date_frame = ttk.Frame(main_frame, style='Card.TFrame')
        date_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            date_frame,
            text="Date Range",
            style='Subheader.TLabel'
        ).pack(anchor='w', padx=20)
        
        # Calendar container
        calendars_frame = ttk.Frame(date_frame, style='Card.TFrame')
        calendars_frame.pack(fill='x', padx=20, pady=10)
        
        # Start date
        start_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        start_frame.pack(side='left', padx=10)
        
        ttk.Label(
            start_frame,
            text="From:",
            style='Subheader.TLabel'
        ).pack()
        
        start_date = ModernCalendar(
            start_frame,
            self.colors
        )
        start_date.pack()
        
        # End date
        end_frame = ttk.Frame(calendars_frame, style='Card.TFrame')
        end_frame.pack(side='left', padx=10)
        
        ttk.Label(
            end_frame,
            text="To:",
            style='Subheader.TLabel'
        ).pack()
        
        end_date = ModernCalendar(
            end_frame,
            self.colors
        )
        end_date.pack()

    def generate_pdf_report(self, start_date, end_date, report_type):
        start_date = start_date.get_date()  # Get date from ModernCalendar
        end_date = end_date.get_date()      # Get date from ModernCalendar
        messagebox.showinfo(
            "Report Generation",
            f"Generating {report_type} PDF report for {start_date} to {end_date}"
        )


    def export_excel_report(self, start_date, end_date, report_type):
        start_date = start_date.get_date()  # Get date from ModernCalendar
        end_date = end_date.get_date()      # Get date from ModernCalendar
        messagebox.showinfo(
            "Report Export",
            f"Exporting {report_type} to Excel for {start_date} to {end_date}"
        )

if __name__ == "__main__":
    try:
        app = ModernBloodBankSystem()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Application Error",
            f"An error occurred while starting the application: {str(e)}"
        )