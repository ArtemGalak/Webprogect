import sqlite3


class HelpBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM Base'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() AS 'count' FROM Members WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Пользователь с таким email уже существует')
                return False

            self.__cur.execute("INSERT INTO Members VALUES(NULL, ?, ?, ?)", (name, email, hpsw))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления пользователя в БД'+str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM Members WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone
            if not res:
                print('Пользователь не найден')
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных из БД' + str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM Members WHERE email = '{email} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка в получение данных из БД' + str(e))

        return False
