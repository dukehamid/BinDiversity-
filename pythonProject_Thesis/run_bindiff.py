import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Set the base path to the current working directory
base_path = os.path.abspath(os.getcwd())

# Directory for BinDiff results
bindiff_results_dir = os.path.join(base_path, 'bindiff_results')

# SQLite database setup
db_path = os.path.join(base_path, 'similarity_scores.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Function to check if a column exists in a table
def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# Ensure the similarity_scores table has the correct schema
c.execute('''CREATE TABLE IF NOT EXISTS similarity_scores
             (filename TEXT, function_name TEXT, similarity REAL)''')
conn.commit()

# Add the 'filename' column if it doesn't exist
if not column_exists(c, 'similarity_scores', 'filename'):
    c.execute('ALTER TABLE similarity_scores ADD COLUMN filename TEXT')
    conn.commit()

# Function to read BinDiff SQLite result files and extract similarity scores
def extract_similarity_scores_from_sqlite(result_file):
    scores = []
    try:
        with sqlite3.connect(result_file) as db_conn:
            query = "SELECT name1, similarity FROM function"
            df = pd.read_sql_query(query, db_conn)
            for index, row in df.iterrows():
                scores.append((row['name1'], row['similarity']))
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return scores

# Process each result file in the bindiff_results directory
for result_file in os.listdir(bindiff_results_dir):
    if '.BinExport' not in result_file:
        result_path = os.path.join(bindiff_results_dir, result_file)
        scores = extract_similarity_scores_from_sqlite(result_path)
        if scores:
            for score in scores:
                # Insert into the SQLite database
                c.execute('INSERT INTO similarity_scores (filename, function_name, similarity) VALUES (?, ?, ?)',
                          (result_file, score[0], score[1]))
            conn.commit()
        else:
            print(f"No function similarity scores found in: {result_file}")

# Query the database to retrieve the similarity scores
query = "SELECT function_name, similarity FROM similarity_scores"
df_db = pd.read_sql_query(query, conn)

# Print the DataFrame with the similarity scores from the database
print(df_db)

# Close the database connection
conn.close()

# Calculate standard deviation of similarity scores for each function
df_std = df_db.groupby('function_name').agg({'similarity': 'std'}).reset_index()

# Print distribution of standard deviations
print(df_std.describe())

# Plot distribution of standard deviations
plt.figure(figsize=(10, 6))
sns.histplot(df_std['similarity'], bins=50, kde=True)
plt.title('Distribution of Standard Deviations of Function Similarity Scores')
plt.xlabel('Standard Deviation')
plt.ylabel('Frequency')
plt.show()

# Adjust the threshold for filtering
threshold = 0.005  # Adjust this value based on the distribution
df_std_filtered = df_std[df_std['similarity'] > threshold]

# Plotting the standard deviation of similarity scores
plt.figure(figsize=(12, 8))
sns.barplot(x='similarity', y='function_name', data=df_std_filtered, palette='viridis')
plt.title('Standard Deviation of Function Similarity Scores')
plt.xlabel('Standard Deviation')
plt.ylabel('Function Name')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()