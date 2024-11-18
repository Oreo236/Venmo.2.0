from datetime import datetime
import json

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users from the database including their basic information
    """
    return json.dumps({"users": DB.get_all_users()}), 200

@app.route("/api/users/", methods = ["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name", 0)
    username = body.get("username", 0)
    balance = body.get("balance", 0)
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 400
    if name == 0:
        return json.dumps({"error": "Invalid input: name"}), 400
    if username == 0:
        return json.dumps({"error": "Invalid input: username"}), 400
    user["transactions"] = []
    return json.dumps(user), 201

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user from the database including all of their information
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    transaction = DB.get_transaction_by_userid(user_id)
    if transaction is None:
        transaction = []
    user["transactions"] = transaction
    return json.dumps(user), 200

@app.route("/api/users/<int:user_id>/", methods = ["DELETE"] )
def delete_user(user_id):
    """
    Endpoint for deleting a user from the database including all of their information
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    transaction = DB.get_transaction_by_userid(user_id)
    if transaction is None:
        transaction = []
    user["transactions"] = transaction
    DB.delete_user_by_id(user_id)
    DB.delete_transaction_by_id(user_id)
    return json.dumps(user), 200

@app.route("/api/transactions/", methods = ["POST"])
def create_transactions():
    """
    Endpoint for creating a transaction
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id", None)
    receiver_id = body.get("receiver_id", None)
    amount = body.get("amount", None)
    message = body.get("message", None)
    accepted = body.get("accepted", None)
    if sender_id is None:
        return json.dumps({"error": "Invalid input: sender_id"}), 400
    if receiver_id is None:
        return json.dumps({"error": "Invalid input: receiver_id"}), 404
    if amount is None:
        return json.dumps({"error": "Invalid input: amount"}), 404
    if message is None:
        return json.dumps({"error": "Invalid input: message"}), 404
    
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None:
        return json.dumps({"error": "Sender not found"}), 404
    
    if receiver is None:
        return json.dumps({"error": "Receiver not found"}), 404
    
    sender_balance = sender.get("balance")

    if amount > sender_balance:
        return json.dumps({"error": "Amount exceeds sender's current balance"}), 403

    receiver_balance = receiver.get("balance") + amount
    sender_balance  -= amount
    timestamp = str(datetime.now())
    transaction_id = DB.insert_user_transaction(timestamp, sender_id, receiver_id, amount, message, accepted)
    transaction = DB.get_transaction_by_id(transaction_id)
    if accepted is True:
        DB.update_user_by_id(sender_id, sender_balance)
        
        DB.update_user_by_id(receiver_id, receiver_balance)
    return json.dumps(transaction), 201

@app.route("/api/transactions/<int:transaction_id>/", methods = ["POST"])
def update_accept(transaction_id):
    """
    Endpoint for updation a user's transaction
    """
    body = json.loads(request.data)
    accepted = body.get("accepted", None)
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return json.dumps({"error": "Transaction not found"}), 400 
    if transaction["accepted"] is not None:
        return json.dumps({"error": "Accepted transaction fields cannot be changed"}), 403
    if accepted is True:
        sender_id = transaction["sender_id"]
        receiver_id = transaction["receiver_id"]
        amount = transaction["amount"]
        sender = DB.get_user_by_id(sender_id)
        receiver = DB.get_user_by_id(receiver_id)
        if sender is None:
            return json.dumps({"error": "Sender not found"}), 404
        
        if receiver is None:
            return json.dumps({"error": "Receiver not found"}), 404
        
        sender_balance = sender.get("balance")

        if amount > sender_balance:
            return json.dumps({"error": "Amount exceeds sender's current balance"}), 403

        receiver_balance = receiver.get("balance") + amount
        sender_balance  -= amount
        DB.update_user_by_id(sender_id, sender_balance)
        
        DB.update_user_by_id(receiver_id, receiver_balance)
    timestamp = str(datetime.now())
    DB.update_transaction(transaction_id, accepted, timestamp)
    transaction["timestamp"] = timestamp
    transaction["accepted"] = accepted

    return json.dumps(transaction), 200





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
