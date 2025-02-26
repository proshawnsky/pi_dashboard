import tkinter as tk
import requests
import datetime
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
    URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"
    response = requests.get(URL)
    data = response.json()
    
    if response.status_code == 200:
        local_tz = get_localzone()
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        condition = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        icon_code = data['weather'][0]['icon']
        
        sunrise_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunrise']).replace(tzinfo=pytz.utc)
        sunset_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunset']).replace(tzinfo=pytz.utc)
        sunrise_local = sunrise_utc.astimezone(local_tz).strftime('%I:%M %p')
        sunset_local = sunset_utc.astimezone(local_tz).strftime('%I:%M %p')
        
        temp_label.config(text=f"{round(temperature)}°F")
        feels_like_label.config(text=f"Feels like: {feels_like}°F")
        condition_label.config(text=f"{condition}")
        humidity_label.config(text=f"Humidity: {humidity}%")
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
        feels_like_label.config(text="")
        condition_label.config(text="")
        humidity_label.config(text="")
        sunrise_label.config(text="")
        sunset_label.config(text="")
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
    
def update_clock():
    now = datetime.datetime.now().strftime('%I:%M:%S %p')
    clock_label.config(text=now)
    root.after(1000, update_clock)

frame_weather = tk.Frame(root, bg="black")
frame_weather.grid(row=0, column=16,columnspan=4,rowspan=5)

temp_label = tk.Label(frame_weather, text="", font=("Arial", 30, "bold"), bg="black", fg="white",anchor="n")
temp_label.pack()

condition_label = tk.Label(frame_weather, text="", font=("Arial", 16, "italic"), bg="black", fg="white")
condition_label.pack()

frame_details = tk.Frame(frame_weather, bg="black")
frame_details.pack()

feels_like_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
feels_like_label.pack()

humidity_label = tk.Label(frame_details, text="", font=("Arial", 16), bg="black", fg="white")
humidity_label.pack()

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

get_weather()
get_astronomical_events()
check_birthdays()
update_clock()

def handle_exit(signum=None, frame=None):
    print("Received signal to exit. Cleaning up...")
    root.quit()   # Close Tkinter mainloop
    root.destroy()  # Ensure cleanup
    sys.exit(0)  # Exit script properly

# Bind SIGINT (Ctrl+C) to the handle_exit function
signal.signal(signal.SIGINT, handle_exit)

root.mainloop()


