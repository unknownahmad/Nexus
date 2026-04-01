import customtkinter as ctk
import requests
import threading
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

API_KEY = "NexusSuperSecret2026"
HEADERS = {"X-API-KEY": API_KEY}
BASE_URL = "https://nexus-production-7bc0.up.railway.app"

class NexusAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nexus Admin Control Center")
        self.geometry("1100x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

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

        self.main_view = ctk.CTkFrame(self, corner_radius=10)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.status_label = ctk.CTkLabel(self.main_view, text="Welcome back, Admin.", font=ctk.CTkFont(size=20))
        self.status_label.pack(pady=20)

    # ---------------------------------------------------------
    # DASHBOARD TAB
    # ---------------------------------------------------------
    def show_dashboard(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_columnconfigure(1, weight=1)

        weather_frame = ctk.CTkFrame(self.main_view, corner_radius=10)
        weather_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(weather_frame, text="Barcelona Weather Status", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.weather_info = ctk.CTkLabel(weather_frame, text="Fetching...")
        self.weather_info.pack(pady=20)
        
        ctk.CTkButton(weather_frame, text="Update Weather", command=self.refresh_weather).pack(pady=10)

        booking_frame = ctk.CTkFrame(self.main_view, corner_radius=10)
        booking_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(booking_frame, text="Active Bookings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.booking_list = ctk.CTkScrollableFrame(booking_frame, height=300)
        self.booking_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(booking_frame, text="Refresh Feed", command=self.refresh_bookings).pack(pady=10)

        self.refresh_weather()
        self.refresh_bookings()

    def refresh_weather(self):
        try:
            response = requests.get(f"{BASE_URL}/weather/check-weather", headers=HEADERS, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.weather_info.configure(text=data["message"], text_color="white")
            else:
                self.weather_info.configure(text=f"Error: {response.status_code}", text_color="red")
        except requests.exceptions.RequestException:
            self.weather_info.configure(text="Weather API Offline", text_color="red")

    def refresh_bookings(self):
        for widget in self.booking_list.winfo_children():
            widget.destroy()
        try:
            response = requests.get(f"{BASE_URL}/bookings", headers=HEADERS, timeout=5)
            if response.status_code == 200:
                bookings = response.json()
                for b in bookings:
                    display_text = f"User {b['user_id']} ➔ {b.get('resource_name', 'Unknown Item')}\nTime: {b['start_time'][:16]}"
                    b_lbl = ctk.CTkLabel(
                        self.booking_list, 
                        text=display_text, 
                        anchor="w", justify="left"
                    )
                    b_lbl.pack(fill="x", padx=5, pady=5)
                    ctk.CTkFrame(self.booking_list, height=1, fg_color="gray").pack(fill="x")
            else:
                ctk.CTkLabel(self.booking_list, text="Failed to fetch bookings.", text_color="red").pack()
        except requests.exceptions.RequestException:
            ctk.CTkLabel(self.booking_list, text="API Offline.").pack()

    # ---------------------------------------------------------
    # RESOURCES TAB
    # ---------------------------------------------------------
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
            response = requests.get(f"{BASE_URL}/resources", headers=HEADERS, timeout=5)
            if response.status_code == 200:
                resources = response.json()

                for item in resources:
                    item_frame = ctk.CTkFrame(self.resource_list_frame)
                    item_frame.pack(fill="x", padx=10, pady=5)
                    
                    name_lbl = ctk.CTkLabel(item_frame, text=f"ID: {item['id']} | {item['name']}", font=ctk.CTkFont(weight="bold"))
                    name_lbl.pack(side="left", padx=10)
                    
                    desc_lbl = ctk.CTkLabel(item_frame, text=item['description'], text_color="gray")
                    desc_lbl.pack(side="left", padx=20)
                    
                    ctk.CTkButton(item_frame, text="Delete", width=60, fg_color="#922B21", 
                                  command=lambda i=item['id']: self.delete_resource(i)).pack(side="right", padx=10)
                    
                    ctk.CTkButton(item_frame, text="Edit", width=60, fg_color="darkblue",
                                  command=lambda i=item: self.open_edit_resource_window(i)).pack(side="right", padx=10)
            else:
                ctk.CTkLabel(self.resource_list_frame, text=f"Auth Error: {response.status_code}").pack(pady=20)

        except requests.exceptions.RequestException:
            ctk.CTkLabel(self.resource_list_frame, text="Error connecting to API.").pack(pady=20)

    def delete_resource(self, resource_id):
        def task():
            url = f"{BASE_URL}/resources/{resource_id}"
            try:
                response = requests.delete(url, headers=HEADERS, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.refresh_resources)
                    self.after(0, lambda: messagebox.showinfo("Success", "Resource deleted!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Failed: {response.text}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()

    def open_add_resource_window(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Resource")
        self.add_win.geometry("400x400")
        self.add_win.attributes("-topmost", True)

        ctk.CTkLabel(self.add_win, text="Resource Name:").pack(pady=(20, 0))
        self.entry_name = ctk.CTkEntry(self.add_win, width=250)
        self.entry_name.pack(pady=5)

        ctk.CTkLabel(self.add_win, text="Description:").pack(pady=(10, 0))
        self.entry_desc = ctk.CTkEntry(self.add_win, width=250)
        self.entry_desc.pack(pady=5)

        ctk.CTkLabel(self.add_win, text="Category ID:").pack(pady=(10, 0))
        self.entry_cat = ctk.CTkEntry(self.add_win, width=250)
        self.entry_cat.pack(pady=5)

        ctk.CTkButton(self.add_win, text="Save to Nexus", command=self.save_new_resource).pack(pady=20)

    def save_new_resource(self):
        payload = {
            "name": self.entry_name.get(),
            "description": self.entry_desc.get(),
            "category_id": int(self.entry_cat.get())
        }
        def task():
            url = f"{BASE_URL}/resources/"
            try:
                response = requests.post(url, headers=HEADERS, json=payload, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.add_win.destroy)
                    self.after(0, self.refresh_resources)
                    self.after(0, lambda: messagebox.showinfo("Success", "Resource Added!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", response.text))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()

    def open_edit_resource_window(self, item):
        self.edit_res_win = ctk.CTkToplevel(self)
        self.edit_res_win.title("Edit Resource")
        self.edit_res_win.geometry("400x400")
        self.edit_res_win.attributes("-topmost", True)

        ctk.CTkLabel(self.edit_res_win, text="Resource Name:").pack(pady=(20, 0))
        self.edit_r_name = ctk.CTkEntry(self.edit_res_win, width=250)
        self.edit_r_name.insert(0, item['name'])
        self.edit_r_name.pack(pady=5)

        ctk.CTkLabel(self.edit_res_win, text="Description:").pack(pady=(10, 0))
        self.edit_r_desc = ctk.CTkEntry(self.edit_res_win, width=250)
        self.edit_r_desc.insert(0, item['description'])
        self.edit_r_desc.pack(pady=5)

        ctk.CTkLabel(self.edit_res_win, text="Category ID:").pack(pady=(10, 0))
        self.edit_r_cat = ctk.CTkEntry(self.edit_res_win, width=250)
        self.edit_r_cat.insert(0, str(item['category_id']))
        self.edit_r_cat.pack(pady=5)

        ctk.CTkButton(self.edit_res_win, text="Update Resource", command=lambda: self.save_edit_resource(item['id'])).pack(pady=20)

    def save_edit_resource(self, resource_id):
        payload = {
            "name": self.edit_r_name.get(),
            "description": self.edit_r_desc.get(),
            "category_id": int(self.edit_r_cat.get())
        }
        def task():
            url = f"{BASE_URL}/resources/{resource_id}"
            try:
                response = requests.put(url, headers=HEADERS, json=payload, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.edit_res_win.destroy)
                    self.after(0, self.refresh_resources)
                    self.after(0, lambda: messagebox.showinfo("Success", "Resource Updated!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", response.text))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()

    # ---------------------------------------------------------
    # USERS TAB
    # ---------------------------------------------------------
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
            response = requests.get(f"{BASE_URL}/users", headers=HEADERS, timeout=5)
            if response.status_code == 200:
                users = response.json()

                for user in users:
                    user_frame = ctk.CTkFrame(self.user_list_frame)
                    user_frame.pack(fill="x", padx=10, pady=5)
                    
                    info_lbl = ctk.CTkLabel(user_frame, text=f"ID: {user['id']} | {user['name']} ({user['role']})", font=ctk.CTkFont(weight="bold"))
                    info_lbl.pack(side="left", padx=10)
                    
                    email_lbl = ctk.CTkLabel(user_frame, text=user['email'], text_color="gray")
                    email_lbl.pack(side="left", padx=20)

                    ctk.CTkButton(user_frame, text="Delete", width=60, fg_color="#922B21", 
                                  command=lambda u=user['id']: self.delete_user(u)).pack(side="right", padx=10)
                    
                    ctk.CTkButton(user_frame, text="Edit", width=60, fg_color="darkblue",
                                  command=lambda u=user: self.open_edit_user_window(u)).pack(side="right", padx=10)
            else:
                ctk.CTkLabel(self.user_list_frame, text=f"Auth Error: {response.status_code}").pack(pady=20)

        except requests.exceptions.RequestException:
            ctk.CTkLabel(self.user_list_frame, text="Error connecting to API.").pack(pady=20)

    def delete_user(self, user_id):
        def task():
            url = f"{BASE_URL}/users/{user_id}"
            try:
                response = requests.delete(url, headers=HEADERS, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.refresh_users) 
                    self.after(0, lambda: messagebox.showinfo("Success", "User deleted!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Failed: {response.text}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()

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

        ctk.CTkLabel(self.user_win, text="Role:").pack(pady=(10, 0))
        self.u_role = ctk.CTkEntry(self.user_win, width=250)
        self.u_role.pack(pady=5)

        ctk.CTkButton(self.user_win, text="Create User", command=self.save_new_user).pack(pady=20)

    def save_new_user(self):
        payload = {
            "name": self.u_name.get(),
            "email": self.u_email.get(),
            "role": self.u_role.get()
        }
        def task():
            url = f"{BASE_URL}/users/"
            try:
                response = requests.post(url, headers=HEADERS, json=payload, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.user_win.destroy)
                    self.after(0, self.refresh_users)
                    self.after(0, lambda: messagebox.showinfo("Success", "User Created!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", response.text))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()

    def open_edit_user_window(self, user):
        self.edit_user_win = ctk.CTkToplevel(self)
        self.edit_user_win.title("Edit User")
        self.edit_user_win.geometry("400x400")
        self.edit_user_win.attributes("-topmost", True)

        ctk.CTkLabel(self.edit_user_win, text="Full Name:").pack(pady=(20, 0))
        self.edit_u_name = ctk.CTkEntry(self.edit_user_win, width=250)
        self.edit_u_name.insert(0, user['name'])
        self.edit_u_name.pack(pady=5)

        ctk.CTkLabel(self.edit_user_win, text="Email:").pack(pady=(10, 0))
        self.edit_u_email = ctk.CTkEntry(self.edit_user_win, width=250)
        self.edit_u_email.insert(0, user['email'])
        self.edit_u_email.pack(pady=5)

        ctk.CTkLabel(self.edit_user_win, text="Role:").pack(pady=(10, 0))
        self.edit_u_role = ctk.CTkEntry(self.edit_user_win, width=250)
        self.edit_u_role.insert(0, user['role'])
        self.edit_u_role.pack(pady=5)

        ctk.CTkButton(self.edit_user_win, text="Update User", command=lambda: self.save_edit_user(user['id'])).pack(pady=20)

    def save_edit_user(self, user_id):
        payload = {
            "name": self.edit_u_name.get(),
            "email": self.edit_u_email.get(),
            "role": self.edit_u_role.get()
        }
        def task():
            url = f"{BASE_URL}/users/{user_id}"
            try:
                response = requests.put(url, headers=HEADERS, json=payload, timeout=5)
                if response.status_code == 200:
                    self.after(0, self.edit_user_win.destroy)
                    self.after(0, self.refresh_users)
                    self.after(0, lambda: messagebox.showinfo("Success", "User Updated!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", response.text))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
                
        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    app = NexusAdmin()
    app.mainloop()