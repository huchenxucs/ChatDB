import pymysql
from prettytable import PrettyTable


def sql_result_to_table_str(sql_result):
    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = sql_result[0].keys()

    # Add rows to the table
    for row in sql_result:
        table.add_row(row.values())
    table.float_format = ".2"
    return str(table)


class MySQLDB(object):
    def __init__(self, host, port, user, password, database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_sql(self, sql, raise_err=False):
        try:
            self.connect()
            for sub_sql in sql.split(";"):
                sub_sql = sub_sql.strip()
                if len(sub_sql) > 0:
                    self.cursor.execute(sub_sql)
            result = self.cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            error_message = f"SQL error: {str(e)}"
            if raise_err:
                raise e
            else:
                return e, error_message
        finally:
            self.disconnect()

        # print(result)
        # convert query result to string
        if result:
            # rows = [', '.join(str(v) for v in row.values()) for row in result]
            # header = ', '.join(result[0].keys())
            # out_str = f"{header}\n{'-' * len(header)}\n" + '\n'.join(rows)
            out_str = sql_result_to_table_str(result)
        else:
            if "create" in sql.lower():
                out_str = "create table successfully."
            elif "insert" in sql.lower():
                out_str = "insert data successfully."
            elif "delete" in sql.lower():
                out_str = "delete data successfully."
            elif "update" in sql.lower():
                out_str = "update data successfully."
            else:
                out_str = "no results found."

        return result, out_str

    def select(self, table, columns="*", condition=None):
        sql = f"SELECT {columns} FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        return self.execute_sql(sql)

    def insert(self, table, data):
        keys = ','.join(data.keys())
        values = ','.join([f"'{v}'" for v in data.values()])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        return self.execute_sql(sql)

    def update(self, table, data, condition):
        set_values = ','.join([f"{k}='{v}'" for k, v in data.items()])
        sql = f"UPDATE {table} SET {set_values} WHERE {condition}"
        return self.execute_sql(sql)

    def delete(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_sql(sql)

    def create_database(self, database):
        try:
            self.execute_sql(f"DROP DATABASE `{database}`", raise_err=True)
        except Exception as e:
            pass
        sql = f"CREATE DATABASE `{database}`"
        self.execute_sql(sql, raise_err=True)
        if self.database is None:
            self.database = database

    def drop_database(self, ):
        assert self.database is not None
        sql = f"DROP DATABASE `{self.database}`"
        self.execute_sql(sql, raise_err=True)
        self.database = None

    # def __del__(self):
    #     if self.database is not None:
    #         self.drop_database()


if __name__ == '__main__':
    from config import cfg
    mysql = MySQLDB(host=cfg.mysql_host, user=cfg.mysql_user, password=cfg.mysql_password,
                    port=cfg.mysql_port, database="try2")
