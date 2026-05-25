import pyttsx3
import speech_recognition as sr
import datetime
import os
import wikipedia
import pywhatkit
import pyautogui
import pyjokes

ASSISTANT_NAME = "friday"

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio, rate=170, volume=1.0):
    print(f"Friday: {audio}")
    engine.setProperty('rate', rate)  # Adjust the rate of speech
    engine.setProperty('volume', volume)  # Adjust the volume (0.0 to 1.0)
    engine.say(audio)
    engine.runAndWait()

def commands():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold=0.5
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)

    try:
        print("Please wait...")
        query=r.recognize_google(audio, language='en-in')
        print(f"You just said: {query}\n")
    except Exception as e:
        print(e)
        speak("")
        query="none"
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

def time():
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"Its currently {str_time}")
    print(str_time)

def ducks():
    speak("Ducks are cool!")

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
        wishings()
        speak("All systems online. How may i help?")

        while True:
            query = commands().lower()

            if ASSISTANT_NAME in query: #checks for the keyword friday in each query like a wakeup call

                if 'time' in query:
                    time()

                #ducks are the best
                elif 'duck' in query:
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

                elif 'open unity' in query:
                        speak("Opening Unity..")
                        os.startfile("C:\\Program Files\\Unity Hub\\Unity Hub.exe")

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
