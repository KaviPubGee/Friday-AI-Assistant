import pyttsx3
import speech_recognition as sr
import datetime
import os
import wikipedia
import pywhatkit
import pyautogui
import pyjokes
import time

ASSISTANT_NAME = "friday"

APPS = {
    "unity": r"C:\Program Files\Unity Hub\Unity Hub.exe",
    "opera": r"C:\Users\ASUS\AppData\Local\Programs\Opera GX\opera.exe",
    "spotify": r"C:\Users\ASUS\AppData\Roaming\Spotify\Spotify.exe",
    "vscode": r"C:\Users\ASUS\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}

APP_ALIASES = {
    "visual studio code": "vscode",
    "vs code": "vscode",
    "code": "vscode",
    "unity hub": "unity"
}

ROUTINES = {
    "work mode": ["unity", "vscode"]
}

def speak(audio, rate=145, volume=1.0):
    print(f"Friday: {audio}")

    try:
        speaker = pyttsx3.init('sapi5')
        voices = speaker.getProperty('voices')
        speaker.setProperty('voice', voices[0].id)
        speaker.setProperty('rate', rate)  # Adjust the rate of speech
        speaker.setProperty('volume', volume)  # Adjust the volume (0.0 to 1.0)

        speaker.say(audio)
        speaker.runAndWait()
        speaker.stop()

        del speaker
        time.sleep(1)

    except Exception as e:
        print("Speech error: ", e)

def commands():
    r=sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold=1.2
        r.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("No speech detected")
            return "none"

    try:
        print("Please wait...")
        query=r.recognize_google(audio, language='en-US')
        print(f"You just said: {query}\n")
        return query
    
    except sr.UnknownValueError:
        print("Could not understand audio.")
        query="none"

    except sr.RequestError:
        print("Speech recognition service error")
        return "none"

    return query

def wishings():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        print("Good Morning Sir")
        speak("Good Morning Sir")
    elif hour>=12 and hour<17:
        print("Good Afternoon Sir")
        speak("Good Afternoon Sir")
    else:
        print("Good Evening Sir")
        speak("Good Evening Sir")

def tell_time():
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"Its currently {str_time}")
    print(str_time)

def ducks():
    speak("Ducks are cool!")

def open_app(app_name):
    if app_name in APPS:
        speak(f"Opening {app_name}")
        os.startfile(APPS[app_name])
    else:
        speak(f"I do not have the app location for {app_name} yet. Sorry")

def handle_open_commands(query):
    for app_name in APPS:
        if app_name in query:
            open_app(app_name)
            return
        
    for alias, app_name in APP_ALIASES.items():
        if alias in query:
            open_app(app_name)
            return
        
    speak(f"I do not have that app location yet. Sorry")

def run_routine(routine_name):
    if routine_name not in ROUTINES:
        speak(f"I do not know the routine {routine_name}.")
        return
    
    speak(f"Starting {routine_name}.")

    for app_name in ROUTINES[routine_name]:
        open_app(app_name)

def handle_routine_command(query):
    for routine_name in ROUTINES:
        if routine_name  in query:
            run_routine(routine_name)
            return True
        
    return False

def search(query):
    speak("Searching Wikipedia")

    query = query.replace(ASSISTANT_NAME,  "")
    query = query.replace("search", "")
    query = query.replace("on wikipedia", "")
    query = query.replace("wikipedia", "")
    query = query.strip()

    try:
        results = wikipedia.summary(query, sentences=1)
        speak("According to wikipedia")
        print(results)
        speak(results)
    except:
        speak("Sorry, I could not find anything for that.")
        print("Sorry, I could not find anything for that.")

def play(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("play", "")
    query = query.strip()

    speak('Playing ' + query)
    pywhatkit.playonyt(query)

def typing_mode():
    speak("What should I write, sir?")
    typing = True  # Flag to indicate if typing is ongoing
    while typing:
        write_in_notepad = commands()
        if write_in_notepad == 'stop typing':
            speak("Done, sir.")
            typing = False  # Set the flag to stop typing
        else:
            pyautogui.write(write_in_notepad)

def jokes():
    joke = pyjokes.get_joke()
    print(joke)
    speak(joke)

if __name__ == "__main__":
        speak("Friday is online. What would you like to do today?")

        while True:
            query = commands().lower()

            if query == "none":
                continue

            if ASSISTANT_NAME in query: #checks for the keyword friday in each query like a wakeup call

                if handle_routine_command(query):
                    continue

                if 'time' in query:
                    tell_time()

                #ducks are the best
                elif 'quack' in query:
                    ducks()

                #letting friday sleep and making him power off
                elif 'sleep' in query:
                    speak("All Systems going idle sir...")
                    break
                
                elif 'shutdown' in query:
                    speak("All systems going off line. Goodbye sir")
                    quit()

                #opening apps
                elif 'internet' in query:
                    speak("Opening OperaGX..")
                    os.startfile("C:\\Users\\Kavidu\\Desktop\\Opera GX Browser.lnk")

                elif 'open skype' in query:
                    speak("Opening Skype..")
                    os.startfile("C:\\Program Files (x86)\\Microsoft\\Skype for Desktop\\Skype.exe")

                elif 'open' in query:
                        handle_open_commands(query)

                elif 'open pycharm' in query:
                        speak("Opening Pycharm..")
                        os.startfile("C:\\Program Files\\JetBrains\\PyCharm Community Edition 2021.1.3\\bin\\pycharm64.exe")

                elif 'open meeting' in query:
                        speak("Opening Zoom..")
                        os.startfile("C:\\Users\\Kavidu\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe")

                elif 'thank you' in query:
                    speak("Happy to help you sir")
                    print("Happy to help you sir")

                #searching things
                elif 'search' in query:
                    search(query)

                elif 'play' in query:
                    play(query)

                elif 'type' in query:
                    typing_mode()

                elif 'joke' in query:
                    jokes()

            else:
                print("Wake word not detected")
