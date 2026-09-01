import json
import csv
from pathlib import Path
from datetime import datetime


def load_latest_json():

    data_folder = Path("data")

    json_files = list(data_folder.glob("trends_*.json"))

    if not json_files:
        print("No JSON file found in data folder.")
        return None

    # Select the newest JSON file
    latest_file = max(
        json_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Reading: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_story(story):

    cleaned_story = {}

    cleaned_story["post_id"] = story.get("post_id")

    # Remove extra spaces from titles
    title = story.get("title", "")
    cleaned_story["title"] = " ".join(title.split())

    cleaned_story["category"] = story.get("category")

    # Convert numeric values safely
    try:
        cleaned_story["score"] = int(story.get("score", 0))
    except (ValueError, TypeError):
        cleaned_story["score"] = 0

    try:
        cleaned_story["num_comments"] = int(
            story.get("num_comments", 0)
        )
    except (ValueError, TypeError):
        cleaned_story["num_comments"] = 0

    author = story.get("author")

    if author is None or str(author).strip() == "":
        cleaned_story["author"] = "Unknown"
    else:
        cleaned_story["author"] = str(author).strip()

    cleaned_story["collected_at"] = story.get("collected_at")

    return cleaned_story


def main():

    stories = load_latest_json()

    if stories is None:
        return

    cleaned_stories = []

    for story in stories:

        cleaned_story = clean_story(story)

        # Keep only records with required information
        if (
            cleaned_story["post_id"] is not None
            and cleaned_story["title"]
            and cleaned_story["category"]
        ):
            cleaned_stories.append(cleaned_story)

    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    date_string = datetime.now().strftime("%Y%m%d")

    output_file = data_folder / f"trends_cleaned_{date_string}.csv"

    fieldnames = [
        "post_id",
        "title",
        "category",
        "score",
        "num_comments",
        "author",
        "collected_at"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(cleaned_stories)

    print(
        f"Processed {len(cleaned_stories)} stories. "
        f"Saved to {output_file}"
    )


if __name__ == "__main__":
    main()