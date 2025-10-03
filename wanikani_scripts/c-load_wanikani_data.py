import pandas as pd
import os
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from env import DATABASE_URL
from wanikani_views import views

def create_database_engine(database_url: str) -> Engine:
    """
    Creates and validates a SQLAlchemy database engine.
    
    Args:
        database_url: PostgreSQL database connection URL
        
    Returns:
        SQLAlchemy Engine instance
        
    Raises:
        ValueError: If database URL is invalid or missing
        SQLAlchemyError: If database connection fails
    """
    try:
        if not database_url:
            raise ValueError("Database URL is required but was not provided")
        
        engine = create_engine(database_url)
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✓ Database connection established")
        return engine
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        raise
    except SQLAlchemyError as e:
        print(f"✗ Database connection failed: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error creating database engine: {e}")
        raise


def manage_views(engine: Engine, views: List[str], action: str = 'drop') -> None:
    """
    Manages database views by dropping or creating them.
    
    Args:
        engine: SQLAlchemy engine instance
        views: List of SQL view definitions
        action: Either 'drop' or 'create' (default: 'drop')
        
    Raises:
        ValueError: If action is not 'drop' or 'create'
        SQLAlchemyError: If view operation fails
    """
    if action not in ['drop', 'create']:
        raise ValueError(f"Invalid action '{action}'. Must be 'drop' or 'create'")
    
    try:
        with engine.connect() as connection:
            for view_sql in views:
                try:
                    # Extract view name (assumes 'CREATE VIEW view_name AS' format)
                    view_name = view_sql.split()[2]
                    
                    if action == 'drop':
                        connection.execute(text(f"DROP VIEW IF EXISTS {view_name};"))
                        connection.commit()
                        print(f"  ✓ Dropped view: {view_name}")
                    elif action == 'create':
                        connection.execute(text(view_sql))
                        connection.commit()
                        print(f"  ✓ Created view: {view_name}")
                        
                except IndexError:
                    print(f"  ⚠ Warning: Could not parse view name from SQL: {view_sql[:50]}...")
                    continue
                except SQLAlchemyError as e:
                    print(f"  ✗ Error managing view {view_name}: {e}")
                    raise
                    
    except SQLAlchemyError as e:
        print(f"✗ Database operation failed: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error managing views: {e}")
        raise

def load_excel_to_database(excel_path: str, engine: Engine, table_name: str = 'wanikani_subjects', 
                           schema: str = 'public') -> int:
    """
    Loads data from Excel file into PostgreSQL database.
    
    Args:
        excel_path: Path to the Excel file to load
        engine: SQLAlchemy engine instance
        table_name: Name of the database table to create/replace
        schema: Database schema name
        
    Returns:
        Number of rows loaded
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        pd.errors.EmptyDataError: If Excel file is empty
        SQLAlchemyError: If database operation fails
    """
    try:
        # Validate file exists
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        # Load the Excel file
        print(f"Loading data from {excel_path}...")
        df = pd.read_excel(excel_path)
        
        if df.empty:
            raise pd.errors.EmptyDataError(f"Excel file is empty: {excel_path}")
        
        print(f"  ✓ Loaded {len(df)} rows from Excel")
        
        # Load to database
        print(f"Writing to database table '{schema}.{table_name}'...")
        df.to_sql(table_name, engine, schema=schema, if_exists='replace', index=False)
        
        print(f"  ✓ Successfully loaded {len(df)} rows to database")
        return len(df)
        
    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        print(f"✗ Data error: {e}")
        raise
    except SQLAlchemyError as e:
        print(f"✗ Database load failed: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error loading data: {e}")
        raise


# Main execution
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("WaniKani Data → Database Load")
        print("=" * 60)
        
        # Create database engine
        engine = create_database_engine(DATABASE_URL)
        
        # Drop existing views
        print("\nDropping existing views...")
        manage_views(engine, views, action='drop')
        
        # Load data from Excel to database
        excel_path = 'data/wanikani_subjects.xlsx'
        row_count = load_excel_to_database(excel_path, engine, table_name='wanikani_subjects')
        
        # Recreate views
        print("\nRecreating views...")
        manage_views(engine, views, action='create')
        
        print("\n" + "=" * 60)
        print(f"✓ Load completed successfully! ({row_count} rows)")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Load failed: {e}")
        print("=" * 60)
        exit(1)
