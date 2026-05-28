import json
import os

MEMORY_FILE = "memory.json"

# How many messages to keep in memory.
# Keeping too many slows down the AI because it has to read through all of it.
# 40 messages = about 20 back-and-forth exchanges. A good balance.
MAX_MEMORY_MESSAGES = 40


def save_memory(conversation_history):
    """Saves conversation history to a file on the hard drive."""
    # Trim before saving so the file never gets huge
    trimmed = trim_memory(conversation_history)
    with open(MEMORY_FILE, "w") as file:
        json.dump(trimmed, file, indent=2)
    print("Memory saved.")


def load_memory():
    """Loads conversation history from the file. Returns empty list if no file exists."""
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except Exception:
        # If the file is corrupted or empty, start fresh instead of crashing
        print("Memory file could not be read. Starting fresh.")
        return []


def trim_memory(conversation_history):
    """
    Keeps memory from growing forever.
    If we have more than MAX_MEMORY_MESSAGES, we cut the oldest ones.
    We always keep the most recent messages because they are most relevant.
    """
    if len(conversation_history) > MAX_MEMORY_MESSAGES:
        return conversation_history[-MAX_MEMORY_MESSAGES:]
    return conversation_history


def clear_memory():
    """Wipes the memory file completely."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    print("Memory cleared.")