import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Directory where the BinDiff results are stored
bindiff_results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bindiff_results')


# Function to extract function scores from a .sqlite file
def query_function_scores(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # SQL query to get all the similarity scores
    query = "SELECT similarity FROM main.function"
    cursor.execute(query)
    scores = cursor.fetchall()
    conn.close()

    return [score[0] for score in scores]


# Aggregate all function similarity scores across all comparisons
def aggregate_all_scores(directory):
    all_scores = []
    for file in os.listdir(directory):
        if file.endswith(".BinDiff"):
            sqlite_file = os.path.join(directory, file)
            scores = query_function_scores(sqlite_file)
            all_scores.extend(scores)
    return all_scores


# Plot the normal distribution of the similarity scores
def plot_distribution(all_scores):
    if not all_scores:
        print("No data to plot!")
        return

    # Creating a professional plot
    plt.figure(figsize=(14, 8))

    # Plotting the histogram with KDE
    sns.histplot(all_scores, kde=True, color='darkblue', bins=30, line_kws={'linewidth': 2.5})

    # Labels and Title
    plt.xlabel('BinDiff Similarity Score', fontsize=18)
    plt.ylabel('Frequency', fontsize=18)
    plt.title('Distribution of BinDiff Similarity Scores Across Compiler Configurations', fontsize=20, pad=20)

    # Adjusting ticks
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    # Saving the plot as a high-resolution PNG
    plt.savefig('BinDiff_Similarity_Distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


# Main Execution
if __name__ == "__main__":
    all_scores = aggregate_all_scores(bindiff_results_dir)
    plot_distribution(all_scores)