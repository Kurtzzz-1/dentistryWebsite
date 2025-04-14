import sqlite3


def execute_query(query, params=None):
    with sqlite3.connect("dentistry.db") as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
    return cursor.fetchall()


def get_topics() -> list:
    """
    Fetch all topics from the database.
    """
    query = "SELECT DISTINCT topic FROM questions"
    return [topic[0] for topic in execute_query(query)]


def get_table_names() -> list:
    """
    Fetch all table names from the database.
    """
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    return [table[0] for table in execute_query(query)]
