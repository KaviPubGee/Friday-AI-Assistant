# Friday - Personal Voice Assistant

Friday is a Python-based personal voice assistant inspired by fictional AI assistants like J.A.R.V.I.S.  
The goal of this project is to create a voice-controlled desktop assistant that can listen, speak, open apps, run routines, and help with daily computer tasks.

## Current Features

- Voice recognition
- Text-to-speech replies
- Basic wake word detection
- Tells the current time
- Opens selected desktop apps
- Plays videos/music on YouTube
- Searches Wikipedia
- Tells programming jokes
- Basic typing assistant mode

## Planned Features

- Custom voice routines  
  Example: "Friday, let's get to work" opens Unity, VS Code, Spotify, and project folders.

- Gaming mode  
  Example: "Friday, gaming time" closes approved background apps and opens a game.

- Better wake word handling  
  Friday should only respond when directly called.

- Safer app control  
  Only approved apps should be opened or closed.

- Memory for custom phrases  
  Teach Friday what a phrase should do, then use it later.

- Floating assistant bubble UI  
  A small voice bubble that appears while Friday is listening or speaking.

## Tech Stack

- Python
- pyttsx3
- SpeechRecognition
- pywhatkit
- pyautogui
- wikipedia
- pyjokes
