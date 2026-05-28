# Friday - Personal AI Voice Assistant

Friday is an advanced, fully AI-driven Python-based personal voice assistant inspired by fictional AI assistants like J.A.R.V.I.S. and F.R.I.D.A.Y.
Unlike rigid, keyword-based scripts, Friday uses a local Large Language Model (Ollama) to dynamically parse context, intents, and conversational memory, making her a truly intelligent desktop assistant.

## Features

- **100% AI-Driven Brain**: Uses a local LLM to understand commands contextually without needing exact keywords.
- **Persistent Memory**: Remembers past conversations, context, and jokes in a persistent `memory.json` file.
- **Dynamic App Locator**: Ask her to open an app, and she will recursively search your PC for the `.exe`, save its path, and launch it instantly.
- **Media Player**: Ask her to play a song, and she will intelligently ask "Spotify or YouTube?". She can autoplay your desktop Spotify or search YouTube.
- **PC Controls**: Native support for taking screenshots and controlling your PC's volume (Mute, Up, Down).
- **Background Reminders**: Set timers and reminders that run asynchronously without freezing her ability to listen to you.
- **Morning Briefings**: On startup, she can fetch the top world news headlines and read them to you.
- **Live Weather**: Uses Open-Meteo and IP-based geolocation to give you accurate, live local weather updates.
- **Advanced Speech Tech**: Uses `faster-whisper` for incredibly crisp, offline speech-to-text with hallucination filters, and Microsoft's `edge-tts` for a high-quality, natural-sounding voice.

## Prerequisites

Before running Friday, you need to have [Ollama](https://ollama.ai/) installed and running locally with the `llama3.2:3b` model downloaded.
```bash
ollama run llama3.2:3b
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Friday-AI-Assistant.git
cd Friday-AI-Assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Run Friday:
```bash
python main.py
```

## Tech Stack

- **Python 3.11+**
- **Ollama** (Local LLM intent parsing & chat)
- **faster-whisper** (Offline Speech-to-Text)
- **edge-tts** (High-quality Neural Text-to-Speech)
- **pycaw** (Windows Volume Control)
- **pyautogui** (Screenshots & Automation)
- **requests** (Weather & News API)
- **SpeechRecognition** (Microphone handling & ambient noise calibration)
