import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the instance variable conn.
        """
        self.conn = sqlite3.connect("venmo2.db", check_same_thread=False)
        self.create_user_table()
        self.create_transaction_table()

    def create_user_table(self):
        """
        Using SQL, creates a user table
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS user(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          username TEXT NOT NULL,
                          balance INTEGER NOT NULL                          
        );""")

#FOREIGN KEY(sender_id) REFERENCES user(id),
                        #FOREIGN KEY(receiver_id) REFERENCES user(id)  
    def create_transaction_table(self):
        """
        Using SQL, creates a transaction table.
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        amount INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        accepted BOOLEAN,
                        FOREIGN KEY(sender_id) REFERENCES user(id),
                        FOREIGN KEY(receiver_id) REFERENCES user(id)                            
        );""")
        
        

    def delete_user_table(self):
        """
        Using SQL, deletes a user table
        """
        self.conn.execute("""
        DROP TABLE IF EXISTS user;
        """)

    def get_all_users(self):
        """
        Using SQL, returns all the users in a table
        """
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users
    
    def insert_user_table(self, name, username, balance):
        """
        Using SQL, inserts a user into a user table
        """
        cursor = self.conn.execute("""
        INSERT INTO user(name, username, balance)  VALUES (?, ?, ?);""", (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_by_id(self, user_id):
        """
        Using SQL, get a user by its id
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (user_id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None
    
    def get_transaction_by_id(self, transaction_id):
        """
        Using SQL, get a transaction by its id
        """
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id = ?;", (transaction_id,))
        for row in cursor:
            return {
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5], 
                "accepted": row[6]
                }
        return None
    
    
    
    def get_transaction_by_userid(self, user_id):
        """
        Using SQL, get a transaction by the sender or receiver's id
        """
        txn = []
        cursor = self.conn.execute("""SELECT * FROM transactions WHERE sender_id = ?;""", (user_id,))
        print(cursor, "cursor")
        for row in cursor:
            txn.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5], 
                "accepted": row[6]
                })
        cursor = self.conn.execute("""SELECT * FROM transactions WHERE receiver_id = ?;""", (user_id,))
        for row in cursor:
            txn.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5], 
                "accepted": row[6]
                })
        print(txn, "txn")
        return txn    
    
    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user by its id
        """
        self.conn.execute("""
                          DELETE FROM user WHERE id = ?""", (id,))
    def delete_transaction_by_id(self, id):
        """
        Using SQL, deletes a transaction by its id
        """
        self.conn.execute("""
                          DELETE FROM transactions WHERE id = ?""", (id,))
    
    def insert_user_transaction(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        """
        Using SQL, inserts a transaction into a transaction table
        """
        cursor = self.conn.execute("""
        INSERT INTO transactions(timestamp, sender_id, receiver_id, amount, message, accepted)  VALUES (?, ?, ?, ?, ?, ?);""", (timestamp, sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid
        
    def update_user_by_id(self, id, balance):
        """
        Using SQL, updates a user's balance by its id
        """
        self.conn.execute("""
        UPDATE user SET balance = ?
                        WHERE id = ?""", (balance, id))
        self.conn.commit()
    
    def update_transaction(self, id, accepted, timestamp):
        """
        Using SQL, updates a user's transaction's timestamp and accepted field
        """
        self.conn.execute("""
        UPDATE transactions SET accepted = ?,
                        timestamp = ?
                        WHERE id = ?""", (accepted, timestamp, id))
        self.conn.commit()

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)