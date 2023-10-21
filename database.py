import sqlite3
import hashlib
from sqlite3 import Error

class DataBase:
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        self.create_table()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            MatricNo TEXT PRIMARY KEY,
            name TEXT,
            department TEXT,
            level TEXT,
            password TEXT,
            profile_image TEXT
        )
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_query)
            self.conn.commit()
        except Error as e:
            print(e)

    def get_user(self, MatricNo):
        select_query = "SELECT * FROM users WHERE MatricNo = ?"
        cursor = self.conn.cursor()
        cursor.execute(select_query, (MatricNo,))
        user = cursor.fetchone()
        if user:
            return user[1], user[2], user[3], user[4], user[5]
        else:
            return None

    def add_user(self, MatricNo, name, department, level, password, profile_image_filename):
        user = self.get_user(MatricNo)
        if user is None:
            insert_query = """
            INSERT INTO users (MatricNo, name, department, level, password, profile_image)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (MatricNo, name, department, level, password, profile_image_filename)
            cursor = self.conn.cursor()
            cursor.execute(insert_query, values)
            self.conn.commit()
            return 1
        else:
            print("Matric No exists already")
            return -1

    def validate(self, MatricNo, password):
        user = self.get_user(MatricNo)
        if user:
            # Check if the provided password matches the stored password
            return password == user[3]
        return False

if __name__ == '__main__':
    db = DataBase('id_card.db')  # Use a local SQLite database file (id_card.db)
