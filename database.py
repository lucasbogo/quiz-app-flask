import sqlite3
# from flask import g

# Singleton pattern to connect to the database only once    

class MetaSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=MetaSingleton):
    connection = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect('/home/lucas/python_projects/quiz_app/quizapp.db')
            self.cursorobj = self.connection.cursor()
        return self.cursorobj


    def close(self):
        self.connection.close()


    