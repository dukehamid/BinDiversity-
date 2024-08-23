import os
import subprocess
import pandas as pd
import numpy as np
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Set the base path to the Desktop
base_path = os.path.join(os.path.expanduser("~"), "Desktop")

# List of directories containing the compiled results
directories = [
    'coreutils-7/bin',
    'coreutils-7-CFLAGS-O1/bin',
    'coreutils-7cflags03/bin',
    'coreutils-9-cflagsO1/bin',
    'coreutils-9-cflagsO3/bin',
    'coreutils-gcc_9/bin'
]

# Function to run BinDiff and capture output
def run_bindiff(primary, secondary, output_dir):
    output_file = os.path.join(output_dir, f'{os.path.basename(primary)}_vs_{os.path.basename(secondary)}.BinDiff')
    cmd = f'bindiff --primary {primary} --secondary {secondary} --output_dir {output_dir}'
    print(f"Running: {cmd}")  # Debug statement
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running BinDiff: {result.stderr}")
    return output_file, result.stdout, result.stderr

# Function to extract similarity scores from BinDiff log output
def extract_similarity_score(output_content):
    match = re.search(r'Similarity: ([0-9]+\.[0-9]+)%', output_content)
    if match:
        return float(match.group(1))
    return None

# Create output directory for BinDiff results
output_dir = os.path.join(base_path, 'bindiff_results')
os.makedirs(output_dir, exist_ok=True)

# Identify common .BinExport files
common_files = None
for directory in directories:
    full_dir = os.path.join(base_path, directory)
    if os.path.isdir(full_dir):
        binexport_files = {f for f in os.listdir(full_dir) if f.endswith('.BinExport')}
        if common_files is None:
            common_files = binexport_files
        else:
            common_files &= binexport_files

# Debug: Print common files
print("Common .BinExport files across all directories:")
print(common_files)

# Aggregate similarity scores between folders
folder_pairs = {}
for i, dir1 in enumerate(directories):
    for j, dir2 in enumerate(directories):
        if i < j:
            folder_pairs[(dir1, dir2)] = []

for file in common_files:
    binaries = {directory: os.path.join(base_path, directory, file) for directory in directories}
    for (dir1, dir2), _ in folder_pairs.items():
        primary = binaries[dir1]
        secondary = binaries[dir2]
        output_file, output_content, error_content = run_bindiff(primary, secondary, output_dir)
        print(f"BinDiff output for {primary} vs {secondary}:")
        print(output_content)
        if error_content:
            print(f"BinDiff error for {primary} vs {secondary}:")
            print(error_content)
        score = extract_similarity_score(output_content)
        if score is not None:
            folder_pairs[(dir1, dir2)].append(score)

# Calculate average similarity scores for each folder pair
average_similarity_scores = {pair: np.mean(scores) for pair, scores in folder_pairs.items() if scores}

# Debug: Print average similarity scores
print("Average similarity scores between folder pairs:")
for pair, score in average_similarity_scores.items():
    print(f"{pair}: {score}")

# Create a list of folder names
folder_names = [directory for directory in directories]

# Initialize an empty similarity matrix
n = len(folder_names)
similarity_matrix = np.zeros((n, n))

# Fill the similarity matrix with average scores
for (dir1, dir2), score in average_similarity_scores.items():
    i = directories.index(dir1)
    j = directories.index(dir2)
    similarity_matrix[i, j] = score
    similarity_matrix[j, i] = score

# Debug: Print the similarity matrix
print("Similarity matrix:")
print(similarity_matrix)

# Transform similarity matrix to distance matrix
distance_matrix = 1 - (similarity_matrix / 100.0)

# Ensure diagonal is zero
np.fill_diagonal(distance_matrix, 0)

# Debug: Print the distance matrix
print("Distance matrix:")
print(distance_matrix)

# Perform MDS
if len(distance_matrix) > 0 and np.any(distance_matrix):
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
    mds_coords = mds.fit_transform(distance_matrix)

    # Create a DataFrame with the MDS results
    mds_df = pd.DataFrame(mds_coords, index=folder_names, columns=['MDS1', 'MDS2'])

    # Plot the MDS results with enhancements
    plt.figure(figsize=(14, 10))
    scatter = sns.scatterplot(data=mds_df, x='MDS1', y='MDS2', palette='viridis', s=100)

    # Annotate points with folder names
    for folder, row in mds_df.iterrows():
        plt.text(row['MDS1'], row['MDS2'], folder, fontsize=9, ha='right')

    plt.title('MDS Plot of Folder Distances Based on BinDiff Similarities', fontsize=15)
    plt.xlabel('MDS Dimension 1', fontsize=12)
    plt.ylabel('MDS Dimension 2', fontsize=12)

    # Adjust legend to show on the right side
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("Distance matrix is empty or invalid, MDS cannot be performed.")