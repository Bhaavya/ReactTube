import unittest
from create_user_db import *

class TestIndex(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient('mongodb://bhavya:Radhika24@ds013901.mlab.com:13901/react_tube')
        self.db = self.client['react_tube']

    def test_sign_in(self):
        #only 1 document created for a user
        sign_in("123",self.db)
        sign_in("123",self.db)
        self.assertEqual(self.db["user"].find({"user_id":"123"}).count(),1)

        sign_in("345",self.db)
        sign_in("891",self.db)
        user = self.db["user"].find_one({"user_id":"123"})
        #playlists are empty initially
        self.assertEqual(user["good"],[])


    def test_up_vote(self):
        #a video is added to a playlist only once
        up_vote("123", "cute", "456",self.db)
        up_vote("123", "cute", "456",self.db)
        user = self.db["user"].find_one({"user_id":"123"})
        self.assertEqual(user["cute"], ["456"])

    def test_undo_vote(self):
        #video is removed from playlist on undo
        undo_vote("123", "cute", "456",self.db)
        user = self.db["user"].find_one({"user_id":"123"})
        self.assertEqual(user["cute"], [])

    def tearDown(self):
        self.client.close()


