# ----------------------------
# Imports
# ----------------------------
import config
import ai_brain


# ----------------------------
# Words
# ----------------------------
OPEN_WORDS = ["open", "launch", "start", "run", "pull up"]
PLAY_WORDS = ["play", "put on", "start playing"]
SEARCH_WORDS = ["search", "look up", "find", "wikipedia"]
THANK_WORDS = ["thank you", "thanks", "cheers"]
JOKE_WORDS = ["joke", "make me laugh"]
TIME_WORDS = ["time", "what time"]
SLEEP_WORDS = ["sleep", "go idle", "stand by"]
SHUTDOWN_WORDS = ["shutdown", "shut down", "power off"]


def find_app(query):
    for app_name in config.APPS:
        if app_name in query:
            return app_name
        
    for alias, app_name in config.APP_ALIASES.items():
        if alias in query:
            return app_name
        
    return None


def find_routine(query):
    for routine_name in config.ROUTINES:
        if routine_name in query:
            return routine_name
        
    for alias, routine_name in config.ROUTINE_ALIASES.items():
        if alias in query:
            return routine_name
        
    return None


def understand_command(query):
    """
    Converts a user's spoken command into a safe intent dictionary.
    """

    routine = find_routine(query)

    if routine:
        return {
            "intent": "run_routine",
            "routine": routine
        }
    
    if contains_any(query, OPEN_WORDS):
        app = find_app(query)

        if app:
            return {
                "intent": "open_app",
                "app": app
            }
        
    if contains_any(query, TIME_WORDS):
        return {
            "intent": "tell_time"
        }
    
    if "duck" in query or "ducks" in query or "quack" in query:
        return {
            "intent" : "ducks"
        }
    
    if contains_any(query, SLEEP_WORDS):
        return {
            "intent": "sleep"
        }
    
    if contains_any(query, SHUTDOWN_WORDS):
        return {
            "intent": "shutdown"
        }
    
    if contains_any(query, THANK_WORDS):
        return {
            "intent": "thanks"
        }
    
    if contains_any(query, SEARCH_WORDS):
        return {
            "intent": "search_wikipedia",
            "query": query
        }
    
    if contains_any(query, PLAY_WORDS):
        return {
            "intent": "play_youtube",
            "query": query
        }
    
    if "type" in query:
        return {
            "intent": "typing_mode"
        }

    if contains_any(query, JOKE_WORDS):
        return {
            "intent": "joke"
        }

    print("Rule brain could not understand. Asking AI brain...")

    ai_command = ai_brain.understand_with_ai(query)
    validated_command = validate_intent(ai_command)

    print("AI brain returned: ", ai_command)
    print("Validated command: ", validated_command)

    return validate_intent(ai_command)


def contains_any(query, words):
    """
    Checks if the query contains any phrase from a list
    """
    for word in words:
        if word in query:
            return True
        
    return False


def validate_intent(command):
    if not isinstance(command, dict):
        return{"intent": "unknown"}
    
    intent = command.get("intent")

    if intent not in config.ALLOWED_INTENTS:
        return {"intent": "unknown"}
    
    if intent == "open_app":
        app = command.get("app")

        if app not in config.APPS:
            return{"intent": "unknown"}
        
    if intent == "run_routine":
        routine = command.get("routine")

        if routine not in config.ROUTINES:
            return{"intent": "unknown"}
        
    return command