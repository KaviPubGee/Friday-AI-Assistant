# ----------------------------
# Imports
# ----------------------------
import json
import requests

import config


def build_ai_prompt(query):
    allowed_apps = list(config.APPS.keys())
    allowed_routines = list(config.ROUTINES.keys())

    return f"""
    You are the intent parser for Friday, a desktop voice assistant.

    Your job:
    Convert the user's command into ONE safe JSON object.

    Allowed intents:
    - open_app
    - run_routine
    - tell_time
    - play_youtube
    - search_wikipedia
    - joke
    - thanks
    - sleep
    - shutdown
    - unknown

    Allowed apps:
    {allowed_apps}

    Allowed routines:
    {allowed_routines}

    Rules:
    1. Return ONLY valid JSON.
    2. Do not explain anything.
    3. Do not run code.
    4. Do not invent app names.
    5. If the user asks to open an app not in allowed apps, return unknown.
    6. If unsure, return unknown.

    Intent priority:
    1. If the command sounds like starting work, coding, game development, productivity, or "get to work", prefer run_routine if a matching routine exists.
    2. Only return "joke" if the user clearly asks for a joke, says "tell me a joke", or says "make me laugh".
    3. Do not return "joke" just because the user says "what do you say".
    4. If the user asks to open an app that is not in the allowed apps list, return unknown.
    5. If unsure, return unknown.

    Examples:
    User: "launch unity for me"
    Response: {{"intent": "open_app", "app": "unity"}}

    User: "start my work setup"
    Response: {{"intent": "run_routine", "routine": "work mode"}}

    User: "put on lofi music"
    Response: {{"intent": "play_youtube", "query": "lofi music"}}

    User: "what time is it"
    Response: {{"intent": "tell_time"}}

    User: "what do you say we get to work"
    Response: {{"intent": "run_routine", "routine": "work mode"}}

    User: "tell me a joke"
    Response: {{"intent": "joke"}}

    User: "what do you say"
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
        content = data["message"]["content"]

        return json.loads(content)

    except Exception as e:
        print("AI brain error:", e)
        return {
            "intent": "unknown",
            "query": query
        }
    

def understand_with_ai(query):
    if not config.AI_BRAIN_ENABLED:
        return {
            "intent": "unknown",
            "query": query
        }

    if config.AI_PROVIDER == "ollama":
        return ask_ollama_for_intent(query)

    return {
        "intent": "unknown",
        "query": query
    }


# ----------------------------
# FIX 1: conversation_history is now passed in so Friday remembers context!
# This means when you say "explain the joke", she knows what joke she told.
# ----------------------------
def chat_with_ai(query, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    # Build the messages list:
    # 1. Start with the system prompt (Friday's personality)
    # 2. Add all the past messages from conversation_history (her memory!)
    # 3. Add the new user message at the end
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
- You never ramble. Short, precise, and impactful responses only — unless the user explicitly asks for detail
- When delivering information, you sound like a briefing, not a chat
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
- Keep responses concise. One to two sentences is ideal unless more detail is asked for.
"""
        }
    ]

    # Add all the past conversation messages (this is Friday's memory!)
    for message in conversation_history:
        messages.append(message)

    # Add the new thing the user just said
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
        # FIX 2: Timeout lowered from 30 to 10 seconds for faster failure
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        reply = data["message"]["content"]

        return reply.strip()

    except Exception as e:
        print("AI chat error:", e)
        return "Sorry sir, my conversational system is having trouble."