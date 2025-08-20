import pandas as pd
import os
from sqlalchemy import create_engine,text
from env import DATABASE_URL
from wanikani_views import views

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Function to drop and recreate views
def manage_views(engine, views, action='drop'):
    with engine.connect() as connection:
        for view_sql in views:
            view_name = view_sql.split()[2]  # Assumes 'CREATE VIEW view_name AS' format
            if action == 'drop':
                connection.execute(text(f"DROP VIEW IF EXISTS {view_name};"))
                connection.commit()
                print(f"dropped {view_name}")
            elif action == 'create':
                connection.execute(text(view_sql))
                connection.commit()

# Drop views
manage_views(engine, views, action='drop')

# Load the Excel file into a DataFrame
excel_path = 'data/wanikani_subjects.xlsx'
df = pd.read_excel(excel_path)

# Specify the name of the table you want to create from the Excel file
table_name = 'wanikani_subjects'

# Use if_exists='replace' to replace the table if it already exists
df.to_sql(table_name, engine, schema='public', if_exists='replace', index=False)

# Recreate views
manage_views(engine, views, action='create')

print(f"Data from {excel_path} has been successfully pushed to the '{table_name}'.")
print("Views have been successfully recreated.")
