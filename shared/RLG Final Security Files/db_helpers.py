# db_helpers.py - Database Helper Functions for RLG Data and RLG Fans

import logging
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from backend.error_handlers import DatabaseError

# Logger configuration
logger = logging.getLogger("db_helpers")
logger.setLevel(logging.INFO)

# Database configurations (placeholder: adjust based on environment)
DATABASE_URI = "postgresql://username:password@host:port/db_name"
engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

# Utility constants
MAX_RETRIES = 3


@contextmanager
def get_db_session():
    """
    Context manager for database session handling.
    Automatically handles session commit/rollback and closure.

    Yields:
        Session: SQLAlchemy session object.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise DatabaseError("A database error occurred.") from e
    finally:
        session.close()


def fetch_one(query, params=None):
    """
    Fetch a single record from the database.

    Args:
        query (str): The SQL query to execute.
        params (dict): Query parameters, if any.

    Returns:
        dict: The fetched record as a dictionary, or None if no result is found.
    """
    try:
        with get_db_session() as session:
            result = session.execute(query, params or {}).fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        logger.error(f"Error executing fetch_one: {e}")
        raise DatabaseError("Failed to fetch data from the database.")


def fetch_all(query, params=None):
    """
    Fetch multiple records from the database.

    Args:
        query (str): The SQL query to execute.
        params (dict): Query parameters, if any.

    Returns:
        list: A list of records as dictionaries.
    """
    try:
        with get_db_session() as session:
            result = session.execute(query, params or {}).fetchall()
            return [dict(row) for row in result] if result else []
    except Exception as e:
        logger.error(f"Error executing fetch_all: {e}")
        raise DatabaseError("Failed to fetch data from the database.")


def execute_query(query, params=None):
    """
    Execute a query (INSERT, UPDATE, DELETE) on the database.

    Args:
        query (str): The SQL query to execute.
        params (dict): Query parameters, if any.

    Returns:
        int: The number of rows affected by the query.
    """
    try:
        with get_db_session() as session:
            result = session.execute(query, params or {})
            return result.rowcount
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise DatabaseError("Failed to execute database query.")


def upsert(table, data, unique_key):
    """
    Perform an upsert (insert or update) operation on a table.

    Args:
        table (str): Table name.
        data (dict): Data to insert or update.
        unique_key (str): The column name for conflict resolution.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    query = f"""
    INSERT INTO {table} ({", ".join(data.keys())})
    VALUES ({", ".join([f":{key}" for key in data.keys()])})
    ON CONFLICT ({unique_key}) DO UPDATE
    SET {", ".join([f"{key} = :{key}" for key in data.keys()])}
    """
    try:
        return execute_query(query, data) > 0
    except Exception as e:
        logger.error(f"Error executing upsert: {e}")
        return False


def retry_operation(func, *args, retries=MAX_RETRIES, **kwargs):
    """
    Retry a database operation with exponential backoff.

    Args:
        func (callable): The database function to execute.
        retries (int): Maximum number of retries.
        args: Positional arguments for the function.
        kwargs: Keyword arguments for the function.

    Returns:
        Any: The result of the function, or raises an error after retries.
    """
    attempt = 0
    while attempt < retries:
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            attempt += 1
            wait_time = 2 ** attempt
            logger.warning(f"Retrying operation after {wait_time}s due to: {e}")
    logger.error("Max retries exceeded.")
    raise DatabaseError("Max retries exceeded for database operation.")


def bulk_insert(table, rows):
    """
    Perform a bulk insert operation.

    Args:
        table (str): Table name.
        rows (list): List of dictionaries containing rows to insert.

    Returns:
        int: Number of rows successfully inserted.
    """
    if not rows:
        logger.warning("No rows to insert.")
        return 0

    columns = rows[0].keys()
    query = f"""
    INSERT INTO {table} ({", ".join(columns)})
    VALUES ({", ".join([f":{col}" for col in columns])})
    """
    try:
        with get_db_session() as session:
            result = session.execute(query, rows)
            logger.info(f"Bulk inserted {result.rowcount} rows into {table}.")
            return result.rowcount
    except Exception as e:
        logger.error(f"Error executing bulk insert: {e}")
        raise DatabaseError("Failed to perform bulk insert.")


def generate_placeholder_list(params):
    """
    Generate a placeholder list for SQL queries.

    Args:
        params (list): List of values to generate placeholders for.

    Returns:
        str: A comma-separated placeholder string.
    """
    return ", ".join([f":param_{i}" for i in range(len(params))])


def build_query_with_placeholders(query, params):
    """
    Build a query string with named placeholders.

    Args:
        query (str): Base SQL query with positional placeholders.
        params (list): List of parameters to replace positional placeholders.

    Returns:
        tuple: Query string with named placeholders and parameter mapping.
    """
    placeholders = {f"param_{i}": value for i, value in enumerate(params)}
    query = query.replace("?", lambda _: generate_placeholder_list(params))
    return query, placeholders


# Health Check
def check_database_health():
    """
    Check the health of the database connection.

    Returns:
        bool: True if the database is healthy, False otherwise.
    """
    try:
        with get_db_session() as session:
            session.execute("SELECT 1")
            logger.info("Database connection is healthy.")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
