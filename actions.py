# ----------------------------
# Imports
# ----------------------------
import datetime
import os
import time
import pyautogui
import pyjokes
import pywhatkit
import wikipedia
import subprocess
import requests

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import config
import tts
import stt


def wish_user():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        tts.speak("Good morning sir.")
    elif 12 <= hour < 17:
        tts.speak("Good afternoon sir.")
    else:
        tts.speak("Good evening sir.")


def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M:%p").replace(":", " ")
    tts.speak(f"It's currently {current_time}.")
    print(current_time)


def ducks():
    tts.speak("Ducks are cool!")


def tell_joke():
    joke = pyjokes.get_joke()
    print(joke)
    tts.speak(joke)
    return joke


def open_app(app_name):
    if app_name in config.APPS:
        tts.speak(f"Opening {app_name}.")
        os.startfile(config.APPS[app_name])
    else:
        tts.speak(f"I do not have the app location for {app_name} yet.")


def find_and_save_app(app_name):
    tts.speak(f"Let me locate {app_name} for you, sir. This might take a moment.")
    print(f"Searching for {app_name}.exe...")
    
    # We will search the most common spots
    search_paths = [
        os.environ.get("PROGRAMFILES", "C:\\Program Files"),
        os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        os.path.join(os.environ.get("USERPROFILE"), "AppData", "Local")
    ]
    
    target = f"{app_name.lower().replace(' ', '')}.exe"
    target_with_spaces = f"{app_name.lower()}.exe"
    
    found_path = None
    
    for path in search_paths:
        if found_path:
            break
        for root, dirs, files in os.walk(path):
            for file in files:
                lower_file = file.lower()
                if lower_file == target or lower_file == target_with_spaces:
                    found_path = os.path.join(root, file)
                    break
            if found_path:
                break
                
    if found_path:
        tts.speak("App located.")
        print(f"Found at: {found_path}")
        # Save it to config
        config.APPS[app_name] = found_path
        
        # Save back to apps.json using json
        import json
        try:
            with open("apps.json", "w") as f:
                json.dump(config.APPS, f, indent=4)
        except Exception:
            pass
            
        open_app(app_name)
    else:
        tts.speak(f"I'm sorry sir, I couldn't find {app_name} on your system.")


def handle_open_command(app_name):
    # Check exact match
    if app_name in config.APPS:
        open_app(app_name)
        return
        
    # Check aliases
    for alias, real_name in config.APP_ALIASES.items():
        if alias in app_name:
            if real_name in config.APPS:
                open_app(real_name)
            else:
                find_and_save_app(real_name)
            return
            
    # If not found at all, search dynamically!
    find_and_save_app(app_name)


def run_routine(routine_name):
    if routine_name not in config.ROUTINES:
        tts.speak(f"I do not know the routine {routine_name}.")
        return
    tts.speak(f"{routine_name} activated.")
    for app_name in config.ROUTINES[routine_name]:
        open_app(app_name)


def handle_routine_command(query):
    for routine_name in config.ROUTINES:
        if routine_name in query:
            run_routine(routine_name)
            return True
    for alias, routine_name in config.ROUTINE_ALIASES.items():
        if alias in query:
            run_routine(routine_name)
            return True
    return False


def search_wikipedia(query):
    tts.speak("Searching Wikipedia.")
    query = query.replace(config.ASSISTANT_NAME, "")
    query = query.replace("search", "")
    query = query.replace("on wikipedia", "")
    query = query.replace("wikipedia", "")
    query = query.strip()

    try:
        results = wikipedia.summary(query, sentences=1)
        tts.speak("According to Wikipedia.")
        print(results)
        tts.speak(results)
    except Exception:
        tts.speak("Sorry, I could not find anything for that.")
        print("Sorry, I could not find anything for that.")


def play_media(query, platform=""):
    if not platform:
        tts.speak(f"Would you like me to play {query} on Spotify or YouTube?")
        platform = stt.listen_for_command()
        
    platform = platform.lower()
    
    if "spotify" in platform:
        tts.speak(f"Playing {query} on Spotify.")
        # Open Spotify search URI directly
        os.system(f"start spotify:search:{query.replace(' ', '%20')}")
        # Spotify Autoplay Hack: Wait for load, tab to top result, hit enter
        time.sleep(4)
        pyautogui.press("tab")
        time.sleep(0.2)
        pyautogui.press("enter")
    elif "youtube" in platform:
        tts.speak(f"Playing {query} on YouTube.")
        pywhatkit.playonyt(query)
    else:
        tts.speak("Media playback cancelled.")


def typing_mode():
    tts.speak("What should I write, sir?")
    while True:
        text_to_type = stt.listen_for_command()
        if text_to_type == "stop typing":
            tts.speak("Done, sir.")
            break
        if text_to_type != "none":
            pyautogui.write(text_to_type)


def volume_control(action):
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        
        if action == "mute":
            volume.SetMute(1, None)
            tts.speak("Volume muted.")
        elif action == "unmute":
            volume.SetMute(0, None)
            tts.speak("Volume unmuted.")
        elif action == "up":
            current_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current_vol + 0.1), None)
            tts.speak("Volume increased.")
        elif action == "down":
            current_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current_vol - 0.1), None)
            tts.speak("Volume decreased.")
    except Exception as e:
        print(f"Volume control error: {e}")
        tts.speak("Sorry sir, I could not adjust the volume.")


def take_screenshot():
    tts.speak("Taking screenshot.")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    time.sleep(1)
    pyautogui.screenshot(filename)
    tts.speak("Screenshot saved in my project folder.")


def get_weather():
    tts.speak("Checking the local weather, sir.")
    try:
        loc_resp = requests.get("http://ip-api.com/json/", timeout=5)
        loc_data = loc_resp.json()
        lat, lon = loc_data['lat'], loc_data['lon']
        city = loc_data['city']
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=5)
        w_data = weather_resp.json()
        temp = w_data['current_weather']['temperature']
        
        tts.speak(f"It is currently {temp} degrees in {city}.")
    except Exception as e:
        print(f"Weather error: {e}")
        tts.speak("I couldn't fetch the weather right now.")