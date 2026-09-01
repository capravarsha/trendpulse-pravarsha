import pandas as pd
import numpy as np
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

    print("\n===== TrendPulse Analysis =====")

    # Basic information
    print("\nTotal stories:")
    print(len(df))

    # Number of stories in each category
    print("\nStories by category:")
    category_counts = df["category"].value_counts()
    print(category_counts)

    # Average score by category
    print("\nAverage score by category:")
    average_scores = (
        df.groupby("category")["score"]
        .mean()
        .sort_values(ascending=False)
    )
    print(average_scores.round(2))

    # Average comments by category
    print("\nAverage comments by category:")
    average_comments = (
        df.groupby("category")["num_comments"]
        .mean()
        .sort_values(ascending=False)
    )
    print(average_comments.round(2))

    # Highest scoring story
    highest_score_index = df["score"].idxmax()
    highest_score_story = df.loc[highest_score_index]

    print("\nHighest scoring story:")
    print(highest_score_story["title"])
    print("Score:", highest_score_story["score"])
    print("Category:", highest_score_story["category"])

    # Most commented story
    most_commented_index = df["num_comments"].idxmax()
    most_commented_story = df.loc[most_commented_index]

    print("\nMost commented story:")
    print(most_commented_story["title"])
    print("Comments:", most_commented_story["num_comments"])
    print("Category:", most_commented_story["category"])

    # NumPy analysis
    scores = df["score"].to_numpy()

    print("\nScore statistics:")
    print("Minimum:", np.min(scores))
    print("Maximum:", np.max(scores))
    print("Mean:", round(np.mean(scores), 2))
    print("Median:", np.median(scores))

    # Engagement calculation
    df["engagement"] = (
        df["score"] + df["num_comments"]
    )

    top_engagement = df.nlargest(
        5,
        "engagement"
    )

    print("\nTop 5 stories by engagement:")

    for _, story in top_engagement.iterrows():

        print(
            f"- {story['title']} "
            f"({story['category']}) "
            f"Engagement: {story['engagement']}"
        )

    # Save analysis summary
    analysis_folder = Path("data")
    analysis_folder.mkdir(exist_ok=True)

    summary = {
        "total_stories": len(df),
        "category_counts": category_counts.to_dict(),
        "average_scores": average_scores.round(2).to_dict(),
        "average_comments": average_comments.round(2).to_dict(),
        "highest_score": int(df["score"].max()),
        "highest_comments": int(df["num_comments"].max()),
        "mean_score": float(np.mean(scores)),
        "median_score": float(np.median(scores))
    }

    summary_df = pd.DataFrame([summary])

    summary_df.to_csv(
        analysis_folder / "analysis_summary.csv",
        index=False
    )

    print("\nAnalysis completed.")
    print("Saved summary to data/analysis_summary.csv")


if __name__ == "__main__":
    main()