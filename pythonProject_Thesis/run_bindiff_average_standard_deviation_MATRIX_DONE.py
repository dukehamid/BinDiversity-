import os
import pandas as pd
import subprocess
import re
import matplotlib.pyplot as plt
import seaborn as sns

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

# Update directories to include the full paths
directories = [os.path.join(base_path, directory) for directory in directories]

# Directory for BinDiff results
bindiff_results_dir = os.path.join(base_path, 'bindiff_results')
os.makedirs(bindiff_results_dir, exist_ok=True)

# Function to run BinDiff and capture output
def run_bindiff(primary, secondary, output_dir):
    output_file = os.path.join(output_dir, f'{os.path.basename(primary)}_vs_{os.path.basename(secondary)}.BinDiff')
    log_file = os.path.join(output_dir, f'{os.path.basename(primary)}_vs_{os.path.basename(secondary)}.log')
    cmd = f'bindiff --primary {primary} --secondary {secondary} --output_dir {output_dir}'
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    with open(log_file, 'w') as lf:
        lf.write(result.stdout)
    if result.returncode != 0:
        print(f"Error running BinDiff: {result.stderr}")
    return output_file, log_file, result.stdout, result.stderr

# Function to extract similarity score from the log file
def extract_similarity_score_from_log(log_file):
    similarity = None
    with open(log_file, 'r') as file:
        for line in file:
            match = re.search(r'Similarity:\s+([0-9.]+)%', line)
            if match:
                similarity = float(match.group(1))
                break
    return similarity

# Identify common .BinExport files
common_files = None
all_files = {}

for directory in directories:
    if os.path.isdir(directory):
        binexport_files = {f for f in os.listdir(directory) if f.endswith('.BinExport')}
        all_files[directory] = binexport_files
        if common_files is None:
            common_files = binexport_files
        else:
            common_files &= binexport_files

# Debug: Print files in each directory
for dir_path, files in all_files.items():
    print(f"Files in {dir_path}: {files}")

# Debug: Print common files
print("Common .BinExport files across all directories:")
print(common_files)

# Check if common_files is None
if not common_files:
    print("No common .BinExport files found across all directories.")
    exit(1)

# Function to get label from directory path
def get_label_from_directory(directory):
    return os.path.basename(os.path.dirname(directory))

# Aggregate similarity scores
data = []
labels = [get_label_from_directory(dir_path) for dir_path in directories]

for file in common_files:
    binaries = {directory: os.path.join(directory, file) for directory in directories}
    for i in range(len(directories)):
        for j in range(i + 1, len(directories)):
            primary = binaries[directories[i]]
            secondary = binaries[directories[j]]
            output_file, log_file, output_content, error_content = run_bindiff(primary, secondary, bindiff_results_dir)
            print(f"BinDiff output for {primary} vs {secondary}:")
            print(output_content)
            if error_content:
                print(f"BinDiff error for {primary} vs {secondary}:")
                print(error_content)
            # Extract similarity score from the log file
            similarity = extract_similarity_score_from_log(log_file)
            if similarity is not None:
                data.append({
                    'primary': labels[i],
                    'secondary': labels[j],
                    'similarity': similarity
                })
            else:
                print(f"No similarity score found for {primary} vs {secondary}")

# Check if data is collected correctly
if not data:
    print("No similarity scores were collected.")
    exit(1)

# Convert the aggregated data into a DataFrame
df = pd.DataFrame(data)

# Calculate mean ± stddev for each pair
df_summary = df.groupby(['primary', 'secondary']).agg({'similarity': ['mean', 'std']}).reset_index()
df_summary.columns = ['primary', 'secondary', 'mean', 'stddev']

# Create a pivot table with mean ± stddev
pivot_table_mean = df_summary.pivot(index='primary', columns='secondary', values='mean')
pivot_table_stddev = df_summary.pivot(index='primary', columns='secondary', values='stddev')

# Ensure the matrix headers are in the same order on both sides
pivot_table_mean = pivot_table_mean.reindex(labels, axis=0).reindex(labels, axis=1)
pivot_table_stddev = pivot_table_stddev.reindex(labels, axis=0).reindex(labels, axis=1)

# Combine mean and stddev into one table for display
combined_table = pivot_table_mean.round(2).astype(str) + " ± " + pivot_table_stddev.round(2).astype(str)

# Replace NaN values with '-'
combined_table = combined_table.replace("nan ± nan", "- ± -")

# Fill diagonal with '0.00 ± 0.00'
for label in labels:
    if label in combined_table.index and label in combined_table.columns:
        combined_table.loc[label, label] = '0.00 ± 0.00'

# Ensure combined_table has the same shape as pivot_table_mean
combined_table = combined_table.reindex(index=labels, columns=labels)

# Plot the heatmap of the mean similarity scores with stddev
plt.figure(figsize=(12, 10))
sns.heatmap(pivot_table_mean, annot=combined_table, fmt='', cmap="YlGnBu", cbar_kws={'label': 'Mean Similarity (%)'})
plt.title('Mean Similarity Scores ± Standard Deviation between Different Binaries')
plt.xlabel('Secondary Binary')
plt.ylabel('Primary Binary')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(base_path, 'similarity_heatmap_mean_stddev.png'))

# Display the plot
plt.show()