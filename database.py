import psycopg2

import prompts_he


class ClosingConnection:
    def __init__(self, path, commit):
        self.path = path
        self.commit = commit

    def __enter__(self) -> psycopg2._psycopg.connection:
        self.conn = psycopg2.connect(host='localhost', database='knibot', user='postgres', password='')
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

    STATE_DEFAULT = 0
    STATE_WRITING = 1
    STATE_ERASING = 2
    STATE_SHARING = 3

    @staticmethod
    def connect(commit=False):
        return ClosingConnection(knibot_db.path, commit)

    @staticmethod
    def create():
        print('creating tables')
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('DROP TABLE IF EXISTS lists CASCADE')
            c.execute('DROP TABLE IF EXISTS listsForUsers')
            c.execute('DROP TABLE IF EXISTS items')
            c.execute('DROP TABLE IF EXISTS workingLists')
            c.execute('CREATE TABLE lists ('
                      'id SERIAL PRIMARY KEY,'
                      'name TEXT NOT NULL)')
            c.execute('CREATE TABLE listsForUsers ('
                      'list_id INTEGER REFERENCES lists ON DELETE CASCADE,'
                      'user_id INTEGER,'
                      'admin INTEGER)')
            c.execute('CREATE TABLE items ('
                      'name TEXT NOT NULL,'
                      'list_id INTEGER REFERENCES lists ON DELETE CASCADE,'
                      'request_by INTEGER)')
            c.execute('CREATE TABLE workingLists ('
                      'user_id INTEGER UNIQUE,'
                      'list_id INTEGER REFERENCES lists ON DELETE CASCADE,'
                      'state INTEGER)')

    @staticmethod
    def clear():
        print('clearing database')
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM listsForUsers')
            c.execute('DELETE FROM lists')
            c.execute('DELETE FROM items')
            c.execute('DELETE FROM workingLists')

    @staticmethod
    def create_list(user, list_name):
        print('%i is creating a new list %s' % (user, list_name))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM lists WHERE id IN ('
                      'SELECT list_id FROM listsForUsers WHERE user_id=%i)'
                      'AND name=\'%s\'' % (user, list_name))
            if c.fetchone() is not None:
                raise ValueError(prompts_he.already_exists_err % list_name)
            c.execute('INSERT INTO lists (name) VALUES (\'%s\')' % list_name)
            c.execute('SELECT LASTVAL()')
            list_id = c.fetchone()[0]
            if user != 0:
                c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES (%i, %i, 1)' %
                          (list_id, user))
            return list_id
    
    @staticmethod
    def add_users_to_list(user, users):
        print('user %i is adding users %s' % (user, str(users)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join('(%i, %i, 0)' % (working_list, u) for u in users)
            c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES %s' % values)
    
    @staticmethod
    def remove_users_from_list(user, users):
        print('user %i is removing users %s' % (user, str(users)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join(users)
            c.execute('DELETE FROM listsForUsers WHERE list_id=%i AND user_id IN (%s)'
                      % (working_list, values))
    
    @staticmethod
    def remove_all_users_from_list(user):
        print('user %i is removing all users' % user)
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            c.execute('DELETE FROM listsForUsers WHERE list_id=%i AND user_id!=%i'
                      % (working_list, user))
    
    @staticmethod
    def remove_all_users_from_list_but(user, users):
        print('user %i is removing all users but %s' % (user, str(users)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join(users) + ', ' + user
            c.execute('DELETE FROM listsForUsers WHERE list_id=%i AND user_id NOT IN (%s)'
                      % (working_list, values))
    
    @staticmethod
    def set_as_admins(user, users):
        print('user %i is setting users %s as admins' % (user, str(users)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join(users)
            c.execute('UPDATE listsForUsers SET admin=1 WHERE list_id=%i user_id IN (%s)'
                      % (working_list, values))

    @staticmethod
    def is_admin(user):
        print('checking if user %i is an admin' % user)
        with knibot_db.connect() as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            c.execute('SELECT admin FROM listsForUsers WHERE list_id=%i AND user_id=%i'
                      % (working_list, user))
    
    @staticmethod
    def set_working_list(user, list_name, state=0):
        print('setting %s as working list for user %i' % (list_name, user))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM lists WHERE id IN ('
                      'SELECT list_id FROM listsForUsers WHERE user_id=%i)'
                      'AND name=\'%s\'' % (user, list_name))
            working_list = c.fetchone()
            if working_list is None:
                raise ValueError(prompts_he.not_exists_err % list_name)
            c.execute('INSERT INTO workingLists (user_id, list_id, state) VALUES (%i, %i, %i)'
                      'ON CONFLICT (user_id) DO UPDATE SET list_id=EXCLUDED.list_id, state=EXCLUDED.state' %
                      (user, working_list[0], state))
    
    @staticmethod
    def get_working_list(user, c):
        c.execute('SELECT list_id FROM workingLists WHERE user_id=%i' % user)
        working_list = c.fetchone()
        if working_list is None:
            raise LookupError(prompts_he.no_working_list_err)
        return working_list[0]
    
    @staticmethod
    def set_working_state(user, state):
        print('setting working state for user %i as %s' % (user, {0: 'default', 1: 'write', 2: 'erase', 3: 'share'}[state]))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('UPDATE workingLists SET state=%i WHERE user_id=%i' % (state, user))
    
    @staticmethod
    def get_working_state(user):
        print('fetching working state for user %i' % user)
        with knibot_db.connect() as conn:
            c = conn.cursor()
            c.execute('SELECT state FROM workingLists WHERE user_id=%i' % user)
            state = c.fetchone()
            if state is None:
                raise ValueError(prompts_he.no_working_list_err)
            return state[0]
    
    @staticmethod
    def add_items(user, items):
        print('user %i is adding items %s' % (user, str(items)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join('(\'%s\', %i, %i)' % (i, working_list, user) for i in items)
            c.execute('INSERT INTO items (name, list_id, request_by) VALUES %s' % values)
    
    @staticmethod
    def remove_items(user, items):
        print('user %i is removing items %s' % (user, str(items)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join('\'%s\'' % i for i in items)
            c.execute('DELETE FROM items WHERE list_id=%i AND name IN (%s)'
                      % (working_list, values))
    
    @staticmethod
    def remove_all_items(user):
        print('user %i is removing all items' % user)
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM items WHERE list_id=%i' % knibot_db.get_working_list(user, c))
    
    @staticmethod
    def remove_all_items_but(user, items):
        print('user %i is removing all items but %s' % (user, str(items)))
        with knibot_db.connect(commit=True) as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join('\'%s\'' % i for i in items)
            c.execute('DELETE FROM items WHERE list_id=%i AND name NOT IN (%s)' %
                      (working_list, values))
    
    @staticmethod
    def get_list_items(user):
        print('fetching list items for user %i' % user)
        with knibot_db.connect() as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            c.execute('SELECT * FROM items WHERE list_id=%i' % working_list)
            return c.fetchall()
    
    @staticmethod
    def get_list_users(user):
        print('fetching list users for user %i' % user)
        with knibot_db.connect() as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            c.execute('SELECT * FROM listsForUsers WHERE list_id=%i AND user_id!=%i' % (working_list, user))
            return c.fetchall()
    
    @staticmethod
    def get_existing_items(user, items):
        print('fetching items from %s that already exist' % str(items))
        with knibot_db.connect() as conn:
            c = conn.cursor()
            working_list = knibot_db.get_working_list(user, c)
            values = ', '.join('\'%s\'' % i for i in items)
            c.execute('SELECT name FROM items WHERE list_id=%i AND name IN (%s)' % (working_list, values))
            return [item[0] for item in c.fetchall()]

    @staticmethod
    def get_lists_for_user(user):
        print('fetching lists for user %i' % user)
        with knibot_db.connect() as conn:
            c = conn.cursor()
            c.execute('SELECT name FROM lists WHERE id IN'
                      '(SELECT list_id FROM listsForUsers WHERE user_id=%i)' % user)
            return c.fetchall()


if __name__ == '__main__':
    knibot_db.create()
    user = 100
    knibot_db.create_list(user, 'poo')
    knibot_db.set_working_list(user, 'poo')
    knibot_db.add_items(user, ['a', 'b', 'c'])
