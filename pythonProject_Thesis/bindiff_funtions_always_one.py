import os
import sqlite3
import csv

# Define the base path to the directories under 'pythonProject_Thesis'
base_path = '/Users/hamidrezaaslani/Desktop/BinDiversity-ONLINE/pythonProject_Thesis'
output_csv = 'functions_with_similarity_1.csv'


# Function to query the SQLite database in .BinDiff files
def query_bindiff_file(bindiff_file):
    functions_with_scores = {}
    try:
        conn = sqlite3.connect(bindiff_file)
        cursor = conn.cursor()
        query = """
        SELECT name1, similarity 
        FROM function
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        functions_with_scores = {row[0]: row[1] for row in results}
    except sqlite3.Error as e:
        print(f"Error querying {bindiff_file}: {e}")
    return functions_with_scores


# Main script execution
if __name__ == "__main__":
    print(f"Searching for .BinDiff files in {base_path}...")

    all_results = []
    function_scores = {}

    # Iterate over the directories and .BinDiff files
    for root, dirs, files in os.walk(base_path):
        print(f"Current directory: {root}")
        print(f"Files: {files}")
        for file in files:
            if file.endswith(".BinDiff"):
                bindiff_file = os.path.join(root, file)
                print(f"Querying {bindiff_file}")
                functions_with_scores = query_bindiff_file(bindiff_file)
                if functions_with_scores:
                    print(f"Functions in {bindiff_file}:")
                    for function_name, similarity in functions_with_scores.items():
                        print(f" - {function_name}: {similarity}")
                        if function_name not in function_scores:
                            function_scores[function_name] = []
                        function_scores[function_name].append(similarity)
                        if similarity == 1:
                            all_results.append([bindiff_file, function_name])
                else:
                    print(f"No functions found in {bindiff_file}")

    # Print all functions with their scores across all comparisons
    print("Functions with their similarity scores across all comparisons:")
    for function_name, scores in function_scores.items():
        print(f" - {function_name}: {scores}")

    # Find common functions with similarity 1 in all files
    common_functions_with_similarity_one = [f for f, scores in function_scores.items() if
                                            all(score == 1 for score in scores)]

    print("Common functions in all files with similarity 1:")
    for function in common_functions_with_similarity_one:
        print(f" - {function}")

    # Save results to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['File', 'Function Name'])
        csvwriter.writerows(all_results)

    print(f"Results saved to {output_csv}")
    print("Process completed.")