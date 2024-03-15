from pymongo import MongoClient

client = MongoClient("mongodb+srv://winterprojectiiitm:ZWSAl0qypIwazq8n@communet.mhdgh6b.mongodb.net/?retryWrites=true&w=majority")

db = client["test"]

email_collection = db.get_collection("emails")
user_collection = db.get_collection("users")