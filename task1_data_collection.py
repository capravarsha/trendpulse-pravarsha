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


categories = {
    "technology": [
        "AI", "software", "tech", "code", "computer",
        "data", "cloud", "API", "GPU", "LLM"
    ],

    "worldnews": [
        "war", "government", "country", "president",
        "election", "climate", "attack", "global"
    ],

    "sports": [
        "NFL", "NBA", "FIFA", "sport", "game", "team",
        "player", "league", "championship"
    ],

    "science": [
        "research", "study", "space", "physics", "biology",
        "discovery", "NASA", "genome"
    ],

    "entertainment": [
        "movie", "film", "music", "Netflix", "game", "book",
        "show", "award", "streaming"
    ]
}


def find_category(title):
    """Find the first category whose keyword appears in the title."""

    title_lower = title.lower()

    for category, keywords in categories.items():
        for keyword in keywords:
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

    # Store the number collected in each category
    category_counts = {
        category: 0
        for category in categories
    }

    # Process each category
    for category in categories:

        for story_id in story_ids:

            # Stop after collecting 25 stories for this category
            if category_counts[category] >= 25:
                break

            story = fetch_story(story_id)

            if story is None:
                continue

            title = story.get("title", "")

            if not title:
                continue

            matched_category = find_category(title)

            if matched_category != category:
                continue

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

        # Wait two seconds between category loops
        time.sleep(2)

    # Create data directory
    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    # Create today's filename
    date_string = datetime.now().strftime("%Y%m%d")

    output_file = data_folder / f"trends_{date_string}.json"

    # Save data to JSON
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            collected_stories,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Collected {len(collected_stories)} stories. "
        f"Saved to {output_file}"
    )


if __name__ == "__main__":
    main()