import os
import subprocess
import shutil
from itertools import combinations

# Set the base path to the PyCharm project directory
base_path = os.path.dirname(os.path.abspath(__file__))

# List of directories containing the compiled results on your Desktop
directories = [
    'gcc-7/bin',
    'gcc-7-cflags-O1/bin',
    'gcc-7-cflags-03/bin',
    'gcc-9-cflags-O1/bin',
    'gcc-9-cflags-O3/bin',
    'gcc-9/bin'
]

# Update directories to include the full paths on the Desktop
directories = [os.path.join(os.path.expanduser("~"), "Desktop", directory) for directory in directories]

# Directory for renamed BinExport files
renamed_binexport_dir = os.path.join(base_path, 'renamed_binexports')
os.makedirs(renamed_binexport_dir, exist_ok=True)

# Directory for BinDiff results and logs
bindiff_results_dir = os.path.join(base_path, 'bindiff_results')
logs_dir = os.path.join(bindiff_results_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Function to rename .BinExport files with directory prefixes
def rename_binexport_files(directories, output_dir):
    renamed_files = {}
    for directory in directories:
        dir_name = os.path.basename(os.path.dirname(directory))
        for file in os.listdir(directory):
            if file.endswith('.BinExport'):
                original_file_path = os.path.join(directory, file)
                new_file_name = f"{dir_name}_{file}"
                new_file_path = os.path.join(output_dir, new_file_name)
                shutil.copy2(original_file_path, new_file_path)
                renamed_files[new_file_name] = new_file_path
    return renamed_files

# Rename all .BinExport files and save the new paths
renamed_files = rename_binexport_files(directories, renamed_binexport_dir)

# Group files by their base names (without the directory prefix)
grouped_files = {}
for renamed_name, path in renamed_files.items():
    base_name = renamed_name.split("_", 1)[1]  # Base name after the first underscore
    if base_name not in grouped_files:
        grouped_files[base_name] = []
    grouped_files[base_name].append(path)

# Debug: Print grouped files
print("Grouped files:")
for base_name, files in grouped_files.items():
    print(f"{base_name}:")
    for file in files:
        print(f"  - {file}")

# Run BinDiff on all possible pairs of files within the same group
for base_name, files in grouped_files.items():
    if len(files) > 1:  # Ensure at least two files are present
        for primary, secondary in combinations(files, 2):
            # Extracting directory names from file paths for the output and log files
            primary_dir_name = os.path.basename(os.path.dirname(primary)).replace('.BinExport', '')
            secondary_dir_name = os.path.basename(os.path.dirname(secondary)).replace('.BinExport', '')

            # Define output and log file names with proper directory headers
            output_file = os.path.join(bindiff_results_dir,
                                       f"{primary_dir_name}_{base_name}_vs_{secondary_dir_name}_{base_name}.BinDiff")
            log_file = os.path.join(logs_dir,
                                    f"{primary_dir_name}_{base_name}_vs_{secondary_dir_name}_{base_name}.log")

            # Run BinDiff with the correctly named output directory
            cmd = f'bindiff --primary {primary} --secondary {secondary} --output_dir {bindiff_results_dir}'
            print(f"Running: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # Save the log file
            with open(log_file, 'w') as lf:
                lf.write(result.stdout)
            if result.returncode != 0:
                print(f"Error running BinDiff: {result.stderr}")
            else:
                print(f"Processed BinDiff results for {primary} vs {secondary}, saved to {output_file}.")
    else:
        print(f"Skipping {base_name}: not enough files to compare.")

print("All pairwise BinDiff operations completed.")