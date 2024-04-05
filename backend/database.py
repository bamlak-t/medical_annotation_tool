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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extract TEXT,
                labels TEXT
            )
        """)
        self.conn.commit()

    def insert_row(self, extract, labels):
        self.cursor.execute("""
            INSERT INTO annotations (extract, labels) VALUES (?, ?)
        """, (extract, labels,))
        self.conn.commit()

    def insert_bulk_row(self, data):
        print(data)
        self.cursor.executemany("""
            INSERT INTO annotations (extract, labels) VALUES (?, ?)
        """, data)
        self.conn.commit()