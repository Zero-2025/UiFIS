import mysql.connector
from mysql.connector import Error
import tkinter.messagebox as messagebox

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='is_expansion',
                user='root',      # измените на вашего пользователя
                password='root',      # измените на ваш пароль
                charset='utf8'
            )
            return True
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных: {e}")
            return False
    
    def execute_query(self, query, params=None):
        if not self.connection:
            if not self.connect():
                return None
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения запроса: {e}")
            return None
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        if not self.connection:
            if not self.connect():
                return []
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения запроса: {e}")
            return []
        finally:
            cursor.close()
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()