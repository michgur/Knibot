import sqlite3

import prompts


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


STATE_DEFAULT = 0
STATE_WRITING = 1
STATE_ERASING = 2


def create_list(user, list_name):
    print('%i is creating a new list %s' % (user, list_name))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM lists WHERE id IN ('
                  'SELECT list_id FROM listsForUsers WHERE user_id=?)'
                  'AND name=?', (user, list_name))
        if c.fetchone() is not None:
            raise ValueError(prompts.already_exists_err % list_name)
        c.execute('INSERT INTO lists (name) VALUES ("%s")' % list_name)
        if user != 0:
            c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES (?, ?, 1)',
                      (c.lastrowid, user))
        return c.lastrowid


def add_users_to_list(list_name, users, admins=None):
    print('adding users %s to list %s' % (str(users), list_name))
    if admins is None:
        admins = []
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM lists WHERE name="%s"' % list_name)
        working_list = c.fetchone()[0]
        values = ', '.join("(%i, %i, %i)" % (working_list, u, 1 if u in admins else 0) for u in users)
        c.execute('INSERT INTO listsForUsers (list_id, user_id, admin) VALUES %s' % values)


def set_working_list(user, list_name, state=0):
    print('setting %s as working list for user %i' % (list_name, user))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM lists WHERE id IN ('
                  'SELECT list_id FROM listsForUsers WHERE user_id=?)'
                  'AND name=?', (user, list_name))
        working_list = c.fetchone()
        if working_list is None:
            raise ValueError(prompts.not_exists_err % list_name)
        c.execute('REPLACE INTO workingLists (user_id, list_id, state) VALUES (?, ?, ?)',
                  (user, working_list[0], state))


def get_working_list(user, c):
    c.execute('SELECT list_id FROM workingLists WHERE user_id=%i' % user)
    working_list = c.fetchone()
    if working_list is None:
        raise LookupError('no working list for user %i' % user)
    return working_list[0]


def set_working_state(user, state):
    print('setting working state for user %i as %s' % (user, {0: 'default', 1: 'write', 2: 'erase'}[state]))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('UPDATE workingLists SET state=? WHERE user_id=?', (state, user))


def get_working_state(user):
    print('fetching working state for user %i' % user)
    with knibot_db.connect() as conn:
        c = conn.cursor()
        c.execute('SELECT state FROM workingLists WHERE user_id=?', (user,))
        state = c.fetchone()
        if state is None:
            raise ValueError(prompts.no_working_list_err)
        return state[0]


def add_items(user, items):
    print('user %i is adding items %s' % (user, str(items)))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        working_list = get_working_list(user, c)
        values = ', '.join('("%s", %i, %i)' % (i, working_list, user) for i in items)
        c.execute('INSERT INTO items (name, list_id, request_by) VALUES %s' % values)


def remove_items(user, items):
    print('user %i is removing items %s' % (user, str(items)))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        working_list = get_working_list(user, c)
        values = ', '.join('"%s"' % i for i in items)
        c.execute('DELETE FROM items WHERE list_id=%i AND name IN (%s)'
                  % (working_list, values))


def remove_all_items(user):
    print('user %i is removing all items' % user)
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM items WHERE list_id=%i' % get_working_list(user, c))


def remove_all_items_but(user, items):
    print('user %i is removing all items but %s' % (user, str(items)))
    with knibot_db.connect(commit=True) as conn:
        c = conn.cursor()
        working_list = get_working_list(user, c)
        values = ', '.join('"%s"' % i for i in items)
        c.execute('DELETE FROM items WHERE list_id=%i AND name NOT IN (%s)' %
                  (working_list, values))


def get_list_items(user):
    print('fetching list items for user %i' % user)
    with knibot_db.connect() as conn:
        c = conn.cursor()
        working_list = get_working_list(user, c)
        c.execute('SELECT * FROM items WHERE list_id=%i' % working_list)
        return c.fetchall()


def get_existing_items(user, items):
    print('fetching items from %s that already exist' % str(items))
    with knibot_db.connect() as conn:
        c = conn.cursor()
        working_list = get_working_list(user, c)
        values = ', '.join('"%s"' % i for i in items)
        c.execute('SELECT name FROM items WHERE list_id=%i AND name IN (%s)' % (working_list, values))
        return [item[0] for item in c.fetchall()]


# c.execute('CREATE TABLE lists ('
#           'id INTEGER PRIMARY KEY,'
#           'name TEXT NOT NULL)')
# c.execute('CREATE TABLE listsForUsers ('
#           'list_id INTEGER,'
#           'user_id INTEGER,'
#           'admin INTEGER,'
#           'FOREIGN KEY(list_id) REFERENCES lists(id))')
# c.execute('CREATE TABLE items ('
#           'name TEXT NOT NULL,'
#           'list_id INTEGER,'
#           'request_by INTEGER,'
#           'FOREIGN KEY(list_id) REFERENCES lists(id))')
# c.execute('CREATE TABLE workingLists ('
#           'user_id INTEGER UNIQUE,'
#           'list_id INTEGER,'
#           'state INTEGER,'
#           'FOREIGN KEY(list_id) REFERENCES lists(id))')
if __name__ == '__main__':
    pass
    # with knibot_db.connect(commit=True) as conn:
    #     c = conn.cursor()
        # c.execute('DELETE FROM listsForUsers')
        # c.execute('DELETE FROM lists')
        # c.execute('DELETE FROM items')
        # c.execute('DELETE FROM workingLists')
