import customtkinter as ctk
import datetime
from tkinter import ttk
import tkinter as tk
import requests
import json
from PIL import Image, ImageTk
import io
import base64
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request




# Function to exit fullscreen when ESC is pressed

# === WINDOW UTILITIES ===
def exit_fullscreen(event=None):
    app.wm_attributes("-fullscreen", False)
def close_app():
    app.destroy()
def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("light" if current_mode == "Dark" else "dark")

# === MISC UTILITIES ===
def format_date(date_str):
    # Convert string to datetime object
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    # Format as "Sunday, Mar 2" (removes leading zero)
    formatted_dt = dt.strftime("%A, %b ") + str(dt.day)  # Example: Sunday, Mar 2
    
    # Add correct day suffix
    def day_suffix(day):
        return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    return f"{formatted_dt}{day_suffix(dt.day)}"
def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    """Handles Google authentication and saves token.json to avoid repeated logins."""
    creds = None

    # Check if we already have a stored token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If credentials are invalid or don't exist, request login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the token if expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)  # Opens browser for login
        # Save new credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# === UPDATE DATA FIELDS ===
def update_daily():
    date = datetime.datetime.now()
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")
    day = date.day
    # Add the correct suffix (st, nd, rd, th)
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    # Combine everything
    formatted_date = f"{day_of_week}, {month} {day}{suffix}"
    date_label.configure(text=formatted_date)
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
    app.after(1000, update_clock)
def update_calendar_events():
    userpass = "66ee8b75-2459-49ab-9a3f-586637c8fe61:3dda189650928f07a077fdd3d6f1cd1c6f0c2087e3e5188ee71280e089b843040735258c780a8af6477d1f1d05966934fdafdfd8615f77d8192e484ecfd61f09acb58b8eaf4da841162ba14fa56269b926fcccb93a2a72c6e96bb5a23516c05edd84aa1ae72b1084720724556a7ba4b0"
    authString = base64.b64encode(userpass.encode()).decode()
def get_upcoming_events():
    """Fetches and prints the next 5 upcoming events from Google Calendar."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Get current time in RFC3339 format
    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Fetch the next 5 upcoming events
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=6,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    events = events_result.get("items", [])
    for event in events:
        day = event["start"].get("dateTime", event["start"].get("date"))  # Handle all-day events

        if "T" in day:
            day = day[:10]
        day = format_date(day)    
   
        print(f"{day}", f"{event['summary']}")

# === HOME TAB ===
def initialize_home_tab(tab_home):
    date_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",52))
    date_label.pack(anchor="n")

    clock_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",86))
    clock_label.pack(anchor="n")

    home_label = ctk.CTkLabel(tab_home, text="Welcome to the Home Tab!", font=("Arial", font_large))
    home_label.pack(anchor="n")
    return date_label, clock_label
# === WEATHER TAB ===
def initialize_weather_tab(tab_weather):
    """ Initializes weather UI elements and returns lists of labels and frames. """
    
    # Create title label
    weather_label = ctk.CTkLabel(tab_weather, text="Welcome to the Weather Tab!", font=("Arial", 18), wraplength=750)
    weather_label.pack(expand=False)

    # Lists to store UI elements
    weather_forecast_containers = []
    weather_forcast_day_labels = []
    weather_forecast_temp_labels = []
    weather_forcast_icons = []

    today = datetime.datetime.today()

    # Create forecast containers
    for i in range(7):
        frame = ctk.CTkFrame(tab_weather, corner_radius=10, border_width=2)
        frame.pack(side="left", fill="x", expand=True, padx=2, pady=2, anchor="s")
        weather_forecast_containers.append(frame)

    # Add labels and icons to containers
    for i, frame in enumerate(weather_forecast_containers):
        day_of_week = today + datetime.timedelta(days=i)

        # Day label
        day_label = ctk.CTkLabel(frame, text=day_of_week.strftime("%a"), font=("Arial", 32))
        day_label.pack(expand=True, side="top", anchor="n", pady=2)
        weather_forcast_day_labels.append(day_label)

        # Weather icon
        icon_label = ctk.CTkLabel(frame, text="", font=("Arial", 20))  # Placeholder for icon
        icon_label.pack(pady=5)
        weather_forcast_icons.append(icon_label)

        # Temperature label
        temp_label = ctk.CTkLabel(frame, text="", font=("Arial", 32))
        temp_label.pack(expand=True, side="top", anchor="n", pady=5)
        weather_forecast_temp_labels.append(temp_label)

    return weather_label, weather_forecast_containers, weather_forcast_day_labels, weather_forecast_temp_labels, weather_forcast_icons
# === CALENDAR TAB ===
def initialize_calendar_tab(tab_calendar):
    calendar_label = ctk.CTkLabel(tab_calendar, text="Welcome to the Calendar Tab!", font=("Arial", font_large))
    calendar_label.pack(expand=True)
    

    # 2x7 grid for calendar dates
    row_frames = []
    calendar_date_labels = []
    calendar_event_labels = []
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

            current_date = start_date + datetime.timedelta(days=i*7+j)
            calendar_date_label = ctk.CTkLabel(frame, text=current_date.strftime("%a %d"), font=("Arial", 18))  
            calendar_date_label.pack(pady=5,side="top",expand=False)
            calendar_date_labels.append(date_label)

            calendar_event_label = ctk.CTkLabel(frame, text=current_date.strftime("%a %d"), font=("Arial", 12))  
            calendar_event_label.pack(pady=5,side="top",expand=False)
            calendar_event_labels.append(calendar_event_label)

            # Add a text label
            # label = ctk.CTkLabel(frame, text="event", font=("Arial", 14))
            # label.pack()
    today = datetime.date.today()
    days_since_sunday = today.weekday()  # weekday() returns 0=Monday, ..., 6=Sunday
    start_date = today - datetime.timedelta(days=days_since_sunday + 1)  # Move back to last Sunday

    return 
# === ASTRONOMY TAB ===
def initialize_astronomy_tab(tab_astronomy):
    astronomy_label = ctk.CTkLabel(tab_astronomy, text="Welcome to the Astronomy Tab!", font=("Arial", font_large))
    astronomy_label.pack(expand=True)
# === SETTINGS TAB ===
def initialize_settings_tab(tab_settings):
    theme_switch = ctk.CTkSwitch(tab_settings, text="Light Mode", command=toggle_theme)
    theme_switch.pack(expand=True)
    exit_button = ctk.CTkButton(tab_settings, text="Exit", command=close_app, fg_color="red", hover_color="darkred")
    exit_button.pack(pady=10)
    about_label = ctk.CTkLabel(tab_settings, text="Proshawnsky Pi Dashboard\nVersion 2.0", font=("Arial", 24))
    about_label.pack(expand=True)

# Initialize main application
app = ctk.CTk()
app.title("Dashboard V2.0")
# app.geometry("800x600")  # Default size before fullscreen

# Force Fullscreen without showing the taskbar
app.wm_attributes("-type", "dock")  # Forces fullscreen overlay
app.wm_attributes("-fullscreen", True)  # Fullscreen mode
SCREEN_WIDTH, SCREEN_HEIGHT = app.winfo_screenwidth(), app.winfo_screenheight()
font_large = 0.06 * SCREEN_WIDTH
font_small = 0.04 * SCREEN_WIDTH

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

date_label, clock_label = initialize_home_tab(tab_home)
weather_label, weather_forecast_containers, weather_forcast_day_labels, weather_forecast_temp_labels, weather_forcast_icons = initialize_weather_tab(tab_weather)
initialize_calendar_tab(tab_calendar)
initialize_astronomy_tab(tab_astronomy)
initialize_settings_tab(tab_settings)

# Run the app
update_clock()
update_daily()
update_weather_tab()
get_upcoming_events()
app.mainloop()
