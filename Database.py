import sqlite3
import os.path
import datetime
import re


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


class Database:
    # Database Class
    def __init__(self):
        self.__db_name = 'reservation.db'
        self.__db_folder = 'Database'
        self.__open_db()
        self.__time_format = '%Y-%m-%d %H:%M'
        self.__conn.create_function("REGEXP", 2, regexp)

    def __get_path(self):
        # get database config file path
        basedir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(basedir, self.__db_folder, self.__db_name)

    def __open_db(self):
        # open Database
        if not os.path.exists(self.__get_path()):
            self.__conn = self.__make_db()
            self.__create_tables(self.__conn)
        else:
            # check_same_thread is extremely important for flask integration
            # there may be some concurrency problems, but this is the only way
            # that a DB connection can be defined in one thread and used in another
            self.__conn = sqlite3.connect(self.__get_path(), check_same_thread=False)
        self.__set_row_factory()
        return

    def __make_db(self):
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.__db_folder)):
            os.mkdir(self.__db_folder)
        return sqlite3.connect(self.__get_path())

    def __create_tables(self, db_conn):
        self.create_machine_table(db_conn)
        self.create_reservations_table(db_conn)
        self.create_transaction_table(db_conn)
        self.create_user_table(db_conn)

    def __set_row_factory(self):
        # From https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.__conn.row_factory = dict_factory

    @staticmethod
    def create_machine_table(db_conn):
        create_statement = """ 
            CREATE TABLE machine (
                          id INTEGER PRIMARY KEY,
                machine_type VARCHAR NOT NULL,
                        cost INTEGER NOT NULL
            ); 
            """
        db_conn.execute(create_statement)
        insert_statement = """
            INSERT INTO machine (id, machine_type, cost)
            VALUES (11, 'Workshop', 99),
                   (12, 'Workshop', 99),
                   (13, 'Workshop', 99),
                   (14, 'Workshop', 99),
                   (21, 'Microvac', 2000),
                   (22, 'Microvac', 2000),
                   (31, 'Irradiator', 2200),
                   (32, 'Irradiator', 2200),
                   (41, 'Extruder', 500),
                   (42, 'Extruder', 500),
                   (51, 'Crusher', 10000),
                   (61, 'Harvester', 8800)
            """
        db_conn.execute(insert_statement)
        db_conn.commit()

    @staticmethod
    def create_reservations_table(db_conn):
        create_statement = """ 
            CREATE TABLE reservations (
                            id INTEGER PRIMARY KEY,
                    machine_id INTEGER,
                       user_id INTEGER,
                start_datetime VARCHAR NOT NULL,
                  end_datetime VARCHAR NOT NULL,
                         price DOUBLE NOT NULL,
                        status BOOL NOT NULL,
                   FOREIGN KEY (machine_id) REFERENCES machine (id),
                   FOREIGN KEY (user_id) REFERENCES users (user_id)
            ); 
            """
        db_conn.execute(create_statement)
        db_conn.commit()

    @staticmethod
    def create_transaction_table(db_conn):
        create_statement = """ 
            CREATE TABLE transactions (id INTEGER PRIMARY KEY,
            reservation_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount DOUBLE NOT NULL,
            type VARCHAR NOT NULL,
            datetime_stamp VARCHAR NOT NULL,
            FOREIGN KEY (reservation_id) REFERENCES reservation(id),
            FOREIGN KEY (user_id) REFERENCES users(user_id));
            """
        db_conn.execute(create_statement)
        db_conn.commit()

    @staticmethod
    def create_user_table(db_conn):
        sql = '''CREATE TABLE users (
                username VARCHAR(30) NOT NULL,
                password VARCHAR(100) NOT NULL,
                balance INT NOT NULL,
                status INT NOT NULL,
                client_flag INT NOT NULL,
                user_id INTEGER PRIMARY KEY,
                UNIQUE (user_id),
                UNIQUE(username));'''
        db_conn.execute(sql)

    def reset_db(self):
        delete = 'DELETE FROM reservations'
        self.__conn.execute(delete)
        delete = 'DELETE FROM users'
        self.__conn.execute(delete)
        delete = 'DELETE FROM transactions'
        self.__conn.execute(delete)
        self.__conn.commit()

    def create_user(self, username, password, user_type):
        # check and create user
        check_sql = "SELECT * FROM users WHERE username = '{}'"
        insert_sql = "INSERT INTO users (username, password, balance, status, client_flag) " \
                     "VALUES ('{}', '{}', {}, {}, {})"
        cursor = self.__conn.cursor()
        cursor.execute(check_sql.format(username))
        ret = cursor.fetchone()
        if not ret:
            if user_type.upper() == 'CLIENT':
                cursor.execute(insert_sql.format(username, password, 0, 1, 1))
                self.__conn.commit()
                return True
            elif user_type.upper() == 'FM':
                cursor.execute(insert_sql.format(username, password, 0, 1, 0))
                self.__conn.commit()
                return True
            else:
                return False
        else:
            return False

    def grant_access(self, username, password):
        # login check
        sql = "SELECT * FROM users where username = '{}' AND password = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(sql.format(username, password))
        ret = cursor.fetchone()
        if ret is not None:
            return True
        else:
            return False

    def deactivate_user(self, username):
        # check and set user status to 0
        return self.activation_helper(username, 0)

    def reactivate_user(self, username):
        # check and set user status to 1
        return self.activation_helper(username, 1)

    def activation_helper(self, username, act_type):
        check_sql = "SELECT * FROM users WHERE username = '{}'"
        update_sql = "UPDATE users SET status = '{}' WHERE username = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(check_sql.format(username))
        ret = cursor.fetchone()
        if ret is not None:
            cursor.execute(update_sql.format(act_type, username))
            self.__conn.commit()
            return True
        else:
            return False

    def get_info(self, username):
        check_sql = "SELECT * FROM users WHERE username = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(check_sql.format(username))
        ret = cursor.fetchone()
        if ret is not None:
            is_active = ret['status'] == 1
            user_type = 'client' if ret['client_flag'] == 1 else 'FM'
            ret_dct = {'funds': ret['balance'], 'is_active': is_active, 'type': user_type,
                       'password': hash(ret['password'])}
            return ret_dct
        else:
            return None

    def edit_user(self, username, new_username=None, password=None, add_funds=None, is_active=None):
        check_sql = "SELECT * FROM users WHERE username = '{}'"

        cursor = self.__conn.cursor()
        if password:
            update_sql = "UPDATE users set password = '{}' WHERE username = '{}'"
            cursor.execute(update_sql.format(password, username))
            self.__conn.commit()
        if add_funds:
            update_sql = "UPDATE users set balance = balance + '{}' WHERE username = '{}'"
            cursor.execute(update_sql.format(add_funds, username))
            self.__conn.commit()
        if is_active is not None:
            update_sql = "UPDATE users set status = '{}' WHERE username = '{}'"
            cursor.execute(update_sql.format(1 if is_active else 0, username))
            self.__conn.commit()
        if new_username:
            cursor.execute(check_sql.format(new_username))
            ret = cursor.fetchone()
            update_sql = "UPDATE users set username = '{}' WHERE username = '{}'"
            if ret is not None:
                return False
            else:
                cursor.execute(update_sql.format(new_username, username))
                self.__conn.commit()
                return True
        else:
            return True

    def add_balance(self, username, add_funds):
        update_sql = "UPDATE users set balance = balance + '{}' " \
                     "WHERE username = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(update_sql.format(add_funds, username))
        self.__conn.commit()
        return True

    def show_balance(self, username):
        check_sql = "SELECT balance FROM users WHERE username = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(check_sql.format(username))
        ret = cursor.fetchone()
        return {'balance': ret['balance']}

    def search_client(self, partial_username):
        check_sql = "SELECT * FROM users WHERE (username REGEXP '{}')"
        cursor = self.__conn.cursor()
        cursor.execute(check_sql.format(partial_username))
        ret = cursor.fetchall()
        if not ret:
            return None
        else:
            user_lst = []
            for user in ret:
                is_active = True if user['status'] == 1 else False
                user_type = 'client' if user['client_flag'] == 1 else 'FM'
                user_lst.append({"username": user['username'],
                                 "funds": user['balance'],
                                 "is_active": is_active,
                                 "type": user_type})
            return user_lst

    def list_clients(self):
        sql = "SELECT username FROM users WHERE client_flag = 1"
        cursor = self.__conn.cursor()
        cursor.execute(sql)
        ret = cursor.fetchall()
        client_lst = []
        for client in ret:
            client_lst.append(client['username'])
        return client_lst

    def get_user_id(self, username):
        sql = "SELECT user_id FROM users WHERE username = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(sql.format(username))
        ret = cursor.fetchone()
        if ret is None:
            return None
        else:
            return ret['user_id']

    def get_username(self, user_id):
        sql = "SELECT username FROM users WHERE user_id = '{}'"
        cursor = self.__conn.cursor()
        cursor.execute(sql.format(user_id))
        ret = cursor.fetchone()
        if ret is None:
            return None
        else:
            return ret['username']

    def valid_machine(self, machine_type):
        cursor = self.__conn.cursor()
        query = f"""
                        SELECT machine_type 
                          FROM machine
                         WHERE machine_type = \'{machine_type}\'
                """
        cursor.execute(query)
        if cursor.fetchone():
            return True
        else:
            return False

    def find_available_machine(self, machine_type, start_datetime, end_datetime):
        # check if the machine item type is valid
        cursor = self.__conn.cursor()
        query = f"""
                SELECT id 
                  FROM machine
                 WHERE machine_type = \'{machine_type}\'
                   AND id NOT IN (
                       SELECT m.id FROM machine AS m
                   INNER JOIN reservations AS r
                           ON m.id = r.machine_id
                          AND \'{start_datetime}\' <= r.end_datetime 
                          AND \'{end_datetime}\' >= r.start_datetime)
        """
        cursor.execute(query)
        ret = cursor.fetchone()
        if ret:
            return ret["id"]
        else:
            return None

    def add_transaction(self, amount, transaction_type, reservation_id, username):
        cursor = self.__conn.cursor()
        datetime_stamp = datetime.datetime.now().strftime(self.__time_format)
        user_id = self.get_user_id(username)
        insert_statement = f"""
            INSERT INTO transactions (amount, type, datetime_stamp, reservation_id, user_id)
                 VALUES ({amount}, \'{transaction_type}\', \'{datetime_stamp}\', {reservation_id}, {user_id})
        """
        cursor.execute(insert_statement)
        self.__conn.commit()
        return cursor.lastrowid

    def add_reservation(self, start_datetime, end_datetime, price, status, machine_id, username):
        cursor = self.__conn.cursor()
        user_id = self.get_user_id(username)
        if status:
            statusval = 1
        else:
            statusval = 0
        insert_statement = f"""
            INSERT INTO reservations (start_datetime, end_datetime, price, status, machine_id, user_id)
                 VALUES (\'{start_datetime}\', \'{end_datetime}\', {price}, {statusval}, {machine_id}, {user_id})
        """
        cursor.execute(insert_statement)
        self.__conn.commit()
        return cursor.lastrowid

    def edit_reservation(self, reservation_id, start_datetime=None, end_datetime=None, price=None, status=None):
        cursor = self.__conn.cursor()
        updates = []
        if start_datetime:
            updates.append(f"start_datetime = \'{start_datetime}\'")
        if end_datetime:
            updates.append(f"end_datetime = \'{end_datetime}\'")
        if price:
            updates.append(f"price = {price}")
        if status is not None:
            updates.append(f"status = {status}")
        update_string = ', '.join(updates)
        update_statement = f"""
            UPDATE reservations
               SET {update_string}
             WHERE id = {reservation_id}
        """
        cursor.execute(update_statement)
        self.__conn.commit()

    def reservation_details(self, reservation_id=None, start_datetime=None, end_datetime=None, status=None,
                            machine=None, username=None):
        cursor = self.__conn.cursor()
        criteria = []
        where_statement = ''
        if reservation_id:
            criteria.append(f"r.id = {reservation_id}")
        if start_datetime:
            criteria.append(f"r.start_datetime >= \'{start_datetime}\'")
        if end_datetime:
            criteria.append(f"r.end_datetime <= \'{end_datetime}\'")
        if status:
            criteria.append(f"r.status = {status}")
        if machine:
            criteria.append(f"m.machine_type = \'{machine}\'")
        if username:
            user_id = self.get_user_id(username)
            criteria.append(f"r.user_id = {user_id}")
        if criteria:
            where_statement = "WHERE " + " AND ".join(criteria)
        query = f"""
            SELECT r.id, r.start_datetime, r.end_datetime, r.status, m.machine_type, r.user_id, r.price
              FROM reservations AS r
              LEFT JOIN machine AS m
                     ON r.machine_id = m.id
              {where_statement}
        """
        cursor.execute(query)
        return cursor.fetchall()

    def transaction_details(self, transaction_id=None, transaction_type=None, reservation_id=None, username=None,
                            start_datetime=None, end_datetime=None):
        cursor = self.__conn.cursor()
        criteria = []
        where_statement = ''
        if transaction_id:
            criteria.append(f"id = {transaction_id}")
        if reservation_id:
            criteria.append(f"reservation_id = {reservation_id}")
        if transaction_type:
            criteria.append(f"type = \'{transaction_type}\'")
        if username:
            user_id = self.get_user_id(username)
            criteria.append(f"user_id = {user_id}")
        if start_datetime:
            criteria.append(f"datetime_stamp >= \'{start_datetime}\'")
        if end_datetime:
            criteria.append(f"datetime_stamp <= \'{end_datetime}\'")
        if criteria:
            where_statement = "WHERE " + " AND ".join(criteria)
        query = f" SELECT * FROM transactions {where_statement} "
        cursor.execute(query)
        return cursor.fetchall()

    def get_cost(self, machine):
        cursor = self.__conn.cursor()
        query = f" SELECT cost FROM machine WHERE machine_type = \'{machine}\' "
        cursor.execute(query)
        return cursor.fetchone()['cost']
