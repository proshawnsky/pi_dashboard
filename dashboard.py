import customtkinter as ctk
import datetime
# from tkinter import ttk
import tkinter as tk
import requests
# import json
from PIL import Image, ImageTk
import io
import base64
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request # type: ignore
import re
import random
import time
import pygame

class Day:
    def __init__(self, unixDay: int, frame=None, dateLabel=None, eventLabel=None):
        self.unixDay = unixDay 
        self.frame = frame
        self.dateLabel = dateLabel
        self.eventLabel = eventLabel
        self.events = []
    
    def add_event(self, event=None):
        self.events.append(event)
        
    def get_events(self):
        return self.events
    
    def get_unixDay(self):
        return self.unixDay
    
    def edit_events_label(self, str=str):
        self.eventLabel.configure(text=str)

    def set_date(self, date=0):
        self.dateLabel.configure(text=str(date))

    def set_frame_color(self,color="", border_width=2):
        self.frame.configure(border_color=color,border_width=border_width)

    def set_unixDay(self,unixDay):
        self.unixDay = unixDay 
    
    def reset_events(self):
        self.events.clear()

class Event:
    def __init__ (self, unixDay=None, summary=None, startTime=None, endTime=None):
        self.unixDay = unixDay
        self.summary = summary
        
    def get_unixDay(self):
        return self.unixDay   
    
    def get_summary(self):
        return self.summary 

class Checklist:
    def __init__(self, name = "", items=[]):
        self.name = name
        self.items = items
        self.states = [False] * len(items)
        self.labels = []
    def set_labels(self, labels=[]):
        self.labels = labels

    def set_vars(self, vars=[]):
        self.vars = vars
    def set_message_label(self, footer_label=[]):
        self.footer_label = footer_label
    def clear_checklist(self):
        for i in range(len(self.states)):  # Assuming you have checklist_labels corresponding to each checklist item
            self.states[i] = False  # Set all to unselected state
            self.labels[i].configure(fg_color="gray20")  # Reset text color (if you changed it)

class Planet:
    def __init__ (self, name="", icon=None, startTime=None, endTime=None):
        self.name = name
        self.icon = icon
        self.az = 0
        self.el = 0    
Days = []
Checklists = []
pygame.mixer.init()

def play_sound():
    pygame.mixer.music.load("mixkit-cool-interface-click-tone-2568.wav")  # Replace with your .wav file path
    pygame.mixer.music.set_volume(1.0)  # Set volume to maximum (1.0 is the max)
    pygame.mixer.music.play()

# === WINDOW UTILITIES ===
def exit_fullscreen(event=None):
    app.wm_attributes("-fullscreen", False)
def close_app():
    app.destroy()
def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("light" if current_mode == "Dark" else "dark")

# === API UTILITIES ===
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
def format_date_for_lookup(date_text):
    """Converts a date label like 'Mon 5th' into 'YYYY-MM-DD' format."""
    parts = date_text.split()  # Example: ["Mon", "5th"]
    if len(parts) != 2:
        raise ValueError(f"Unexpected date format: {date_text}")

    day = remove_ordinal_suffix(parts[1])  # Remove 'th', 'st', etc.
    day = int(day)  # Convert cleaned day to integer

    today = datetime.date.today()
    possible_date = datetime.date(today.year, today.month, day)

    return possible_date.strftime("%Y-%m-%d")
def remove_ordinal_suffix(day_str):
    """Removes ordinal suffixes (st, nd, rd, th) from day numbers."""
    return re.sub(r"(st|nd|rd|th)", "", day_str)
# === UPDATE DATA FIELDS ===
def new_day():
    # global Days
    update_weather_tab()
    # Update Date Label on Home Page
    date = datetime.datetime.now()
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")
    day = date.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")    # Add the correct suffix (st, nd, rd, th)
    formatted_date = f"{day_of_week}, {month} {day}{suffix}"    # Combine everything
    date_label.configure(text=formatted_date)
    
    update_calendar_tab()

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
def update_clock():
    now = datetime.datetime.now()
    clock_label.configure(text=now.strftime('%I:%M:%S %p'))
    if now.hour == 0 and now.minute == 0 and now.second == 0:
        new_day()  # Call the function exactly once at midnight
    app.after(1000, update_clock)  # Call again after 1 second
def update_calendar_events():
    
    userpass = "66ee8b75-2459-49ab-9a3f-586637c8fe61:3dda189650928f07a077fdd3d6f1cd1c6f0c2087e3e5188ee71280e089b843040735258c780a8af6477d1f1d05966934fdafdfd8615f77d8192e484ecfd61f09acb58b8eaf4da841162ba14fa56269b926fcccb93a2a72c6e96bb5a23516c05edd84aa1ae72b1084720724556a7ba4b0"
    authString = base64.b64encode(userpass.encode()).decode()
    all_events = google_calendar_API()  # Fetch events

    for day in Days:
        day.reset_events()
        for event in all_events:
            if day.get_unixDay() == event.get_unixDay():
                day.add_event(event)
    for day in Days:
        event_label = []
        for event in day.get_events():
            event_label += event.get_summary() + "\n\n"
        event_label = "".join(event_label)
        day.edit_events_label(event_label)
def toggle(checklist, index):
    """Toggle the state of the checklist item."""
    checklist.states[index] = not checklist.states[index]
    play_sound()
    if checklist.states[index]:
        checklist.labels[index].configure(fg_color="green2") 
    else:
        checklist.labels[index].configure(fg_color="gray22") 
    if all(checklist.states):
        app.after(1000, checklist.clear_checklist)  # Call again after 1 second
        checklist.footer_label.configure(text=get_random_phrase())

def get_random_phrase():
    phrases = [
    "Only 40 more years!",
    "Crush this day!",
    "Have a great day at work!",
    "Do it for the shareholders!",
    "You are CEO Barbie!",
    "Work hard today! (but not too hard!)",
    "Rise and grind! (or just rise… that’s enough)",
    "Remember: you're working for future-you's retirement!",
    "Another day, another dollar (before taxes)!",
    "Get in, get paid, get out!",
    "Make that paper!",
    "Don't let the existential dread win!",
    "Meetings don't make money—just survive them!",
    "You got this! (and by ‘this’ I mean capitalism)",
    "If they ask for ‘one more thing,’ run!",
    "Smile! It confuses management.",
    "HR is not your friend, but coffee is!",
    "Emails don't reply to themselves! (but they should...)",
    "Clock in, zone out, clock out!",
    "Just pretend it's a video game with bad graphics.",
    "Keep calm and collect direct deposits.",
    "Your future self will thank you for showing up today!",
    "Success is just controlled chaos—go control some chaos!",
    "Time to trade time for money again!",
    "Make today better than your WiFi connection.",
    "If all else fails, just look busy!",
    "Remember: caffeine is a productivity multiplier!",
    "Every meeting could have been an email—stay strong!",
    "Monday’s almost over… unless it’s not Monday.",
    "Do it for the PTO!",
    "Another workday, another step closer to the weekend!",
    "No one reads reports, just make it look impressive!",

]
    return random.choice(phrases)    

def google_calendar_API():
    """Fetches and prints the next 5 upcoming events from Google Calendar."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Get current time in RFC3339 format
    now = datetime.datetime.utcnow() - datetime.timedelta(days=5)
    now = (now).isoformat() + "Z"
    later = datetime.datetime.utcnow() + datetime.timedelta(days=14)
    later = (later).isoformat() + "Z"

    # Fetch the next 5 upcoming events
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=later,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    all_events = []
    events = events_result.get("items", [])

    for event in events:
       
        day = event["start"].get("dateTime", event["start"].get("date"))  # Handle all-day events
        if "T" in day:
            day = day[:10]
        day = format_date(day)
        # Convert Google Calendar API date format to Unix time
        day_clean = re.sub(r"^[A-Za-z]+, ", "", day)  # This removes the weekday name and the comma
        day_clean = re.sub(r"(st|nd|rd|th)", "", day_clean) # Step 2: Remove ordinal suffixes (e.g., 'st', 'nd', 'rd', 'th')
        current_year = datetime.datetime.now().year # Step 3: Add the current year (if the year isn't specified)
        day_clean = f"{day_clean} {current_year}"  # Assuming we want to use the current year
        date_obj = datetime.datetime.strptime(day_clean, "%b %d %Y")   # Step 4: Convert the cleaned string to a datetime object
        unix_timestamp = int(date_obj.timestamp()) # Step 5: Convert the datetime object to Unix time
        
        all_events.append(Event(unix_timestamp, event['summary']))

    return all_events
# === HOME TAB ===
def initialize_home_tab(tab_home):
    date_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",72))
    date_label.pack(anchor="n")

    clock_label = ctk.CTkLabel(tab_home, text = "", font=("Arial",118))
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
def initialize_calendar_tab():
    global tab_calendar
    global Days
    # 2x7 grid for calendar dates
    row_frames = []

    today = datetime.date.today()
    days_to_previous_sunday = (today.weekday() + 1) % 7  # Ensure no extra day is subtracted
    previous_sunday = today - datetime.timedelta(days=days_to_previous_sunday)
    two_week_dates = [previous_sunday + datetime.timedelta(days=i) for i in range(14)]
    
    day_of_week_frame = ctk.CTkFrame(tab_calendar)  # Create a row
    day_of_week_frame.pack(fill="both", expand=True,anchor="n")  # Stack rows vertically
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    for day in weekdays:        # Make a label for the day of the week
        frame = ctk.CTkFrame(day_of_week_frame, corner_radius=1, border_width=2)
        frame.pack(side="left", fill="x", expand=True, padx=1, pady=1)  # Distribute evenly
        day_of_week_label = ctk.CTkLabel(frame, text=day, font=("Arial", 18),width=100)  
        day_of_week_label.pack(pady=3,padx=0,side="top",expand=True, anchor="center")

    for _ in range(2):  
        row_frame = ctk.CTkFrame(tab_calendar,height=80)  # Create a row
        row_frame.pack(fill="both", expand=True,anchor="s")  # Stack rows vertically
        row_frames.append(row_frame)

    for i,row_frame in enumerate(row_frames):
        for j in range(7):
            date = two_week_dates[(i)*7+j]

            frame = ctk.CTkFrame(row_frame, corner_radius=0, border_width=2, width=100)
            frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)  # Distribute evenly
            # if date == today:
            #     frame.configure(border_color='green2',border_width=3)

            # Make a label for the day of the week and date
            # calendar_date_label = ctk.CTkLabel(frame, text=f"{date.day}", font=("Arial", 18),width=100)  
            calendar_date_label = ctk.CTkLabel(frame, text="", font=("Arial", 18),width=100)  
            calendar_date_label.pack(pady=3,side="top",expand=False,anchor="n")

            # Make a label to store the events in that day
            calendar_event_label = ctk.CTkLabel(frame, text="", font=("Arial", 16),wraplength=90,width=100)  
            calendar_event_label.pack(pady=3,padx=4,side="top",expand=False)

            unixDay = int(date.strftime('%s'))
            Days.append(Day(unixDay, frame, calendar_date_label, calendar_event_label))

    # return calendar_date_labels, calendar_event_labels
def update_calendar_tab():
    today = datetime.date.today()
    days_to_previous_sunday = (today.weekday() + 1) % 7  # Ensure no extra day is subtracted
    previous_sunday = today - datetime.timedelta(days=days_to_previous_sunday)
    two_week_dates = [previous_sunday + datetime.timedelta(days=i) for i in range(14)]

    for i, day in enumerate(Days):

        date = two_week_dates[i]
        if date == today:
            day.set_frame_color('green2',3)
        else:
            day.set_frame_color('gray52',2)

        day.set_date(date.day)
        day.set_unixDay(int(date.strftime('%s')))
    update_calendar_events()

# === ASTRONOMY TAB ===
def initialize_astronomy_tab(tab_astronomy):
    astronomy_label = ctk.CTkLabel(tab_astronomy, text="Object Visibility Tonight (8:00pm)", font=("Arial", 24))
    astronomy_label.pack(expand=False)

    auth_string = "66ee8b75-2459-49ab-9a3f-586637c8fe61:3dda189650928f07a077fdd3d6f1cd1c6f0c2087e3e5188ee71280e089b843040735258c780a8af6477d1f1d05966934fdafdfd8615f77d8192e484ecfd61f09acb58b8eaf4da841162ba14fa56269b926fcccb93a2a72c6e96bb5a23516c05edd84aa1ae72b1084720724556a7ba4b0"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    LAT, LON = 33.3062, -111.8413  # Chandler, AZ
    DATE = datetime.date.today().isoformat()
    URL = f"https://api.astronomyapi.com/api/v2/bodies/positions"

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    tonight = "20:00:00" 
    
    params = {
        "latitude": LAT,
        "longitude": LON,
        "elevation": 0,
        "from_date": DATE,
        "to_date": DATE,
        "time": current_time#tonight # replaceable with current_time
    }
    headers = {
    "Authorization": f"Basic {auth_base64}"
    }
    response = requests.get(URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        planet_icons = {}
        for i, body in enumerate(data['data']['table']['rows']):
            name = body['cells'][0]['name']
            if name not in ["Sun", "Earth","Uranus","Neptune","Pluto"]:
                el = float(body['cells'][0]['position']['horizontal']['altitude']['degrees'])
                az = float(body['cells'][0]['position']['horizontal']['azimuth']['degrees'])
                print(name, az, el)
                frame = ctk.CTkFrame(tab_astronomy, corner_radius=25, border_width=5)
                frame.pack(side="left", fill="x", expand=True, padx=1, pady=1)  # Distribute evenly
                planet_name_label = ctk.CTkLabel(frame, text=name, font=("Arial", 32),width=100)  
                planet_name_label.pack(pady=15,padx=0,side="top",expand=True, anchor="center")
                planet_icon_label = ctk.CTkLabel(frame, text="", font=("Arial", 18),width=100)  
                planet_icon_label.pack(pady=10,padx=0,side="top",expand=True, anchor="center")
                formatted_string = f"El: {el:.1f}°\nAz: {az:.1f}°"

                planet_details_label = ctk.CTkLabel(frame, text=formatted_string, font=("Arial", 28),width=100)  
                planet_details_label.pack(pady=10,padx=0,side="top",expand=True, anchor="center")
                if el > 35:
                    planet_details_label.configure(text_color='lime green')
                    planet_name_label.configure(text_color='lime green')
                elif el > 0:
                    planet_details_label.configure(text_color='orange2')
                    planet_name_label.configure(text_color='orange2')
                image = Image.open(f"{name.lower()}.png")
                ctk_img = ctk.CTkImage(image, size=(100,100))
                planet_icon_label.configure(image=ctk_img,text="")
# === SETTINGS TAB ===
def initialize_settings_tab(tab_settings):
    theme_switch = ctk.CTkSwitch(tab_settings, text="Light Mode", command=toggle_theme)
    theme_switch.pack(expand=True)
    exit_button = ctk.CTkButton(tab_settings, text="Exit", command=close_app, fg_color="red", hover_color="darkred")
    exit_button.pack(pady=10)
    about_label = ctk.CTkLabel(tab_settings, text="Proshawnsky Pi Dashboard\nVersion 2.3", font=("Arial", 24))
    about_label.pack(expand=True)
    update_button = ctk.CTkButton(tab_settings, text="Update Calendar", command=update_calendar_tab)
    update_button.pack(pady=10)  # Adjust padding as needed
# === CHECKLISTS TAB ===
def initialize_checklists_tab(tab_checklists):
    tabview = ctk.CTkTabview(tab_checklists,corner_radius=20,border_width=2)
    tabview.pack(expand=True, fill="both", padx=0, pady=0,)
    Ellie_work_Checklist = Checklist(name="Ellie Work", items=["Phone", "Keys", "Badge", "Lunch","Water", "Coffee", "Laptop"])
    Shawn_work_Checklist = Checklist(name="Shawn Work", items=["Phone", "Keys", "Wallet","Badge", "Lunch", "Coffee", "Glasses"])
    Shawn_Biking = Checklist(name="Shawn Biking", items=["Water X2", "Food", "Phone","Wallet","Wahoo", "Lights","Gloves", "Glasses"])
    
    Checklists.append(Ellie_work_Checklist)
    Checklists.append(Shawn_work_Checklist)
    Checklists.append(Shawn_Biking)

    for checklist in Checklists:
        tab = tabview.add(checklist.name)
        checklist.set_vars([tk.IntVar(value=0) for _ in checklist.items])
        # checklist_vars = [tk.IntVar(value=0) for _ in checklist.items]
        # tab_Ellie1.configure(bg_color="white")
        labels = []
        checklist_frame = tk.Frame(tab)
        checklist_frame.pack(padx=0, pady=0, expand=True)  # Use pack for the frame
        checklist_frame.configure(bg=tab.cget("fg_color"))

        # Create a grid layout (2 columns) inside the frame
        for index, item in enumerate(checklist.items):
            row = index // 3  # Spread labels into two rows
            col = index % 3   # Alternate between column 0 and 1

            label = ctk.CTkLabel(checklist_frame, text=item, font=("Arial", 60), cursor="none", corner_radius=10,fg_color="gray20")  # Makes it clickable
            label.bind("<Button-1>", lambda e, i=index, c=checklist: toggle(c,i))  # Bind click event
            
            label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Place in grid
            labels.append(label)

        checklist.set_labels(labels)
        checklist_frame.columnconfigure(0, weight=1,uniform="equal")
        checklist_frame.columnconfigure(1, weight=1,uniform="equal")
        checklist_frame.columnconfigure(2, weight=1,uniform="equal")
        tabview._segmented_button.configure(font=("Arial", 30))  # Adjust font size here

        footer_label = ctk.CTkLabel(tab, text="", font=("Arial", 24))
        footer_label.pack(pady=10)  # Using pack for other elements
        checklist.set_message_label(footer_label)

    return labels, footer_label
# === SET UP WINDOW ===
def start():
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
    tabview.pack(expand=True, fill="both", padx=0, pady=0)

    # Add tabs
    tab_home = tabview.add("Home")
    tab_weather = tabview.add("Weather")
    tab_calendar = tabview.add("Calendar")
    tab_astronomy = tabview.add("Astronomy")
    tab_checklists = tabview.add("Checklists")
    
    tab_settings = tabview.add("Settings")
    tabview._segmented_button.configure(font=("Arial", 30))  # Adjust font size here

    return app, tab_home, tab_weather, tab_calendar, tab_astronomy, tab_settings, tab_checklists, font_large, font_small

# Create window, populate tabs

sound = pygame.mixer.Sound("mixkit-cool-interface-click-tone-2568.wav")
app, tab_home, tab_weather, tab_calendar, tab_astronomy, tab_settings, tab_checklists, font_large, font_small = start()
date_label, clock_label = initialize_home_tab(tab_home)
weather_label, weather_forecast_containers, weather_forcast_day_labels, weather_forecast_temp_labels, weather_forcast_icons = initialize_weather_tab(tab_weather)
initialize_calendar_tab()
initialize_astronomy_tab(tab_astronomy)
labels, footer_label = initialize_checklists_tab(tab_checklists)
initialize_settings_tab(tab_settings)

# Update fields
update_clock()
calendar_dates_JD = []
new_day()
update_weather_tab()
app.mainloop()