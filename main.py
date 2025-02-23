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

class BloodBankSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blood Bank Management System")
        self.root.geometry("1200x800")
        
        # Apply dark theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("equilux") 
        
        # Configure colors
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_light': '#2d2d2d',
            'accent': '#bb86fc',
            'text': '#ffffff',
            'error': '#cf6679',
            'success': '#03dac6'
        }
        
        self.colors.update({
            'chart_bg': '#2d2d2d',
            'grid': '#3d3d3d',
            'chart_text': '#ffffff'
        })
        
        self.current_user = None
        
        # Configure styles
        self.style.configure('Main.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Card.TFrame', background=self.colors['bg_light'])
        self.style.configure(
            'Custom.TButton',
            background=self.colors['accent'],
            foreground=self.colors['text'],
            padding=(20, 10),
            font=('Helvetica', 10)
        )
        self.style.configure(
            'Title.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            font=('Helvetica', 24, 'bold'),
            padding=(0, 20)
        )
        self.style.configure(
            'Subtitle.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            font=('Helvetica', 16),
            padding=(0, 10)
        )
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Initialize database connection
        self.init_database()
        
        # Setup admin account
        self.setup_admin()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize login screen
        self.show_login_screen()

    def init_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="bloodbank_user",
                password="BloodBank@123",
                database="blood_bank"
            )
            self.cursor = self.db.cursor()
            self.create_tables()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            self.root.quit()

    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS BloodBank (
                id INT AUTO_INCREMENT PRIMARY KEY,
                blood_group VARCHAR(5) NOT NULL,
                units_available INT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS Donors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                blood_group VARCHAR(5) NOT NULL,
                contact_info VARCHAR(100) NOT NULL,
                donation_date DATE NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS Requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital_name VARCHAR(100) NOT NULL,
                blood_group VARCHAR(5) NOT NULL,
                units_requested INT NOT NULL,
                request_date DATE NOT NULL,
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending'
            )""",
            """CREATE TABLE IF NOT EXISTS Users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'staff') NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS DonationSchedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                donor_id INT,
                scheduled_date DATE NOT NULL,
                time_slot VARCHAR(20) NOT NULL,
                status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
                FOREIGN KEY (donor_id) REFERENCES Donors(id)
            )""",
            """CREATE TABLE IF NOT EXISTS Inventory_Alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                blood_group VARCHAR(5) NOT NULL,
                alert_type ENUM('Low', 'Critical') NOT NULL,
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
                    "INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
                    ('admin', hashed, 'admin')
                )
            self.db.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup admin: {e}")

    def show_login_screen(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title = ttk.Label(
            login_frame,
            text="Blood Bank Management System",
            style='Title.TLabel'
        )
        title.pack(pady=20)
        
        # Login form
        form_frame = ttk.Frame(login_frame, style='Card.TFrame')
        form_frame.pack(padx=40, pady=20)
        
        # Username
        ttk.Label(
            form_frame,
            text="Username:",
            style='Subtitle.TLabel'
        ).pack(anchor='w')
        
        username_entry = ttk.Entry(
            form_frame,
            font=('Helvetica', 12),
            width=30
        )
        username_entry.pack(pady=(0, 20))
        
        # Password
        ttk.Label(
            form_frame,
            text="Password:",
            style='Subtitle.TLabel'
        ).pack(anchor='w')
        
        password_entry = ttk.Entry(
            form_frame,
            font=('Helvetica', 12),
            width=30,
            show="•"
        )
        password_entry.pack(pady=(0, 30))
        
        # Login button
        login_button = ttk.Button(
            form_frame,
            text="Login",
            style='Custom.TButton',
            command=lambda: self.validate_login(
                username_entry.get(),
                password_entry.get()
            )
        )
        login_button.pack(pady=(0, 20))
        
        # Forgot Password button
        forgot_password = ttk.Button(
            form_frame,
            text="Forgot Password?",
            style='Custom.TButton',
            command=self.show_password_reset
        )
        forgot_password.pack(pady=10)

    def validate_login(self, username, password):
        try:
            self.cursor.execute(
                "SELECT password, role FROM Users WHERE username = %s",
                (username,)
            )
            result = self.cursor.fetchone()
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                self.current_user = {'username': username, 'role': result[1]}
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def show_password_reset(self):
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("400x300")
        reset_window.configure(bg=self.colors['bg_dark'])
        
        frame = ttk.Frame(reset_window, style='Card.TFrame')
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        ttk.Label(frame, text="Username:", style='Subtitle.TLabel').pack(pady=5)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Email:", style='Subtitle.TLabel').pack(pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.pack(pady=5)
        
        ttk.Label(frame, text="New Password:", style='Subtitle.TLabel').pack(pady=5)
        password_entry = ttk.Entry(frame, width=30, show="•")
        password_entry.pack(pady=5)
        
        def reset_password():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            new_password = password_entry.get()
            
            if not all([username, email, new_password]):
                messagebox.showerror("Error", "All fields are required")
                return
                
            if not self.validate_email(email):
                messagebox.showerror("Error", "Invalid email format")
                return
                
            try:
                self.cursor.execute(
                    "UPDATE Users SET password = %s WHERE username = %s",
                    (bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()), username)
                )
                self.db.commit()
                messagebox.showinfo("Success", "Password reset successful")
                reset_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {e}")
        
        ttk.Button(
            frame,
            text="Reset Password",
            style='Custom.TButton',
            command=reset_password
        ).pack(pady=20)

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def show_dashboard(self):
        if not self.current_user:
            self.show_login_screen()
            return

        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create navigation frame
        nav_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        nav_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Donor Registration", self.show_donor_registration),
            ("Blood Requests", self.show_blood_requests),
            ("Analytics", self.show_analytics),
            ("Generate Report", self.generate_report),
            ("Donation History", self.show_donation_history),
            ("Logout", self.logout)
        ]
        
        for text, command in nav_buttons:
            ttk.Button(
                nav_frame,
                text=text,
                style='Custom.TButton',
                command=command
            ).pack(side='left', padx=5)

        # Main content area
        content_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True)
    
        # Blood inventory cards
        self.show_blood_inventory(content_frame)
        
        
    def show_blood_inventory(self, parent):
        # Grid layout for blood type cards
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i, blood_type in enumerate(blood_types):
            card = ttk.Frame(parent, style='Card.TFrame')
            card.grid(row=i//4, column=i%4, padx=10, pady=10, sticky='nsew')
            
            # Blood type label
            ttk.Label(
                card,
                text=blood_type,
                style='Title.TLabel'
            ).pack(pady=10)
            
            # Get units from database
            self.cursor.execute(
                "SELECT units_available FROM BloodBank WHERE blood_group = %s",
                (blood_type,)
            )
            result = self.cursor.fetchone()
            units = result[0] if result else 0
            
            ttk.Label(
                card,
                text=f"{units} units",
                style='Subtitle.TLabel'
            ).pack(pady=5)
            
            # Action buttons
            ttk.Button(
                card,
                text="Donate",
                style='Custom.TButton',
                command=lambda bt=blood_type: self.show_donation_form(bt)
            ).pack(pady=5)
            
            ttk.Button(
                card,
                text="Request",
                style='Custom.TButton',
                command=lambda bt=blood_type: self.show_request_form(bt)
            ).pack(pady=5)

    def show_donor_registration(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Donor Registration")
        registration_window.geometry("800x600")
        registration_window.configure(bg=self.colors['bg_dark'])
        
        notebook = ttk.Notebook(registration_window)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Personal Information
        personal_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(personal_frame, text='Personal Information')
        
        fields = [
            ("Name:", "name"),
            ("Age:", "age"),
            ("Blood Group:", "blood_group"),
            ("Contact:", "contact"),
            ("Address:", "address"),
            ("Email:", "email")
        ]
        
        entries = {}
        for i, (label_text, key) in enumerate(fields):
            ttk.Label(
                personal_frame,
                text=label_text,
                style='Subtitle.TLabel'
            ).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            if key == "blood_group":
                entry = ttk.Combobox(
                    personal_frame,
                    values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
                    state='readonly'
                )
            else:
                entry = ttk.Entry(personal_frame, width=30)
            
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='w')
            entries[key] = entry
        
        # Health Screening
        health_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(health_frame, text='Health Screening')
        
        questions = [
            "Have you donated blood in the last 3 months?",
            "Do you have any chronic diseases?",
            "Are you currently taking any medications?",
            "Have you had any recent surgeries?",
            "Have you had any recent infections?"
        ]
        
        health_vars = {}
        for i, question in enumerate(questions):
            var = tk.BooleanVar()
            health_vars[f"q{i}"] = var
            
            ttk.Label(
                health_frame,
                text=question,
                style='Subtitle.TLabel'
            ).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            ttk.Checkbutton(
                health_frame,
                variable=var,
                style='Custom.TCheckbutton'
            ).grid(row=i, column=1, padx=10, pady=5)
        
        # Scheduling
        schedule_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(schedule_frame, text='Scheduling')
        
        ttk.Label(
            schedule_frame,
            text="Preferred Donation Date:",
            style='Subtitle.TLabel'
        ).pack(pady=10)
        
        date_entry = DateEntry(
            schedule_frame,
            width=20,
            background=self.colors['accent'],
            foreground=self.colors['text']
        )
        date_entry.pack(pady=10)
        
        time_var = tk.StringVar()
        time_slots = [
            '09:00 AM', '10:00 AM', '11:00 AM',
            '02:00 PM', '03:00 PM', '04:00 PM'
        ]
        
        ttk.Label(
            schedule_frame,
            text="Preferred Time:",
            style='Subtitle.TLabel'
        ).pack(pady=10)
        
        time_combo = ttk.Combobox(
            schedule_frame,
            textvariable=time_var,
            values=time_slots,
            state='readonly'
        )
        time_combo.pack(pady=10)
        
        # Submit button
        def validate_and_save():
            try:
                # Validate personal information
                name = entries['name'].get().strip()
                age = int(entries['age'].get())
                blood_group = entries['blood_group'].get()
                contact = entries['contact'].get().strip()
                
                email = entries['email'].get().strip()
                if email and not self.validate_email(email):
                    raise ValueError("Invalid email format")
                
                if not all([name, age, blood_group, contact]):
                    raise ValueError("All required fields must be filled")
                
                if age < 18 or age > 65:
                    raise ValueError("Age must be between 18 and 65")
                
                # Check eligibility
                if health_vars['q0'].get():
                    raise ValueError("Cannot donate if donated in last 3 months")
                
                if any(health_vars[f"q{i}"].get() for i in range(1, 5)):
                    raise ValueError("Health conditions prevent donation")
                
                # Save donor information
                self.cursor.execute("""
                    INSERT INTO Donors (
                        name, age, blood_group, contact_info,
                        address, email, donation_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, age, blood_group, contact,
                    entries['address'].get(),
                    email,
                    date_entry.get_date()
                ))
                
                # Schedule donation
                self.cursor.execute("""
                    INSERT INTO DonationSchedule (
                        donor_id, scheduled_date, time_slot
                    ) VALUES (LAST_INSERT_ID(), %s, %s)
                """, (
                    date_entry.get_date(),
                    time_var.get()
                ))
                
                self.db.commit()
                messagebox.showinfo("Success", "Donor registered successfully!")
                registration_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.db.rollback()
        
        ttk.Button(
            schedule_frame,
            text="Register Donor",
            style='Custom.TButton',
            command=validate_and_save
        ).pack(pady=20)

    def show_request_form(self, blood_type):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Request {blood_type} Blood")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg_dark'])
        
        form_frame = ttk.Frame(dialog, style='Card.TFrame')
        form_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        ttk.Label(
            form_frame,
            text=f"Request {blood_type} Blood",
            style='Title.TLabel'
        ).pack(pady=20)
        
        fields = [
            ("Hospital Name:", "hospital"),
            ("Units Required:", "units")
        ]
        
        entries = {}
        for label_text, key in fields:
            ttk.Label(
                form_frame,
                text=label_text,
                style='Subtitle.TLabel'
            ).pack(anchor='w')
            
            entry = ttk.Entry(form_frame, width=30)
            entry.pack(pady=(0, 20))
            entries[key] = entry
        
        ttk.Button(
            form_frame,
            text="Submit Request",
            style='Custom.TButton',
            command=lambda: self.process_request(
                blood_type,
                entries,
                dialog
            )
        ).pack(pady=20)
        
    
    def process_request(self, blood_type, entries, dialog):
        try:
            hospital = entries['hospital'].get().strip()
            units = int(entries['units'].get())
            
            if not all([hospital, units]):
                raise ValueError("All fields are required")
            
            # Check availability
            self.cursor.execute(
                "SELECT units_available FROM BloodBank WHERE blood_group = %s",
                (blood_type,)
            )
            available = self.cursor.fetchone()[0]
            
            if units > available:
                raise ValueError(f"Only {available} units available")
            
            # Process request
            self.cursor.execute("""
                INSERT INTO Requests 
                (hospital_name, blood_group, units_requested, request_date, status)
                VALUES (%s, %s, %s, %s, 'Approved')
            """, (hospital, blood_type, units, date.today()))
            
            # Update inventory
            self.cursor.execute("""
                UPDATE BloodBank 
                SET units_available = units_available - %s 
                WHERE blood_group = %s
            """, (units, blood_type))
            
            self.db.commit()
            messagebox.showinfo("Success", "Blood request processed successfully!")
            dialog.destroy()
            self.show_dashboard()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process request: {str(e)}")
            self.db.rollback()

    def show_analytics(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        analytics_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        analytics_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create charts
        self.create_inventory_chart(analytics_frame)
        self.create_donation_trend_chart(analytics_frame)
        self.show_statistics(analytics_frame)

    def create_inventory_chart(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        self.cursor.execute("SELECT blood_group, units_available FROM BloodBank")
        data = self.cursor.fetchall()
        
        groups = [row[0] for row in data]
        units = [row[1] for row in data]
        
        ax.bar(groups, units, color=self.colors['accent'])
        ax.set_facecolor(self.colors['chart_bg'])
        ax.set_title('Blood Inventory', color=self.colors['chart_text'])
        ax.tick_params(colors=self.colors['chart_text'])
        ax.grid(True, color=self.colors['grid'])
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_donation_trend_chart(self, parent):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(side='right', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['chart_bg'])
        ax = fig.add_subplot(111)
        
        # Get last 7 days of donations
        self.cursor.execute("""
            SELECT DATE(donation_date), COUNT(*)
            FROM Donors
            WHERE donation_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(donation_date)
            ORDER BY donation_date
        """)
        data = self.cursor.fetchall()
        
        dates = [row[0] for row in data]
        counts = [row[1] for row in data]
        
        ax.plot(dates, counts, color=self.colors['accent'], marker='o')
        ax.set_facecolor(self.colors['chart_bg'])
        ax.set_title('Donation Trend (Last 7 Days)', color=self.colors['chart_text'])
        ax.tick_params(colors=self.colors['chart_text'])
        ax.grid(True, color=self.colors['grid'])
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_statistics(self, parent):
        stats_frame = ttk.Frame(parent, style='Card.TFrame')
        stats_frame.pack(fill='x', pady=20)
        
        # Get statistics
        self.cursor.execute("""
            SELECT 
                COUNT(DISTINCT d.id) as total_donors,
                COUNT(DISTINCT r.id) as total_requests,
                SUM(b.units_available) as total_units,
                COUNT(DISTINCT CASE WHEN r.status = 'Approved' THEN r.id END) as approved_requests
            FROM Donors d
            CROSS JOIN Requests r
            CROSS JOIN BloodBank b
        """)
        stats = self.cursor.fetchone()
        
        # Display statistics in grid
        stats_data = [
            ("Total Donors", stats[0]),
            ("Total Requests", stats[1]),
            ("Available Units", stats[2]),
            ("Approved Requests", stats[3])
        ]
        
        for i, (label, value) in enumerate(stats_data):
            card = ttk.Frame(stats_frame, style='Card.TFrame')
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(
                card,
                text=label,
                style='Subtitle.TLabel'
            ).pack(pady=5)
            
            ttk.Label(
                card,
                text=str(value),
                style='Title.TLabel'
            ).pack(pady=5)

    def generate_report(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Report")
        report_window.geometry("400x300")
        report_window.configure(bg=self.colors['bg_dark'])
        
        frame = ttk.Frame(report_window, style='Card.TFrame')
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        ttk.Label(
            frame,
            text="Report Duration",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # Date range selection
        start_date = DateEntry(frame, width=20)
        start_date.pack(pady=10)
        
        end_date = DateEntry(frame, width=20)
        end_date.pack(pady=10)
        
        ttk.Button(
            frame,
            text="Generate Report",
            style='Custom.TButton',
            command=lambda: self.create_report(start_date.get_date(), end_date.get_date())
        ).pack(pady=20)

    def create_report(self, start_date, end_date):
        # Query data for report
        self.cursor.execute("""
            SELECT 
                b.blood_group,
                COUNT(d.id) as donations,
                COUNT(r.id) as requests,
                b.units_available
            FROM BloodBank b
            LEFT JOIN Donors d ON b.blood_group = d.blood_group 
                AND d.donation_date BETWEEN %s AND %s
            LEFT JOIN Requests r ON b.blood_group = r.blood_group 
                AND r.request_date BETWEEN %s AND %s
            GROUP BY b.blood_group
        """, (start_date, end_date, start_date, end_date))
        
        data = self.cursor.fetchall()
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Report: {start_date} to {end_date}")
        report_window.geometry("800x600")
        report_window.configure(bg=self.colors['bg_dark'])
        
        frame = ttk.Frame(report_window, style='Card.TFrame')
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create Treeview
        columns = ('Blood Group', 'Donations', 'Requests', 'Available Units')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for row in data:
            tree.insert('', 'end', values=row)
        
        tree.pack(fill='both', expand=True, pady=20)
        
        # Export button
        ttk.Button(
            frame,
            text="Export to CSV",
            style='Custom.TButton',
            command=lambda: self.export_report(data)
        ).pack(pady=10)
        
        
    def show_donation_history(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # Title
        ttk.Label(
            self.main_container,
            text="Donation History",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # Date filter frame
        filter_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(
            filter_frame,
            text="From:",
            style='Subtitle.TLabel'
        ).pack(side='left', padx=5)
        
        start_date = DateEntry(
            filter_frame,
            width=12,
            background=self.colors['accent'],
            foreground=self.colors['text'],
            borderwidth=2
        )
        start_date.pack(side='left', padx=5)
        
        ttk.Label(
            filter_frame,
            text="To:",
            style='Subtitle.TLabel'
        ).pack(side='left', padx=5)
        
        end_date = DateEntry(
            filter_frame,
            width=12,
            background=self.colors['accent'],
            foreground=self.colors['text'],
            borderwidth=2
        )
        end_date.pack(side='left', padx=5)
        
        # Create Treeview
        columns = ('Name', 'Blood Group', 'Donation Date', 'Contact', 'Total Donations')
        tree = ttk.Treeview(
            self.main_container,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
        
        def update_history():
            tree.delete(*tree.get_children())
            
            query = """
                SELECT 
                    d.name,
                    d.blood_group,
                    d.donation_date,
                    d.contact_info,
                    COUNT(*) OVER (PARTITION BY d.id) as total_donations
                FROM Donors d
                WHERE d.donation_date BETWEEN %s AND %s
                ORDER BY d.donation_date DESC
            """
            
            self.cursor.execute(query, (
                start_date.get_date(),
                end_date.get_date()
            ))
            
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        # Update button
        ttk.Button(
            filter_frame,
            text="Update",
            style='Custom.TButton',
            command=update_history
        ).pack(side='left', padx=20)
        
        # Initial update
        update_history()

    def export_report(self, data):
        import csv
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Blood Group', 'Donations', 'Requests', 'Available Units'])
                writer.writerows(data)
            messagebox.showinfo("Success", "Report exported successfully!")

    def show_enhanced_dashboard(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # Quick Stats Panel
        stats_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM Donors WHERE DATE(donation_date) = CURDATE()) as today_donations,
                (SELECT COUNT(*) FROM Requests WHERE DATE(request_date) = CURDATE()) as today_requests,
                (SELECT COUNT(*) FROM BloodBank WHERE units_available < 10) as low_inventory
        """)
        today_stats = self.cursor.fetchone()
        
        stats = [
            ("Today's Donations", today_stats[0]),
            ("Today's Requests", today_stats[1]),
            ("Low Inventory Alerts", today_stats[2])
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_card = ttk.Frame(stats_frame, style='Card.TFrame')
            stat_card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            ttk.Label(
                stat_card,
                text=label,
                style='Subtitle.TLabel'
            ).pack(pady=5)
            
            ttk.Label(
                stat_card,
                text=str(value),
                style='Title.TLabel',
                foreground=self.colors['error'] if 'Low' in label and value > 0 else self.colors['text']
            ).pack(pady=5)
            
    
    def enhance_date_handling(self):
        # Get current date and time
        now = datetime.now()
        today = now.date()
        
        # Calculate important time ranges
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        three_months_ago = today - timedelta(days=90)
        
        # Check for expired donations (older than 42 days)
        expiry_date = today - timedelta(days=42)
        self.cursor.execute("""
            UPDATE BloodBank SET units_available = units_available - (
                SELECT COUNT(*) 
                FROM Donors 
                WHERE blood_group = BloodBank.blood_group 
                AND donation_date <= %s
            )
        """, (expiry_date,))
        
        # Create alerts for donations nearing expiry
        warning_date = today - timedelta(days=35)  # 1 week before expiry
        self.cursor.execute("""
            INSERT INTO Inventory_Alerts (blood_group, alert_type)
            SELECT DISTINCT blood_group, 'Critical'
            FROM Donors
            WHERE donation_date <= %s
            AND donation_date > %s
        """, (warning_date, expiry_date))
        
        self.db.commit()
    

    def show_blood_requests(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # Status filter frame
        filter_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        status_var = tk.StringVar(value='All')
        for status in ['All', 'Pending', 'Approved', 'Rejected']:
            ttk.Radiobutton(
                filter_frame,
                text=status,
                variable=status_var,
                value=status,
                command=lambda: self.update_requests_list(tree, status_var.get()),
                style='Custom.TRadiobutton'
            ).pack(side='left', padx=10)
        
        # Create Treeview for requests
        columns = ('ID', 'Hospital', 'Blood Group', 'Units', 'Date', 'Status')
        tree = ttk.Treeview(
            self.main_container,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Initial load
        self.update_requests_list(tree, 'All')

    def update_requests_list(self, tree, status_filter):
        tree.delete(*tree.get_children())
        
        query = """
            SELECT id, hospital_name, blood_group, units_requested, request_date, status
            FROM Requests
            WHERE status = %s OR %s = 'All'
            ORDER BY request_date DESC
        """
        
        self.cursor.execute(query, (status_filter, status_filter))
        
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BloodBankSystem()
    app.run()