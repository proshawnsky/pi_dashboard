import tkinter as tk
import requests
import datetime
from datetime import timedelta
import pytz
from tzlocal import get_localzone
from PIL import Image, ImageTk
import io
import base64
import json
import tkinter.ttk as ttk  # Import ttk for the table
from PIL import Image, ImageTk 
import sys
import os
import signal
import sys
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

os.environ["DISPLAY"] = ":0"

# Predefined birthdays
BIRTHDAYS = {
    "02-21": "Alice's Birthday",
    "03-15": "Bob's Birthday",
    "07-04": "Independence Day"
}

def get_weather():
    API_KEY = "930c87b7116a66e85b21d872488e5f66"
    CITY = "Chandler"

    # Get current weather for current temp, condition, and sunrise/sunset
    URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"
    response = requests.get(URL)
    data = response.json()

    if response.status_code == 200:
        local_tz = get_localzone()
        temperature = data['main']['temp']
        temperature_lo = data['main']['temp_min']
        temperature_hi = data['main']['temp_max']
        condition = data['weather'][0]['description'].capitalize()
        icon_code = data['weather'][0]['icon']
        
        sunrise_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunrise']).replace(tzinfo=pytz.utc)
        sunset_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunset']).replace(tzinfo=pytz.utc)
        sunrise_local = sunrise_utc.astimezone(local_tz).strftime('%I:%M %p')
        sunset_local = sunset_utc.astimezone(local_tz).strftime('%I:%M %p')
        
        temp_label.config(text=f"{round(temperature)}°F")
        temp_lo_hi_label.config(text=f"{round(temperature_lo)}°F - {round(temperature_hi)}°F")
        # temp_hi_label.config(text=f"{round(temperature_hi)}°F")
        condition_label.config(text=f"{condition}")
        sunrise_label.config(text=f"Sunrise: {sunrise_local}")
        sunset_label.config(text=f"Sunset: {sunset_local}")
        
        # Load weather icon
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
        icon_response = requests.get(icon_url)
        icon_image = Image.open(io.BytesIO(icon_response.content))
        icon_image = icon_image.resize((300, 300))
        icon_photo = ImageTk.PhotoImage(icon_image)
    else:
        temp_label.config(text="")
        condition_label.config(text="")
        sunrise_label.config(text="")
        sunset_label.config(text="")
    
    # Get daily weather for mix/max temp
    lat, lon = 33.3062, -111.8413  # Chandler, AZ
    cnt = 8
    # API_KEY = "24a10d3098dce520e6bacdd1ee79124b"
    URL = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&cnt={cnt}"
    response = requests.get(URL)
    data = response.json()
    print(json.dumps(data, indent=4))
    # temperatures = [entry["main"]["temp"] for entry in data["list"]]
    # print(temperatures)
    # # Find min and max temperatures
    # min_temp = min(temperatures)
    # max_temp = max(temperatures)

    # print(f"Minimum Temperature: {min_temp} K")
    # print(f"Maximum Temperature: {max_temp} K")

    root.after(600000, get_weather)

def get_astronomical_events():
    global planet_icons  # Ensure the dictionary persists
    planet_icons = {}
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

    for row in astro_table.get_children():
        astro_table.delete(row)
    astro_table.tag_configure("visible", foreground="green")
    astro_table.tag_configure("partiallyvisible", foreground="orange")
    astro_table.tag_configure("hidden", foreground="white")
    
    if response.status_code == 200:
        data = response.json()
        planet_icons = {}
        for body in data['data']['table']['rows']:
            name = body['cells'][0]['name']
            if name not in ["Sun", "Earth","Uranus","Neptune","Pluto"]:
                el = float(body['cells'][0]['position']['horizontal']['altitude']['degrees'])
                az = float(body['cells'][0]['position']['horizontal']['azimuth']['degrees'])
                tag = "visible" if el > 30 else "partiallyvisible" if el > 5 else "hidden"
                img = Image.open(f"{name.lower()}.png")
                img = img.resize((35, 35), Image.LANCZOS)
                planet_icons[name] = ImageTk.PhotoImage(img)

                # Insert into the table
                astro_table.insert("", "end", image=planet_icons[name], values=(name, f"{az:.1f}", f"{el:.1f}"), tags=(tag,))
    root.after(1000*5*60, get_astronomical_events) # Update every 5 minutes

def check_birthdays():
    today = datetime.datetime.now().strftime("%m-%d")
    date = datetime.datetime.now()
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")
    day = date.day

    # Add the correct suffix (st, nd, rd, th)
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Combine everything
    formatted_date = f"{day_of_week}, {month} {day}{suffix}"

    date_label.config(text=formatted_date)
    # if today in BIRTHDAYS:
    #     birthday_label.config(text=f"Today: {BIRTHDAYS[today]}")
    # else:
    #     birthday_label.config(text="No special birthdays today")

def exit_fullscreen(event):
    root.attributes('-fullscreen', False)
    root.geometry("800x600")

# def create_calendar_grid():

    # # Define column headers (Day Names)
    # day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # # Get today's date and find the start of the current week (Sunday)
    # today = datetime.today()
    # start_date = today - timedelta(days=today.weekday() + 1)  # Adjust to last Sunday

    # # Create grid layout
    # for col, day in enumerate(day_names):
    #     # Row 0: Day of the week
    #     tk.Label(root, text=day, font=("Arial", 12, "bold"), padx=10, pady=5, borderwidth=2, relief="ridge").grid(row=0, column=col, sticky="nsew")

    #     # Row 1: This week's dates
    #     date_label = (start_date + timedelta(days=col)).strftime("%b %d")  # Format: "Feb 25"
    #     tk.Label(root, text=date_label, font=("Arial", 12), padx=10, pady=5, borderwidth=2, relief="ridge").grid(row=1, column=col, sticky="nsew")

    #     # Row 2: Next week's dates
    #     next_week_label = (start_date + timedelta(days=col + 7)).strftime("%b %d")
    #     tk.Label(root, text=next_week_label, font=("Arial", 12), padx=10, pady=5, borderwidth=2, relief="ridge").grid(row=2, column=col, sticky="nsew")

    # # Configure column widths evenly
    # for i in range(7):
    #     root.grid_columnconfigure(i, weight=1)




root = tk.Tk()
root.title("Weather Dashboard")
root.attributes('-fullscreen', True)
root.configure(bg="black")

rows, cols = 12, 20  # Define the grid size
# Make all rows and columns expandable
for i in range(rows):  # Number of rows
    root.grid_rowconfigure(i, minsize=40)  # Set fixed row heights
    root.grid_rowconfigure(0,weight=0, uniform='row')
for i in range(cols):  # Number of columns
    root.grid_columnconfigure(i, minsize=35)  # Set fixed column widths
    root.grid_columnconfigure(i, weight=0)

# Populate the grid with bordered labels
# for r in range(rows):
#     for c in range(cols):
#         label = tk.Label(root, text=f"{r},{c}", borderwidth=1, relief="solid")
#         label.grid(row=r, column=c, padx=0, pady=0, sticky="nsew")  # sticky fills the cell

clock_label = tk.Label(root, text="",font=("Arial", 40, "bold"), bg="black", fg="white")
clock_label.grid(row=1, column=7,columnspan=8,rowspan=2)

date_label = tk.Label(root, text="",font=("Arial", 20, "bold"), bg="black", fg="white")
date_label.grid(row=0, column=7,columnspan=8,rowspan=1)

userpass = "66ee8b75-2459-49ab-9a3f-586637c8fe61:3dda189650928f07a077fdd3d6f1cd1c6f0c2087e3e5188ee71280e089b843040735258c780a8af6477d1f1d05966934fdafdfd8615f77d8192e484ecfd61f09acb58b8eaf4da841162ba14fa56269b926fcccb93a2a72c6e96bb5a23516c05edd84aa1ae72b1084720724556a7ba4b0"
authString = base64.b64encode(userpass.encode()).decode()

# Format the date with the full weekday name, month, and day with suffix

# Define the scope needed to read Google Calendar events
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_credentials():
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

    if not events:
        print("No upcoming events found.")
        return

    print("Upcoming events:")
    for event in events:
        
        day = event["start"].get("dateTime", event["start"].get("date"))  # Handle all-day events

        if "T" in day:
            day = day[:10]
        day = format_date(day)    
        print(day)

            # start = datetime.datetime.strptime(f"{start}", "%Y-%m-%dT%H:%M")

            # print(f"{start} - {event['summary']}")

        # event_summary = event["start"].get("dateTime", event["start"].get("date"))
        # start_time = 
        # event_dt = 
        events_table.insert("", "end", values=(f"{day}", f"{event['summary']}"))

def update_clock():
    now = datetime.datetime.now().strftime('%I:%M:%S %p')
    clock_label.config(text=now)
    root.after(1000, update_clock)

def format_date(date_str):
    # Convert string to datetime object
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    # Format as "Sunday, Mar 2" (removes leading zero)
    formatted_dt = dt.strftime("%A, %b ") + str(dt.day)  # Example: Sunday, Mar 2
    
    # Add correct day suffix
    def day_suffix(day):
        return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    return f"{formatted_dt}{day_suffix(dt.day)}"

frame_weather = tk.Frame(root, bg="black")
frame_weather.grid(row=0, column=16,columnspan=4,rowspan=5)

temp_label = tk.Label(frame_weather, text="", font=("Arial", 48, "bold"), bg="black", fg="white",anchor="n")
temp_label.pack()

temp_lo_hi_label = tk.Label(frame_weather, text="", font=("Arial", 24, "bold"), bg="black", fg="white",anchor="n")
temp_lo_hi_label.pack()

# temp_hi_label = tk.Label(frame_weather, text="", font=("Arial", 30, "bold"), bg="black", fg="white",anchor="n")
# temp_hi_label.pack(side="right")



frame_details = tk.Frame(frame_weather, bg="black")
frame_details.pack()

# feels_like_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
# feels_like_label.pack()

# humidity_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
# humidity_label.pack()

condition_label = tk.Label(frame_weather, text="", font=("Arial", 16, "italic"), bg="black", fg="white")
condition_label.pack()

sunrise_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
sunrise_label.pack()

sunset_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
sunset_label.pack()


style = ttk.Style()
style.theme_use("clam")  # Use 'clam' to allow background modifications

# # Configure the style for Treeview
style.configure("Treeview", font=("Arial", 14))  # Adjust font size
style.configure("Treeview", rowheight=35)  # Increase row height for larger text
style.configure("Treeview",
                background="black",  # Background of rows
                foreground="white",  # Text color
                fieldbackground="black",  # Background when not selected
                borderwidth=0)  # Remove borders

# # Configure the heading style
style.configure("Treeview.Heading",
                background="black",  # Header background
                foreground="white",  # Header text color
                font=("Arial", 12, "bold"))

# # Create Treeview for astronomical data
astro_table = ttk.Treeview(root, columns=("Planet", "Azimuth", "Elevation"), show="tree headings", style="Treeview", height = 6)
astro_table.grid(row=5, column=14, rowspan = 9, columnspan = 6)
astro_table.column("#0", width=60, minwidth=60, stretch=True) 
astro_table.heading("Planet", text="Body")
astro_table.heading("Azimuth", text="Az°")
astro_table.heading("Elevation", text="El°")

# astro_table.column("Icon", width=0, anchor="center")  # Hidden column for images
astro_table.column("Planet", width=90)
astro_table.column("Azimuth", width=80)
astro_table.column("Elevation", width=60)

events_table = ttk.Treeview(root, columns=("Date", "Event"), show="headings", style="Treeview", height = 6)
events_table.grid(row=5, column=0, rowspan = 9, columnspan = 14)
events_table.heading("Date", text="Date")
events_table.heading("Event", text="Event")

# astro_table.column("Icon", width=0, anchor="center")  # Hidden column for images
events_table.column("Date", width=180)
events_table.column("Event", width=300)

get_weather()
get_astronomical_events()
check_birthdays()
update_clock()
get_upcoming_events()

def handle_exit(signum=None, frame=None):
    print("Received signal to exit. Cleaning up...")
    root.quit()   # Close Tkinter mainloop
    root.destroy()  # Ensure cleanup
    sys.exit(0)  # Exit script properly

# Bind SIGINT (Ctrl+C) to the handle_exit function
signal.signal(signal.SIGINT, handle_exit)

root.mainloop()


