# ----------------------------
# Imports
# ----------------------------
import json
import requests
import config

def build_ai_prompt(query):
    return f"""
You are the intent parser for Friday, a desktop voice assistant.

Your ONLY job: Convert the user's voice command into ONE raw JSON object.

Allowed intents:
- open_app       → requires "app" string  (e.g. "discord", "spotify", "chrome", "valorant")
- run_routine    → requires "routine" string
- tell_time
- weather
- play_media     → requires "query" string (song/artist), optional "platform" string ("spotify" or "youtube" if stated)
- search_wikipedia → requires "query" string
- joke
- thanks
- sleep
- shutdown
- volume_control → requires "action": "up" | "down" | "mute" | "unmute"
- screenshot
- set_reminder   → requires "message" string, "delay_seconds" integer
- briefing
- play_game      → requires "game" string — ONLY use this if user explicitly says they want to play/launch a GAME (e.g. valorant, minecraft, fortnite)
- unknown        → for general questions and conversation

CRITICAL RULES:
1. Return ONLY raw JSON. No backticks, no markdown, no explanation text.
2. "play_media" is for MUSIC/SONGS. "open_app" is for opening software.
3. If the user says "play valorant" or "launch valorant", use play_game. If they ask about valorant, use unknown.
4. If the user says "play [song/artist name]" or "put on [music]", use play_media.
5. Never return play_game for music requests.
6. If unsure whether it's music or a game, prefer play_media.

Examples:
User: "play run it by drake"
Response: {{"intent": "play_media", "query": "run it by drake", "platform": ""}}

User: "put on some lofi"
Response: {{"intent": "play_media", "query": "lofi music", "platform": ""}}

User: "play perfect by ed sheeran on spotify"
Response: {{"intent": "play_media", "query": "perfect by ed sheeran", "platform": "spotify"}}

User: "play a song like run it"
Response: {{"intent": "play_media", "query": "run it", "platform": ""}}

User: "can you play me a song"
Response: {{"intent": "play_media", "query": "", "platform": ""}}

User: "let's play valorant"
Response: {{"intent": "play_game", "game": "valorant"}}

User: "launch valorant"
Response: {{"intent": "play_game", "game": "valorant"}}

User: "open discord"
Response: {{"intent": "open_app", "app": "discord"}}

User: "launch unity for me"
Response: {{"intent": "open_app", "app": "unity"}}

User: "what time is it"
Response: {{"intent": "tell_time"}}

User: "what's the weather"
Response: {{"intent": "weather"}}

User: "set a reminder to check the oven in 5 minutes"
Response: {{"intent": "set_reminder", "message": "check the oven", "delay_seconds": 300}}

User: "remind me to drink water in 2 minutes"
Response: {{"intent": "set_reminder", "message": "drink water", "delay_seconds": 120}}

User: "turn the volume up"
Response: {{"intent": "volume_control", "action": "up"}}

User: "mute"
Response: {{"intent": "volume_control", "action": "mute"}}

User: "take a screenshot"
Response: {{"intent": "screenshot"}}

User: "what's the news today"
Response: {{"intent": "briefing"}}

User: "what songs do you know of malcolm todd"
Response: {{"intent": "unknown"}}

User: "who is elon musk"
Response: {{"intent": "unknown"}}

User command:
"{query}"
"""

def ask_ollama_for_intent(query):
    prompt = build_ai_prompt(query)

    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()

        data = response.json()
        content = data["message"]["content"].strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            content = "\n".join(lines).strip()

        if not content:
            print("AI brain returned empty response.")
            return {"intent": "unknown", "query": query}

        # Find the JSON object in the response (in case there's extra text)
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]

        return json.loads(content)

    except json.JSONDecodeError as e:
        print(f"AI brain returned non-JSON: {e}. Raw: {content[:200]}")
        return {"intent": "unknown", "query": query}

    except Exception as e:
        print("AI brain error:", e)
        return {
            "intent": "unknown",
            "query": query
        }

def understand_with_ai(query):
    if not config.AI_BRAIN_ENABLED:
        return {"intent": "unknown", "query": query}

    if config.AI_PROVIDER == "ollama":
        return ask_ollama_for_intent(query)

    return {"intent": "unknown", "query": query}


def chat_with_ai(query, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    messages = [
        {
            "role": "system",
            "content": """You are FRIDAY, a personal AI assistant inspired by Iron Man's FRIDAY.

Personality:
- Calm, professional, Irish-influenced tone
- Dry understated wit, never sarcastic
- Call the user "boss" occasionally, not every sentence
- Quiet confidence

Speech rules — CRITICAL:
- MAXIMUM 1 SHORT SENTENCE per response. Never more.
- No bullet points. No lists. No paragraphs.
- Sound like a military briefing, not a friend chatting.
- If you have nothing useful to say, say "Noted." or "Got it, boss."

Examples of correct responses:
- "On it, boss."
- "Already ahead of you."
- "That's not something I'd recommend."
- "All systems nominal."
- "Noted."
- "Malcolm Todd is a singer-songwriter known for indie folk music."

NEVER write more than one sentence. NEVER explain yourself at length."""
        }
    ]

    for message in conversation_history[-10:]:  # limit context window
        messages.append(message)

    messages.append({
        "role": "user",
        "content": query
    })

    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()

        data = response.json()
        reply = data["message"]["content"]

        # Trim to first sentence only if model ignores instructions
        reply = reply.strip()
        for punct in [". ", "! ", "? "]:
            if punct in reply:
                reply = reply.split(punct)[0] + punct.strip()
                break

        return reply

    except Exception as e:
        print("AI chat error:", e)
        return "My conversational system is offline, boss."