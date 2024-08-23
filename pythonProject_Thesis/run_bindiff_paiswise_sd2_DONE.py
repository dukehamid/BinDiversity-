import sqlite3
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Directory where the BinDiff results are stored
bindiff_results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bindiff_results')


# Function to extract function scores from a .BinDiff file
def query_function_scores(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # SQL query to get all the similarity scores
    query = "SELECT similarity FROM main.function"
    cursor.execute(query)
    scores = cursor.fetchall()
    conn.close()

    return [score[0] for score in scores]  # Only return similarity scores


# Group .BinDiff files by compiler configuration based on the filename header
def group_files_by_compiler(directory):
    grouped_files = {}
    for file in os.listdir(directory):
        if file.endswith(".BinDiff"):
            # Extracting the compiler configuration from the filename
            header = os.path.basename(file).split("_")[
                0]  # Using the first part before '_vs_' to identify the compiler flag
            if header not in grouped_files:
                grouped_files[header] = []
            grouped_files[header].append(os.path.join(directory, file))
    return grouped_files


# Aggregate scores for each compiler configuration
def aggregate_scores_by_compiler(grouped_files):
    grouped_scores = {}
    for header, files in grouped_files.items():
        compiler_scores = []
        for sqlite_file in files:
            scores = query_function_scores(sqlite_file)
            compiler_scores.extend(scores)
        grouped_scores[header] = compiler_scores
    return grouped_scores


# Plot KDE for each compiler configuration
def plot_kde(grouped_scores):
    plt.figure(figsize=(12, 8))
    sns.set_palette("tab10")  # Use a 10-color palette for distinction
    sns.set_style("whitegrid")  # Use a grid style for clarity

    for header, scores in grouped_scores.items():
        sns.kdeplot(scores, label=header, linewidth=2.5)  # Increased linewidth for visibility

    plt.xlabel('BinDiff Similarity Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.title('KDE of BinDiff Similarity Scores Across Compiler Configurations', fontsize=16)
    plt.legend(title='Compiler Configurations', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    plt.tight_layout()
    plt.show()


# Main Execution
if __name__ == "__main__":
    grouped_files = group_files_by_compiler(bindiff_results_dir)  # Group files by compiler configuration
    grouped_scores = aggregate_scores_by_compiler(grouped_files)  # Aggregate scores for each group
    plot_kde(grouped_scores)  # Plot KDE for each compiler configuration