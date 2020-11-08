import sqlite3


class ClosingConnection:
    def __init__(self, path, commit):
        self.path = path
        self.commit = commit

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            if self.commit:
                self.conn.commit()
            self.conn.close()


class knibot_db:
    path = './knibot.db'

    @classmethod
    def connect(cls, commit=False):
        return ClosingConnection(cls.path, commit)


def create_list(list_name, created_by=0):
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO lists (name) VALUES ("%s")' % list_name)
        if created_by != 0:
            c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES (?, ?, 1)',
                      (c.lastrowid, created_by))
        return c.lastrowid


def add_user_to_list(user, list_name, admin=False):
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM lists WHERE name="%s"' % list_name)
        c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES ('
                  '?, ?, ?)', (c.fetchall()[0][0], user, 1 if admin else 0))


if __name__ == '__main__':
    # create_list('assholes')
    # add_user_to_list(1411, 'assholes', True)
    # add_user_to_list(487834, 'assholes', False)
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        # c.execute('DROP TABLE IF EXISTS lists')
        # c.execute('DROP TABLE IF EXISTS listsForUsers')
        # c.execute('CREATE TABLE lists ('
        #           'id INTEGER PRIMARY KEY,'
        #           'name TEXT NOT NULL)')
        # c.execute('CREATE TABLE listsForUsers ('
        #           'list_id INTEGER,'
        #           'user_id INTEGER,'
        #           'admin INTEGER,'
        #           'FOREIGN KEY(list_id) REFERENCES lists(id))')
        # c.execute('INSERT INTO lists (name) VALUES ("friends")')
        # c.execute('INSERT INTO listsForUsers (list_id, user_id) VALUES (0, 972502057283)')
        # # select all available lists for a user
        # c.execute('SELECT name FROM lists WHERE id IN ('
        #           'SELECT list_id FROM listsForUsers WHERE user_id=972502057283)')
        # # select all users in a list
        # c.execute('SELECT user_id FROM listsForUsers WHERE list_id=0')
        c.execute('SELECT * FROM lists')
        print('lists: ' + str(c.fetchall()))
        c.execute('SELECT * FROM listsForUsers')
        print('listsForUsers: ' + str(c.fetchall()))
