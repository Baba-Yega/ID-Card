import mysql.connector
import datetime
import hashlib

class DataBase:
    def __init__(self, host, user, password, database):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="id_card"
        )
        self.cursor = self.db.cursor()

    def get_user(self, MatricNo):
        self.cursor.execute("SELECT * FROM users WHERE MatricNo = %s", (MatricNo,))
        user = self.cursor.fetchone()
        if user:
            # Return user's name, department, level, and profile image filename
            # print(f"User 2: {user[2]}, user 3: {user[3]}, user 4: {user[4]}, user 5: {user[5]}")
            return user[2], user[3], user[4], user[5], user[6]
        else:
            return None

    def add_user(self, MatricNo, name, department, level, password, profile_image_filename):
        user = self.get_user(MatricNo)
        if user is None:
            insert_query = """
            INSERT INTO users (MatricNo, name, department, level, password, profile_image)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (MatricNo, name, department, level, password, profile_image_filename)
            self.cursor.execute(insert_query, values)
            self.db.commit()
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
