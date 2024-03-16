from pymongo import MongoClient

client = MongoClient("")

db = client["test"]

email_collection = db.get_collection("emails")
user_collection = db.get_collection("users")
