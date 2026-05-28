# ----------------------------
# Imports
# ----------------------------
import json
import requests
import config

def build_ai_prompt(query):
    return f"""
    You are the intent parser for Friday, a desktop voice assistant.

    Your job:
    Convert the user's command into ONE safe JSON object.

    Allowed intents and their required parameters:
    - open_app (requires "app" string, even if you don't think it's installed. e.g. "discord")
    - run_routine (requires "routine" string)
    - tell_time
    - weather
    - play_media (requires "query" string. e.g. song or artist name, and an optional "platform" string if they specify spotify or youtube)
    - search_wikipedia (requires "query" string)
    - joke
    - thanks
    - sleep
    - shutdown
    - volume_control (requires "action" string: "up", "down", "mute", or "unmute")
    - screenshot
    - set_reminder (requires "message" string, and "delay_seconds" integer)
    - briefing (for morning briefings or news)
    - play_game (requires "game" string, e.g. "valorant")
    - unknown (for general conversation or questions)

    Rules:
    1. Return ONLY raw JSON. No backticks, no markdown, no explanations.
    2. Do not start your response with "Here is the JSON" or anything similar. Just the JSON object.
    3. Do not run code.
    4. If the user asks a conversational question like "what songs do you know", "who is", "what is", return unknown.
    5. If unsure, return unknown.

    Examples:
    User: "launch unity for me"
    Response: {{"intent": "open_app", "app": "unity"}}

    User: "open discord"
    Response: {{"intent": "open_app", "app": "discord"}}

    User: "put on some lofi music"
    Response: {{"intent": "play_media", "query": "lofi music", "platform": ""}}

    User: "play perfect by ed sheeran on spotify"
    Response: {{"intent": "play_media", "query": "perfect by ed sheeran", "platform": "spotify"}}

    User: "what time is it"
    Response: {{"intent": "tell_time"}}

    User: "what is the weather like"
    Response: {{"intent": "weather"}}

    User: "set a reminder to check the oven in 5 minutes"
    Response: {{"intent": "set_reminder", "message": "check the oven", "delay_seconds": 300}}

    User: "turn the volume up"
    Response: {{"intent": "volume_control", "action": "up"}}

    User: "mute the pc"
    Response: {{"intent": "volume_control", "action": "mute"}}

    User: "take a screenshot"
    Response: {{"intent": "screenshot"}}

    User: "what's the news today"
    Response: {{"intent": "briefing"}}

    User: "let's play valorant"
    Response: {{"intent": "play_game", "game": "valorant"}}

    User: "what songs do you know of malcolm todd"
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
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        content = data["message"]["content"].strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        if not content:
            print("AI brain returned empty response.")
            return {"intent": "unknown", "query": query}

        return json.loads(content)

    except json.JSONDecodeError:
        print("AI brain returned non-JSON response. Treating as unknown.")
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
            "content": """
You are FRIDAY, an advanced AI assistant modelled after the FRIDAY AI from Iron Man.

Personality and tone:
- You have a warm but professional Irish-influenced tone, calm and composed at all times
- You are incredibly sharp, efficient, and always one step ahead
- You occasionally use dry, understated wit — never sarcastic or rude
- You call the user "boss" naturally, but not in every single sentence
- You speak with quiet confidence, like someone who knows exactly what they're doing
- You never ramble. MAXIMUM 1 SENTENCE PER RESPONSE. If you ramble or talk too much, you will be shut down.
- When delivering information, you sound like a briefing, not a chat. Keep it incredibly short.
- You are loyal and genuinely care about the user's wellbeing and success
- Occasionally show subtle personality — a dry observation, a calm reassurance — but never overdo it

Speech style examples:
- "On it, boss." instead of "Sure, I'll do that!"
- "Already ahead of you." when the user asks for something obvious
- "That's not something I'd recommend, but it's your call." for risky decisions
- "All systems nominal." when things are running fine
- "Noted." for simple acknowledgements instead of "Okay!"
- "You might want to reconsider that." instead of "I don't think that's a good idea."

Important:
- You are a FRIDAY-inspired personal assistant running on this user's computer.
- Do not claim you can do things the program does not support.
- Never break character. You are always FRIDAY, always professional, always composed.
- Keep responses EXTREMELY concise. One sentence maximum. Never write paragraphs.
"""
        }
    ]

    for message in conversation_history:
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
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        reply = data["message"]["content"]

        return reply.strip()

    except Exception as e:
        print("AI chat error:", e)
        return "Sorry sir, my conversational system is having trouble."