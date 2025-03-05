import customtkinter as ctk
import datetime
from tkinter import ttk
import tkinter as tk
import requests
import json
from PIL import Image, ImageTk
import io

# Initialize main application
app = ctk.CTk()
app.title("Dashboard V2.0")
# app.geometry("800x600")  # Default size before fullscreen

# Force Fullscreen without showing the taskbar
app.wm_attributes("-type", "dock")  # Forces fullscreen overlay
app.wm_attributes("-fullscreen", True)  # Fullscreen mode

SCREEN_WIDTH, SCREEN_HEIGHT = app.winfo_screenwidth(), app.winfo_screenheight()
print(SCREEN_WIDTH, SCREEN_HEIGHT)

font_large = 0.06 * SCREEN_WIDTH
font_small = 0.04 * SCREEN_WIDTH
# Function to exit fullscreen when ESC is pressed
def exit_fullscreen(event=None):
    app.wm_attributes("-fullscreen", False)

# Function to close the application
def close_app():
    app.destroy()

# def update_daily():
def update_weather_tab():
    API_KEY = "930c87b7116a66e85b21d872488e5f66"
    lat, lon = 33.3062, -111.8413  # Chandler, AZ
    URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=imperial&appid={API_KEY}"
    response = requests.get(URL)
    data = response.json()

    URL_overview = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon={lon}&units=imperial&appid={API_KEY}"
    response_overview = requests.get(URL_overview)
    data_overview = response_overview.json()


    daily_summary_text = data_overview['weather_overview']
    print(daily_summary_text)
    weather_label.configure(text=f"Today: {daily_summary_text}")

    for i, label in enumerate(weather_forecast_temp_labels):
        # Example: Add a text label
        max = int(data['daily'][i]['temp']['max'])
        min = int(data['daily'][i]['temp']['min'])
        
        label.configure(text=f"{min}°F\n{max}°F",pady=5)

    for i, icon_handle in enumerate(weather_forcast_icons):
        icon_code = data['daily'][i]['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"        
        icon_response = requests.get(icon_url)
        pil_image = Image.open(io.BytesIO(icon_response.content))
        ctk_img = ctk.CTkImage(pil_image, size=(84,84))
        icon_handle.configure(image=ctk_img,text="")

        # label.pack(expand=True,side="top",anchor="n")

        # Example: Add an icon (just a text placeholder for now)
        # icon = ctk.CTkLabel(frame, text="🔆", font=("Arial", 20))  # Replace with an actual image if needed
        # icon.pack(pady=5)

def update_clock():
    now = datetime.datetime.now().strftime('%I:%M:%S %p')
    clock_label.configure(text=now)
    minutes = int(datetime.datetime.now().strftime('%M'))
    seconds = int(datetime.datetime.now().strftime('%S'))
    
    date = datetime.datetime.now()
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")
    day = date.day
    # Add the correct suffix (st, nd, rd, th)
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    # Combine everything
    formatted_date = f"{day_of_week}, {month} {day}{suffix}"
    date_label.configure(text=formatted_date)
    # after(1000, update_clock) # every second, update the clock
    app.after(1000, update_clock)


##########################################################################################################################################################

# Bind ESC key to exit fullscreen
app.bind("<Escape>", exit_fullscreen)
app.configure(cursor="none")

# Set theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create a Tabview
tabview = ctk.CTkTabview(app,corner_radius=20,border_width=2)
tabview.pack(expand=True, fill="both", padx=0, pady=0,)

# Add tabs
tab_home = tabview.add("Home")
tab_weather = tabview.add("Weather")
tab_calendar = tabview.add("Calendar")
tab_astronomy = tabview.add("Astronomy")
tab_settings = tabview.add("Settings")
tabview._segmented_button.configure(font=("Arial", 24))  # Adjust font size here

# === HOME TAB ===
date_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",52))
date_label.pack(anchor="n")

clock_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",86))
clock_label.pack(anchor="n")

home_label = ctk.CTkLabel(tab_home, text="Welcome to the Home Tab!", font=("Arial", font_large))
home_label.pack(anchor="n")

# === WEATHER TAB ===
weather_label = ctk.CTkLabel(tab_weather, text="Welcome to the Weather Tab!", font=("Arial", 18),wraplength=750)
weather_label.pack(expand=False)

today = datetime.datetime.today()
weather_forecast_containers = []
weather_forcast_day_labels = []
weather_forecast_temp_labels = []
weather_forcast_icons = []

for i in range(7):
    frame = ctk.CTkFrame(tab_weather, corner_radius=10, border_width=2)
    frame.pack(side="left", fill="x", expand=True, padx=2, pady=2,anchor="s")
    weather_forecast_containers.append(frame)

# Add content to each container
for i, frame in enumerate(weather_forecast_containers):
    # Example: Add a text label
    day_of_week = today + datetime.timedelta(days=i)
    label = ctk.CTkLabel(frame, text=day_of_week.strftime("%a"), font=("Arial", 32))
    label.pack(expand=True,side="top",anchor="n",pady=2)
    weather_forcast_day_labels.append(label)

    # Example: Add an icon (just a text placeholder for now)
    icon = ctk.CTkLabel(frame, text="", font=("Arial", 20))  # Replace with an actual image if needed
    icon.pack(pady=5)
    weather_forcast_icons.append(icon)

    label = ctk.CTkLabel(frame, text="", font=("Arial", 32))
    label.pack(expand=True,side="top",anchor="n",pady=5)
    weather_forecast_temp_labels.append(label)

# === CALENDAR TAB ===
calendar_label = ctk.CTkLabel(tab_calendar, text="Welcome to the Calendar Tab!", font=("Arial", font_large))
calendar_label.pack(expand=True)

# 2x7 grid for calendar dates
row_frames = []
calendar_date_labels = []
today = datetime.date.today()
days_since_sunday = today.weekday()  # weekday() returns 0=Monday, ..., 6=Sunday
start_date = today - datetime.timedelta(days=days_since_sunday + 1)  # Move back to last Sunday

for _ in range(2):  
    row_frame = ctk.CTkFrame(tab_calendar)  # Create a row
    row_frame.pack(fill="both", expand=True)  # Stack rows vertically
    row_frames.append(row_frame)
calendar_containers = []
for i,row_frame in enumerate(row_frames):
    for j in range(7):
        frame = ctk.CTkFrame(row_frame, corner_radius=10, border_width=5)
        frame.pack(side="left", fill="both", expand=True, padx=2, pady=2)  # Distribute evenly
        calendar_containers.append(frame)

        # Add an icon (placeholder)
        current_date = start_date + datetime.timedelta(days=i*7+j)
        icon = ctk.CTkLabel(frame, text=current_date.strftime("%a %d"), font=("Arial", 18))  
        icon.pack(pady=5,side="top",expand=False)

        # Add a text label
        # label = ctk.CTkLabel(frame, text="event", font=("Arial", 14))
        # label.pack()
today = datetime.date.today()
days_since_sunday = today.weekday()  # weekday() returns 0=Monday, ..., 6=Sunday
start_date = today - datetime.timedelta(days=days_since_sunday + 1)  # Move back to last Sunday


# === ASTRONOMY TAB ===
astronomy_label = ctk.CTkLabel(tab_astronomy, text="Welcome to the Astronomy Tab!", font=("Arial", font_large))
astronomy_label.pack(expand=True)


# === SETTINGS TAB ===
def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("light" if current_mode == "Dark" else "dark")
theme_switch = ctk.CTkSwitch(tab_settings, text="Light Mode", command=toggle_theme)
theme_switch.pack(expand=True)
exit_button = ctk.CTkButton(tab_settings, text="Exit", command=close_app, fg_color="red", hover_color="darkred")
exit_button.pack(pady=10)
about_label = ctk.CTkLabel(tab_settings, text="Proshawnsky Pi Dashboard\nVersion 2.0", font=("Arial", 24))
about_label.pack(expand=True)

# Run the app
update_clock()
update_weather_tab()
app.mainloop()

 
