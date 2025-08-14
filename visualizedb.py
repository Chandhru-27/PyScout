import sqlite3
import pandas as pd

# Path to your SQLite DB file
db_path = r"C:\Users\Chandhru\AppData\Roaming\PyScout\userdata\User_db.sqlite3"  # change this to your actual DB path

# Connect to the database
conn = sqlite3.connect(db_path)

# Get all table names
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

print("\n📋 All tables in the database:")
print(tables)

# Loop through each table and display contents
for table_name in tables['name']:
    print(f"\n=== Table: {table_name} ===")
    df = pd.read_sql(f"SELECT * FROM {table_name};", conn)
    print(df)  # Print DataFrame to console
    
    # If you want a quick visualization (works in Jupyter or with plt.show()

# Close connection
conn.close()
