import os
import sqlite3


class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect("db.sqlite")
        self.cur = self.conn.cursor()
        sql_query = """SELECT name FROM sqlite_master WHERE type='table';"""
        if not ("recent_files",) in self.cur.execute(sql_query).fetchall():
            self.cur.execute(
                '''
                        CREATE TABLE "recent_files" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "file_path"	TEXT NOT NULL UNIQUE,
                            "last_edit"	INTEGER NOT NULL,
                            PRIMARY KEY("id" AUTOINCREMENT)
                        );
                '''
            )
        if not ("settings",) in self.cur.execute(sql_query).fetchall():
            self.cur.execute(
                '''
                CREATE TABLE "settings" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "name"	TEXT NOT NULL UNIQUE,
                    "value"	TEXT NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );
            '''
            )

    def update_recent(self, filename, time):
        sql_query = f"""
        INSERT INTO recent_files (file_path, last_edit)
        VALUES ("{filename}", {time})
        ON CONFLICT(file_path) DO UPDATE SET last_edit = {time};
        """
        self.cur.execute(sql_query)
        self.conn.commit()

    def delete_record(self, filename):
        sql_query = f"""
                DELETE FROM recent_files
                WHERE file_path="{filename}";
                """
        self.cur.execute(sql_query)
        self.conn.commit()

    def get_recent(self):
        sql_query = """
        SELECT * from recent_files
        ORDER BY last_edit DESC;
        """
        files = self.cur.execute(sql_query).fetchall()
        f = False
        for file in files:
            if not os.path.exists(file[1]):
                self.delete_record(file[1])
                f = True
        if f:
            return self.get_recent()
        return files

    def get_settings(self):
        sql_query = '''
        SELECT * from settings
        '''
        query_res = self.cur.execute(sql_query).fetchall()
        settings = {name: value for i, name, value in query_res}
        return settings

    def save_settings(self, settings):
        sql_query = ""
        for key, value in settings.items():
            sql_query += f"""
                    INSERT INTO settings (name, value)
                    VALUES ("{key}", "{value}")
                    ON CONFLICT(name) DO UPDATE SET value = "{value}";
                    """
        self.cur.executescript(sql_query)
        self.conn.commit()
