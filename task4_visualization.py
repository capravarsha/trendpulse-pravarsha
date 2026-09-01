import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def load_latest_csv():

    data_folder = Path("data")

    csv_files = list(
        data_folder.glob("trends_cleaned_*.csv")
    )

    if not csv_files:
        print("No cleaned CSV file found.")
        return None

    latest_file = max(
        csv_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Reading: {latest_file}")

    return pd.read_csv(latest_file)


def main():

    df = load_latest_csv()

    if df is None:
        return

    # Create output folder for charts
    charts_folder = Path("charts")
    charts_folder.mkdir(exist_ok=True)

    # -----------------------------------------
    # Chart 1: Number of stories per category
    # -----------------------------------------

    category_counts = df["category"].value_counts()

    plt.figure(figsize=(10, 6))

    category_counts.plot(
        kind="bar"
    )

    plt.title("Number of Trending Stories by Category")
    plt.xlabel("Category")
    plt.ylabel("Number of Stories")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        charts_folder / "stories_by_category.png"
    )

    # plt.show()

    plt.close()

    # -----------------------------------------
    # Chart 2: Average score by category
    # -----------------------------------------

    average_scores = (
        df.groupby("category")["score"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    average_scores.plot(
        kind="bar"
    )

    plt.title("Average Score by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Score")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        charts_folder / "average_score_by_category.png"
    )

    # plt.show()

    plt.close()

    # -----------------------------------------
    # Chart 3: Comments by category
    # -----------------------------------------

    average_comments = (
        df.groupby("category")["num_comments"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    average_comments.plot(
        kind="bar"
    )

    plt.title("Average Comments by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Comments")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        charts_folder / "average_comments_by_category.png"
    )

    # plt.show()

    plt.close()

    # -----------------------------------------
    # Chart 4: Score distribution
    # -----------------------------------------

    plt.figure(figsize=(10, 6))

    df["score"].plot(
        kind="hist",
        bins=20
    )

    plt.title("Distribution of Story Scores")
    plt.xlabel("Score")
    plt.ylabel("Number of Stories")
    plt.tight_layout()

    plt.savefig(
        charts_folder / "score_distribution.png"
    )

    # plt.show()

    plt.close()

    print("\nVisualization completed.")
    print("Charts saved in the charts/ folder.")


if __name__ == "__main__":
    main()
