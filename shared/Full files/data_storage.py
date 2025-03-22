# data_storage.py

import pandas as pd
import sqlite3
import os
from typing import Union

class DataStorage:
    """
    Class to handle data storage, including operations to connect to databases,
    create tables, insert data, update, delete, retrieve, and ensure data consistency.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the DataStorage class with a database path.
        :param db_path: Path to the database file.
        """
        self.db_path = db_path

    def connect(self):
        """
        Connect to the SQLite database and return the connection object.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            raise ConnectionError(f"Error connecting to database: {e}")

    def create_table(self, table_name: str, schema: str) -> None:
        """
        Create a table in the database.
        :param table_name: Name of the table to be created.
        :param schema: SQL schema string defining the table.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error creating table: {e}")
        finally:
            conn.close()

    def insert_data(self, table_name: str, data: pd.DataFrame) -> None:
        """
        Insert data into the table.
        :param table_name: Name of the table to insert data into.
        :param data: DataFrame containing the data to be inserted.
        """
        try:
            conn = self.connect()
            data.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error inserting data: {e}")
        finally:
            conn.close()

    def retrieve_data(self, table_name: str, columns: Union[list, None] = None) -> pd.DataFrame:
        """
        Retrieve data from the table.
        :param table_name: Name of the table to retrieve data from.
        :param columns: List of columns to retrieve, or None to retrieve all columns.
        :return: DataFrame containing the retrieved data.
        """
        try:
            conn = self.connect()
            if columns:
                column_string = ', '.join(columns)
                query = f"SELECT {column_string} FROM {table_name}"
            else:
                query = f"SELECT * FROM {table_name}"
            
            data = pd.read_sql_query(query, conn)
            return data
        except Exception as e:
            raise ValueError(f"Error retrieving data: {e}")
        finally:
            conn.close()

    def update_data(self, table_name: str, update_dict: dict, condition: str) -> None:
        """
        Update data in the table based on a condition.
        :param table_name: Name of the table to update data in.
        :param update_dict: Dictionary containing column-value pairs to update.
        :param condition: SQL condition string to identify the rows to update.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            update_clause = ', '.join([f"{col} = ?" for col in update_dict.keys()])
            cursor.execute(f"UPDATE {table_name} SET {update_clause} WHERE {condition}", tuple(update_dict.values()))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error updating data: {e}")
        finally:
            conn.close()

    def delete_data(self, table_name: str, condition: str) -> None:
        """
        Delete data from the table based on a condition.
        :param table_name: Name of the table to delete data from.
        :param condition: SQL condition string to identify the rows to delete.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error deleting data: {e}")
        finally:
            conn.close()

    def backup_database(self, backup_path: str) -> None:
        """
        Backup the entire database to a specified path.
        :param backup_path: Path where the backup file should be stored.
        """
        try:
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)

            backup_file = os.path.join(backup_path, os.path.basename(self.db_path))
            conn = self.connect()
            with open(backup_file, 'wb') as f:
                for chunk in conn.iterdump():
                    f.write(f"{chunk}\n".encode('utf-8'))
            conn.close()
        except Exception as e:
            raise ValueError(f"Error creating backup: {e}")

    def close_connection(self, conn):
        """
        Close the database connection.
        :param conn: Connection object to be closed.
        """
        if conn:
            conn.close()

# Example Usage:
"""
if __name__ == "__main__":
    db_path = "example_database.db"
    storage = DataStorage(db_path)

    # Example table schema
    table_schema = "id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT"
    
    # Create table
    storage.create_table("Users", table_schema)
    
    # Example DataFrame to insert
    sample_data = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 28],
        'city': ['New York', 'Los Angeles', 'Chicago']
    })
    
    # Insert data into table
    storage.insert_data("Users", sample_data)

    # Retrieve data from table
    retrieved_data = storage.retrieve_data("Users")
    print("Retrieved Data:")
    print(retrieved_data)

    # Update data in table
    storage.update_data("Users", {"age": 26}, "name = 'Alice'")
    
    # Delete data from table
    storage.delete_data("Users", "name = 'Bob'")
    
    # Backup database
    storage.backup_database("backup_folder")
"""
