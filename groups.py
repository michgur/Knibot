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


if __name__ == '__main__':
    with knibot_db.connect() as conn:
        print(conn, type(conn))
