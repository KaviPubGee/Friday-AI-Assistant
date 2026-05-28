import requests
import xml.etree.ElementTree as ET
import tts

def get_morning_briefing():
    """
    Fetches the top 3 world news headlines from NYT RSS feed and reads them out.
    """
    tts.speak("Fetching your morning briefing, sir.")
    
    url = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # The items are inside the <channel> tag
        channel = root.find("channel")
        items = channel.findall("item")
        
        if not items:
            tts.speak("I couldn't find any news headlines right now.")
            return

        tts.speak("Here are the top world headlines.")
        
        # Read top 3
        count = 0
        for item in items:
            if count >= 3:
                break
            title = item.find("title").text
            print(f"Headline: {title}")
            tts.speak(title)
            count += 1
            
        tts.speak("That concludes the briefing.")
            
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        tts.speak("Sorry sir, I was unable to retrieve the news.")
