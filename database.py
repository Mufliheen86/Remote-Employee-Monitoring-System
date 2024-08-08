import sqlite3
import os
import cv2
import numpy

class database:
    def __init__(self):
        try:
            with open("emp.db", "r") as r:
                r.close()
        except FileNotFoundError:
            db, cursor = self.get()
            cursor.execute("CREATE TABLE IF NOT EXISTS EMPLOYEE(\
                USERID INEGER PRIMARY KEY NOT NULL,\
                    USERNAME VARCHAR NOT NULL,\
                        PASSWORD VARCHAR NOT NULL);")
            db.commit()
            db.close()

    def get(self):
        with sqlite3.connect("emp.db") as db:
            cursor = db.cursor()
        return db, cursor

    def insert(self, username, password):
        db, cursor = self.get()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE USERNAME = ?", (username,))
        if cursor.fetchall():
            db.close()
            return False
        else:
            cursor.execute("SELECT * FROM EMPLOYEE")
            total = len(cursor.fetchall())
            cursor.execute("INSERT INTO EMPLOYEE VALUES (?,?,?)", (total, username, password))
            db.commit()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {username} (\
                TIME_LINE VACHAR PRIMARY KEY NOT NULL,\
                    CAMERA BLOB);")
            db.commit()
            db.close()
            return True
    
    def check_exists(self, username, password):
        db, cursor = self.get()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE USERNAME = ? AND PASSWORD = ?", (username, password))
        if cursor.fetchall():
            db.close()
            return True
        else:
            db.close()
            return False
        
    def get_usernames(self):
        db, cursor = self.get()
        cursor.execute("SELECT USERNAME FROM EMPLOYEE")
        data = cursor.fetchall()
        db.close()
        return data

    def get_blob(self, username):
        db, cursor = self.get()
        cursor.execute(f"SELECT * FROM {username}")
        data = cursor.fetchall()
        db.close()
        return data[-1]
    
    def get_all_blob(self, username):
        db, cursor = self.get()
        cursor.execute(f"SELECT * FROM {username}")
        data = cursor.fetchall()
        db.close()
        return data

    def insert_blob(self, username, time, bytes):
        bytes = cv2.cvtColor(bytes, cv2.COLOR_BGR2RGB)
        cv2.imwrite('test.jpg', bytes)
        data = None
        with open('test.jpg', 'rb') as rb:
            data = rb.read()
            rb.close()
        db, cursor = self.get()
        cursor.execute(f"INSERT INTO {username} VALUES (?,?)", (time, data))
        db.commit()
        db.close()
        os.remove('test.jpg')
  
    def delete(self):
        try:
            os.remove("emp.db")
        except FileNotFoundError:
            pass

    def inspect(self):
        db, cursor = self.get()
        cursor.execute("SELECT name FROM sqlite_master  WHERE type=\"table\"")
        print(cursor.fetchall())
        '''cursor.execute(f"SELECT * FROM {cursor.fetchall()[1][0]}")
        frames = cursor.fetchall()
        try:
            os.mkdir('ex')
        except:
            files = os.listdir('ex')
            for file in files:
                os.remove('ex/'+file)
            os.rmdir('ex')
        for i in range(len(frames)):
            try:
                f = open(f'ex/{frames[i][0].replace(":","-")}.jpg', 'wb')
                f.write(frames[i][1])
                f.close()
            except:
                break'''


