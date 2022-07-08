"""
Initializes all tables and inserts base data.
"""
import sqlite3

from load_config import load_config


def create_tables():
    """
    Initializes all tables and inserts base data.
    """
    config = load_config()

    file_name = config['database']['init_file']
    database_name = config['database']['dbname']

    with open(file_name, 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()

    db = sqlite3.connect(database_name)
    cursor = db.cursor()
    cursor.executescript(sql_script)
    db.commit()
    db.close()


if __name__ == "__main__":
    create_tables()
