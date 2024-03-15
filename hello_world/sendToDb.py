from connectToDb import email_collection, user_collection
from bson import ObjectId
from datetime import datetime
import json

def sendToDb(emails, names, companies, current_designation, user_id):
    
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if user is None:
            print(f"User with id {user_id} not found.")
            raise Exception("User not found")
        

        for i in range(len(emails)):
            if not emails[i]:
                continue
            
            email_found = email_collection.find_one({"email" : emails[i]})
            
            if user["emailSelected"] and email_found and email_found["_id"] in user["emailSelected"]:
                    print("skipped")
                    continue

            inserted_email = email_collection.insert_one({
                "email": emails[i],
                "name": names[i],
                "company": companies[i],
                "currentDesingation": current_designation[i],
                "addedOn" : datetime.now()
            })
            
            user_collection.update_one(
                filter= {
                    "_id" : ObjectId(user_id)
                },
                update= {
                    "$addToSet" : {"emailSelected" : inserted_email.inserted_id}
                }
            )
            print("sent")

        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    