import sqlite3

DB_NAME = 'annotations.db'

class AnnotationDb:
    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        """)

    def insert_data(self, data):
        self.cursor.execute("""
            INSERT INTO annotations (data) VALUES (?)
        """, (data,))
        self.conn.commit()