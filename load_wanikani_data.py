import pandas as pd
import os
from sqlalchemy import create_engine
from env import DATABASE_URL

# Your database credentials and connection details
user = 'admin'
password = 'Alexandria5332'
host = 'localhost'
port = '5432'
dbname = 'DB'

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Load the Excel file into a DataFrame
excel_path = 'data/wanikani/wanikani_subjects.xlsx'
df = pd.read_excel(excel_path)

# Specify the name of the table you want to create from the Excel file
table_name = 'wanikani_subjects'

# Use if_exists='replace' to replace the table if it already exists
# Use if_exists='append' to append data to an existing table
# Use index=False if your DataFrame index is not meaningful in the database
df.to_sql(table_name, engine, schema='public', if_exists='replace', index=False)

print(f"Data from {excel_path} has been successfully pushed to the '{table_name}' table in the '{dbname}' database.")
