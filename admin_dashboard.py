import customtkinter as ctk
import requests

# Set the theme to match a professional tech tool
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NexusAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nexus Admin Control Center")
        self.geometry("1100x600")

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NEXUS", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_resources = ctk.CTkButton(self.sidebar_frame, text="Resources/Studios", command=self.show_resources)
        self.btn_resources.grid(row=2, column=0, padx=20, pady=10)

        self.btn_users = ctk.CTkButton(self.sidebar_frame, text="User Management", command=self.show_users)
        self.btn_users.grid(row=3, column=0, padx=20, pady=10)

        # --- MAIN CONTENT AREA ---
        self.main_view = ctk.CTkFrame(self, corner_radius=10)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.status_label = ctk.CTkLabel(self.main_view, text="Welcome back, Admin.", font=ctk.CTkFont(size=20))
        self.status_label.pack(pady=20)

    # ==========================================
    #             DASHBOARD TAB
    # ==========================================
    def show_dashboard(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

        # Create two columns for the dashboard
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_columnconfigure(1, weight=1)

        # --- LEFT COLUMN: WEATHER STATION ---
        weather_frame = ctk.CTkFrame(self.main_view, corner_radius=10)
        weather_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(weather_frame, text="Barcelona Weather Status", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.weather_info = ctk.CTkLabel(weather_frame, text="Fetching...")
        self.weather_info.pack(pady=20)
        
        ctk.CTkButton(weather_frame, text="Update Weather", command=self.refresh_weather).pack(pady=10)

        # --- RIGHT COLUMN: LIVE BOOKINGS ---
        booking_frame = ctk.CTkFrame(self.main_view, corner_radius=10)
        booking_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(booking_frame, text="Active Bookings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.booking_list = ctk.CTkScrollableFrame(booking_frame, height=300)
        self.booking_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(booking_frame, text="Refresh Feed", command=self.refresh_bookings).pack(pady=10)

        # Initial Load
        self.refresh_weather()
        self.refresh_bookings()

    def refresh_weather(self):
        try:
            response = requests.get("http://127.0.0.1:8000/check-weather")
            data = response.json()
            self.weather_info.configure(text=data["message"], text_color="white")
        except Exception:
            self.weather_info.configure(text="Weather API Offline", text_color="red")

    def refresh_bookings(self):
        for widget in self.booking_list.winfo_children():
            widget.destroy()
        try:
            response = requests.get("http://127.0.0.1:8000/bookings/")
            bookings = response.json()
            for b in bookings:
                b_lbl = ctk.CTkLabel(
                    self.booking_list, 
                    text=f"User {b['user_id']} ➔ Item {b['resource_id']}\nTime: {b['start_time'][:16]}", 
                    anchor="w", justify="left"
                )
                b_lbl.pack(fill="x", padx=5, pady=5)
                ctk.CTkFrame(self.booking_list, height=1, fg_color="gray").pack(fill="x") # Separator line
        except Exception:
            ctk.CTkLabel(self.booking_list, text="No bookings found.").pack()

    # ==========================================
    #             RESOURCES TAB
    # ==========================================
    def show_resources(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header_frame, text="Inventory & Studios", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header_frame, text="+ Add New", width=100, fg_color="green", command=self.open_add_resource_window).pack(side="right", padx=10)
        ctk.CTkButton(header_frame, text="Refresh", width=80, command=self.refresh_resources).pack(side="right")

        self.resource_list_frame = ctk.CTkScrollableFrame(self.main_view, width=800, height=400)
        self.resource_list_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.refresh_resources()

    def refresh_resources(self):
        for widget in self.resource_list_frame.winfo_children():
            widget.destroy()

        try:
            response = requests.get("http://127.0.0.1:8000/resources/")
            resources = response.json()

            for item in resources:
                item_frame = ctk.CTkFrame(self.resource_list_frame)
                item_frame.pack(fill="x", padx=10, pady=5)
                
                name_lbl = ctk.CTkLabel(item_frame, text=f"ID: {item['id']} | {item['name']}", font=ctk.CTkFont(weight="bold"))
                name_lbl.pack(side="left", padx=10)
                
                desc_lbl = ctk.CTkLabel(item_frame, text=item['description'], text_color="gray")
                desc_lbl.pack(side="left", padx=20)
                
                ctk.CTkButton(item_frame, text="Edit", width=60, fg_color="darkblue").pack(side="right", padx=10)

        except Exception:
            ctk.CTkLabel(self.resource_list_frame, text="Error connecting to API. Is Uvicorn running?").pack(pady=20)

    def open_add_resource_window(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Resource/Studio")
        self.add_win.geometry("400x400")
        self.add_win.attributes("-topmost", True)

        ctk.CTkLabel(self.add_win, text="Resource Name:").pack(pady=(20, 0))
        self.entry_name = ctk.CTkEntry(self.add_win, width=250)
        self.entry_name.pack(pady=5)

        ctk.CTkLabel(self.add_win, text="Description:").pack(pady=(10, 0))
        self.entry_desc = ctk.CTkEntry(self.add_win, width=250)
        self.entry_desc.pack(pady=5)

        ctk.CTkLabel(self.add_win, text="Category ID (1=Photo, 2=Studio):").pack(pady=(10, 0))
        self.entry_cat = ctk.CTkEntry(self.add_win, width=250)
        self.entry_cat.pack(pady=5)

        ctk.CTkButton(self.add_win, text="Save to Nexus", command=self.save_new_resource).pack(pady=20)

    def save_new_resource(self):
        name = self.entry_name.get()
        desc = self.entry_desc.get()
        cat_id = self.entry_cat.get()

        url = f"http://127.0.0.1:8000/resources/?name={name}&description={desc}&category_id={cat_id}"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                self.add_win.destroy()
                self.refresh_resources()
        except Exception:
            pass

    # ==========================================
    #             USERS TAB
    # ==========================================
    def show_users(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header_frame, text="User Management", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header_frame, text="+ Add User", width=100, fg_color="green", command=self.open_add_user_window).pack(side="right", padx=10)
        ctk.CTkButton(header_frame, text="Refresh", width=80, command=self.refresh_users).pack(side="right")

        self.user_list_frame = ctk.CTkScrollableFrame(self.main_view, width=800, height=400)
        self.user_list_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.refresh_users()

    def refresh_users(self):
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        try:
            response = requests.get("http://127.0.0.1:8000/users/")
            users = response.json()

            for user in users:
                user_frame = ctk.CTkFrame(self.user_list_frame)
                user_frame.pack(fill="x", padx=10, pady=5)
                
                info_lbl = ctk.CTkLabel(user_frame, text=f"ID: {user['id']} | {user['name']} ({user['role']})", font=ctk.CTkFont(weight="bold"))
                info_lbl.pack(side="left", padx=10)
                
                email_lbl = ctk.CTkLabel(user_frame, text=user['email'], text_color="gray")
                email_lbl.pack(side="left", padx=20)

        except Exception:
            ctk.CTkLabel(self.user_list_frame, text="Error connecting to API.").pack(pady=20)

    def open_add_user_window(self):
        self.user_win = ctk.CTkToplevel(self)
        self.user_win.title("Add New User")
        self.user_win.geometry("400x400")
        self.user_win.attributes("-topmost", True)

        ctk.CTkLabel(self.user_win, text="Full Name:").pack(pady=(20, 0))
        self.u_name = ctk.CTkEntry(self.user_win, width=250)
        self.u_name.pack(pady=5)

        ctk.CTkLabel(self.user_win, text="Email:").pack(pady=(10, 0))
        self.u_email = ctk.CTkEntry(self.user_win, width=250)
        self.u_email.pack(pady=5)

        ctk.CTkLabel(self.user_win, text="Role (Student/Admin):").pack(pady=(10, 0))
        self.u_role = ctk.CTkEntry(self.user_win, width=250)
        self.u_role.pack(pady=5)

        ctk.CTkButton(self.user_win, text="Create User", command=self.save_new_user).pack(pady=20)

    def save_new_user(self):
        name = self.u_name.get()
        email = self.u_email.get()
        role = self.u_role.get()

        url = f"http://127.0.0.1:8000/users/?name={name}&email={email}&role={role}"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                self.user_win.destroy()
                self.refresh_users()
        except Exception:
            pass

if __name__ == "__main__":
    app = NexusAdmin()
    app.mainloop()