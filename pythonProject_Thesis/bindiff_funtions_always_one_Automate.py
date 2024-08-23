import os
import angr
import sqlite3
import logging
import matplotlib.pyplot as plt

# Ensure distutils is imported correctly
try:
    import distutils
except ModuleNotFoundError:
    try:
        import setuptools._distutils as distutils
    except ModuleNotFoundError:
        raise ImportError("Failed to import distutils module, which is required by capstone.")

# Define directories where the binaries are stored
directories = [
    'coreutils-7/bin',
    'coreutils-7-CFLAGS-O1/bin',
    'coreutils-7cflags03/bin',
    'coreutils-9-cflagsO1/bin',
    'coreutils-9-cflagsO3/bin',
    'coreutils-gcc_9/bin'
]

# Update directories to include the full paths on the Desktop
directories = [os.path.join(os.path.expanduser("~"), "Desktop", directory) for directory in directories]

# Directory where the BinDiff results are stored
bindiff_results_dir = os.path.join(os.path.expanduser("~"), 'Desktop', 'BinDiversity-ONLINE', 'pythonProject_Thesis',
                                   'bindiff_results')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to extract functions with similarity 1 from BinDiff results
def extract_functions_with_similarity_one(bindiff_db):
    conn = sqlite3.connect(bindiff_db)
    cursor = conn.cursor()

    query = """
    SELECT name1, name2 
    FROM function 
    WHERE similarity = 1.0
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return results


# Function to disassemble and compare functions in two binaries
def compare_functions_by_disassembly(binary_path1, func_name1, binary_path2, func_name2):
    project1 = angr.Project(binary_path1, auto_load_libs=False)
    project2 = angr.Project(binary_path2, auto_load_libs=False)

    func1 = project1.loader.main_object.get_symbol(func_name1)
    func2 = project2.loader.main_object.get_symbol(func_name2)

    if not func1 or not func2:
        logging.warning(f"Function {func_name1} or {func_name2} not found in the binaries.")
        return 0, 0

    block1 = project1.factory.block(func1.rebased_addr).capstone
    block2 = project2.factory.block(func2.rebased_addr).capstone

    instructions1 = [f"{i.mnemonic} {i.op_str}" for i in block1.insns]
    instructions2 = [f"{i.mnemonic} {i.op_str}" for i in block2.insns]

    identical_instructions = sum(inst1 == inst2 for inst1, inst2 in zip(instructions1, instructions2))
    differing_instructions = len(instructions1) + len(instructions2) - 2 * identical_instructions

    return identical_instructions, differing_instructions


# Main function to process the binaries and BinDiff results
def analyze_similarity_one_functions(bindiff_results_dir):
    identical_counts = []
    differing_counts = []
    function_pairs = []

    for root, dirs, files in os.walk(bindiff_results_dir):
        for file in files:
            if file.endswith('.BinDiff'):
                bindiff_db = os.path.join(root, file)
                logging.info(f"Analyzing BinDiff results: {bindiff_db}")

                functions = extract_functions_with_similarity_one(bindiff_db)

                for func1, func2 in functions:
                    for dir1, dir2 in zip(directories[:-1], directories[1:]):
                        binary1 = os.path.join(dir1, func1)
                        binary2 = os.path.join(dir2, func2)

                        identical, differing = compare_functions_by_disassembly(binary1, func1, binary2, func2)

                        identical_counts.append(identical)
                        differing_counts.append(differing)
                        function_pairs.append(f"{func1} ({os.path.basename(dir1)}) vs {func2} ({os.path.basename(dir2)})")

    return identical_counts, differing_counts, function_pairs


# Function to plot the results
def plot_results(identical_counts, differing_counts, function_pairs):
    bar_width = 0.35
    index = range(len(function_pairs))

    plt.figure(figsize=(12, 8))
    plt.bar(index, identical_counts, bar_width, label='Identical Instructions')
    plt.bar([i + bar_width for i in index], differing_counts, bar_width, label='Differing Instructions')

    plt.xlabel('Function Pairs')
    plt.ylabel('Instruction Count')
    plt.title('Instruction Comparison for Functions with Similarity Score of 1')
    plt.xticks([i + bar_width / 2 for i in index], function_pairs, rotation=90)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    identical_counts, differing_counts, function_pairs = analyze_similarity_one_functions(bindiff_results_dir)
    plot_results(identical_counts, differing_counts, function_pairs)