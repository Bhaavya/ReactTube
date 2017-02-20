from pymongo import MongoClient

def sign_in(user_id, db):
    #create a new document for a new user only
   if not(bool(db["user"].find_one({"user_id":user_id}))):
       db["user"].insert_one({"user_id":user_id,"cute":[],"good":[],"funny":[]})

#adds video to appropriate playlist if not already present and return true
#else removes it from playlist and returns false
def up_vote(user_id, type_of_vote, video_id, db):
    if not(bool(db["user"].find_one({"user_id":user_id, type_of_vote:video_id}))):
        db["user"].update({"user_id":user_id,},{"$pushAll":{type_of_vote:[video_id]}})
        return True
    else:
        undo_vote(user_id, type_of_vote, video_id, db)
        return False

#remove video from playlist on undo
def undo_vote(user_id, type_of_vote, video_id, db):
    db["user"].update({"user_id":user_id,},{"$pull":{type_of_vote:video_id}})


if __name__ == '__main__':
    conn = MongoClient('mongodb://bhavya:Radhika24@ds013901.mlab.com:13901/react_tube')
    db = conn['react_tube']

