import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host= "localhost",
        user = "root",
        password = "Bhavesh123",
        database = "sentiment_analysis"
    )


def select_one(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchone()

def select_all(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchall()

def execute_query(cursor, query, params=None):
    cursor.execute(query, params or ())

