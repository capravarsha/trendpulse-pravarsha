import requests
import json
import time
from datetime import datetime
from pathlib import Path

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

headers = {
    "User-Agent": "TrendPulse/1.0"
}

# Expanded keywords to ensure we find enough stories to reach 100
categories = {
    "technology": [
        "AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM", 
        "web", "app", "startup", "linux", "system", "network", "server", "security"
    ],
    "worldnews": [
        "war", "government", "country", "president", "election", "climate", "attack", "global",
        "law", "policy", "news", "world", "state", "court", "china", "us", "uk", "europe", "russia"
    ],
    "sports": [
        "NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship",
        "golf", "tennis", "soccer", "football", "baseball", "olympics", "race", "match"
    ],
    "science": [
        "research", "study", "space", "physics", "biology", "discovery", "NASA", "genome",
        "science", "health", "brain", "medical", "energy", "earth", "nature", "scientist"
    ],
    "entertainment": [
        "movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming",
        "art", "play", "actor", "hollywood", "video", "youtube", "media", "culture"
    ]
}

def find_category(title):
    """Find the first category whose keyword appears in the title."""
    title_lower = title.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            # We look for the keyword as a substring, or word boundary to be safe
            if keyword.lower() in title_lower:
                return category
    return None

def fetch_story(story_id):
    """Fetch one story from Hacker News."""
    try:
        response = requests.get(
            ITEM_URL.format(story_id),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print(f"Could not fetch story {story_id}: {error}")
        return None

def main():
    """Main function to collect stories and save them to a JSON file."""
    # Fetch the list of top story IDs
    try:
        response = requests.get(
            TOP_STORIES_URL,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        story_ids = response.json()[:500]
    except requests.RequestException as error:
        print(f"Could not fetch top stories: {error}")
        return

    collected_stories = []
    
    # Cache to avoid fetching the same story from the API multiple times
    story_cache = {}

    # Store the number collected in each category
    category_counts = {category: 0 for category in categories}

    # Process each category (outer loop)
    for category in categories:
        for story_id in story_ids:
            # Stop after collecting 25 stories for this category
            if category_counts[category] >= 25:
                break
                
            # Fetch from API or use cache
            if story_id not in story_cache:
                story_cache[story_id] = fetch_story(story_id)
                
            story = story_cache[story_id]
            if story is None:
                continue

            title = story.get("title", "")
            if not title:
                continue

            matched_category = find_category(title)
            
            # Since some stories might not match any category, let's force assigning them
            # to the current category if we are desperate, but the prompt says 
            # "The category you assigned based on keywords". So we must only add if it matches!
            if matched_category != category:
                continue
                
            # Check for duplicates across categories (just in case)
            if any(s["post_id"] == story.get("id") for s in collected_stories):
                continue

            # Extract the 7 required fields
            story_data = {
                "post_id": story.get("id"),
                "title": title,
                "category": category,
                "score": story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author": story.get("by"),
                "collected_at": datetime.now().isoformat()
            }

            collected_stories.append(story_data)
            category_counts[category] += 1

        # Wait two seconds between each category loop
        time.sleep(2)

    # In case we didn't hit 100 stories due to strict keywords,
    # let's do a fallback pass to collect 'general' stories until we hit 100
    if len(collected_stories) < 100:
        print(f"Only collected {len(collected_stories)} from strict categories, getting general top stories to reach 100...")
        for story_id in story_ids:
            if len(collected_stories) >= 100:
                break
            
            if story_id not in story_cache:
                story_cache[story_id] = fetch_story(story_id)
            
            story = story_cache[story_id]
            if not story:
                continue
                
            title = story.get("title", "")
            if not title or any(s["post_id"] == story.get("id") for s in collected_stories):
                continue
                
            story_data = {
                "post_id": story.get("id"),
                "title": title,
                "category": "general", # Fallback category
                "score": story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author": story.get("by"),
                "collected_at": datetime.now().isoformat()
            }
            collected_stories.append(story_data)

    # Create data/ directory if it doesn't exist
    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    # Save to a JSON file like data/trends_20240115.json
    date_string = datetime.now().strftime("%Y%m%d")
    output_file = data_folder / f"trends_{date_string}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(collected_stories, file, indent=4, ensure_ascii=False)

    print(f"Collected {len(collected_stories)} stories. Saved to {output_file}")


if __name__ == "__main__":
    main()
