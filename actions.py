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

from pycaw.pycaw import AudioUtilities

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
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    tts.speak(f"It's {current_time}.")
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
        tts.speak(f"I do not have {app_name} on record.")


def find_and_save_app(app_name):
    tts.speak(f"Locating {app_name}, give me a moment.")
    print(f"Searching for {app_name}.exe...")

    search_paths = [
        os.environ.get("PROGRAMFILES", "C:\\Program Files"),
        os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), ""),
        os.path.join(os.environ.get("APPDATA", ""), ""),
    ]

    target = f"{app_name.lower().replace(' ', '')}.exe"
    target_with_spaces = f"{app_name.lower()}.exe"

    found_path = None

    for path in search_paths:
        if not path or not os.path.exists(path):
            continue
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
        tts.speak("Found it.")
        print(f"Found at: {found_path}")
        config.APPS[app_name] = found_path

        import json
        try:
            with open("apps.json", "w") as f:
                json.dump(config.APPS, f, indent=4)
        except Exception:
            pass

        open_app(app_name)
    else:
        tts.speak(f"I could not find {app_name}.")


def handle_open_command(app_name):
    # Normalise
    app_name = app_name.lower().strip()

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

    # Dynamic search
    find_and_save_app(app_name)


def run_routine(routine_name):
    routine_name = routine_name.lower().strip()
    if routine_name not in config.ROUTINES:
        tts.speak(f"No routine called {routine_name} on record.")
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
    tts.speak("Searching.")
    query = query.strip()
    try:
        results = wikipedia.summary(query, sentences=1)
        print(results)
        tts.speak(results)
    except Exception:
        tts.speak("Nothing found for that.")


def play_on_spotify(query):
    """
    Opens Spotify desktop app to the search result and auto-plays the top track.
    Uses the spotify: URI scheme — no API key required.
    """
    tts.speak(f"Playing {query} on Spotify.")

    # Open Spotify with the search URI
    search_uri = f"spotify:search:{query.replace(' ', '%20')}"
    os.system(f"start {search_uri}")

    # Give Spotify time to open / come to foreground
    time.sleep(3.5)

    # Navigate to the first track in results and play it.
    # Spotify's search page focuses the first item after Tab from the search bar.
    # We press Tab twice to skip the search bar controls, then Enter to play.
    pyautogui.hotkey("alt", "1")   # Switch to Songs tab in Spotify search (shortcut)
    time.sleep(0.5)

    # Use Tab to reach first result, then Enter to play
    for _ in range(3):
        pyautogui.press("tab")
        time.sleep(0.15)

    pyautogui.press("enter")
    time.sleep(0.5)


def play_on_youtube(query):
    tts.speak(f"Playing {query} on YouTube.")
    pywhatkit.playonyt(query)


def play_media(query, platform=""):
    """
    Asks user for platform if not already specified, then plays.
    """
    if not platform:
        tts.speak(f"Spotify or YouTube?")
        response = stt.listen_for_command()

        if response == "none":
            tts.speak("Cancelled.")
            return

        response = response.lower()
        if "spotify" in response:
            platform = "spotify"
        elif "youtube" in response or "you tube" in response:
            platform = "youtube"
        else:
            tts.speak("Didn't catch that. Cancelled.")
            return

    platform = platform.lower()

    if "spotify" in platform:
        play_on_spotify(query)
    elif "youtube" in platform:
        play_on_youtube(query)
    else:
        tts.speak("Cancelled.")


def typing_mode():
    tts.speak("What should I type?")
    while True:
        text_to_type = stt.listen_for_command()
        if text_to_type == "none":
            continue
        if "stop" in text_to_type or "done" in text_to_type:
            tts.speak("Done.")
            break
        pyautogui.write(text_to_type, interval=0.05)


def volume_control(action):
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume

        if action == "mute":
            volume.SetMute(1, None)
            tts.speak("Muted.")
        elif action == "unmute":
            volume.SetMute(0, None)
            tts.speak("Unmuted.")
        elif action == "up":
            current_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current_vol + 0.1), None)
            tts.speak("Volume up.")
        elif action == "down":
            current_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current_vol - 0.1), None)
            tts.speak("Volume down.")
    except Exception as e:
        print(f"Volume error: {e}")
        tts.speak("Volume adjustment failed.")


def _get_desktop_path():
    """Gets the real Desktop path via Windows Registry (handles OneDrive redirection)."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        desktop, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        if os.path.isdir(desktop):
            return desktop
    except Exception:
        pass
    # Fallback: try standard paths
    for candidate in [
        os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Desktop"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
    ]:
        if os.path.isdir(candidate):
            return candidate
    # Last resort: save next to main.py
    return os.path.dirname(os.path.abspath(__file__))


def take_screenshot():
    tts.speak("Screenshot taken.")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop = _get_desktop_path()
    filename = os.path.join(desktop, f"screenshot_{timestamp}.png")
    time.sleep(0.5)
    pyautogui.screenshot(filename)
    tts.speak(f"Saved to your Desktop.")
    print(f"Screenshot saved: {filename}")


def get_weather():
    try:
        loc_resp = requests.get("http://ip-api.com/json/", timeout=5)
        loc_data = loc_resp.json()

        if loc_data.get("status") != "success":
            tts.speak("Could not determine your location.")
            return

        lat = loc_data["lat"]
        lon = loc_data["lon"]
        city = loc_data["city"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_resp = requests.get(weather_url, timeout=5)
        w_data = weather_resp.json()
        temp = w_data["current_weather"]["temperature"]
        unit = "Celsius"

        tts.speak(f"{temp} degrees {unit} in {city}.")
    except Exception as e:
        print(f"Weather error: {e}")
        tts.speak("Weather check failed.")