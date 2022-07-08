"""Contains database-related operations."""
import sqlite3

from load_config import load_config


def create_connection():
    """Creates a connection for database operations and returns the cursor."""
    config = load_config()
    con = sqlite3.connect(config['database']['dbname'])
    con.row_factory = sqlite3.Row
    return con
