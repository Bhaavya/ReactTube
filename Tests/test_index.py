import unittest
from save_videos import save_videos
from elasticsearch import Elasticsearch
from ret_update_videos import update_es_votes
from ret_update_videos import search_videos

#tests indexing,retrieving and updating elasticsearch indices
class TestIndex(unittest.TestCase):
    def setUp(self):
        self.es = Elasticsearch()
        self.index = "test_index"
        self.doc_type = "video"
    #tests all videos are indexed correctly
    def test_save(self):
        videos = {}
        videos['ij123'] = {'title': "Test", "description":"This is a test document", "lol":5000, "aww":100, "yass":10000}
        videos['ij124'] = {'title': "Machine Learning tutorial", "description":"A video on machine learning with python.", "lol":30, "aww":4, "yass":150000}
        videos['ij125'] = {'title': "Machine Learning tutorial", "description":"Another machine learning tutorial with python", "lol":50, "aww":2, "yass":1200}
        videos['ij126'] = {'title': "Time machine", "description":"Time machine will soon become a reality", "lol":10000, "aww":10, "yass":18000}
        save_videos(videos,self.index,self.doc_type)
        num_videos = self.es.count(index=self.index, doc_type = self.doc_type)
        self.assertEqual(num_videos['count'],4)
        video2 = self.es.get(index=self.index,doc_type=self.doc_type,id= 'ij124')
        self.assertEqual(video2['_source']['title'],"Machine Learning tutorial")

    #tests number of votes are updated in the index
    def test_update(self):
        update_es_votes('ij124',self.es,self.index,self.doc_type,'aww',3,inc=False)
        new_video2 = self.es.get(index=self.index,doc_type=self.doc_type,id= 'ij124')
        self.assertEqual(new_video2['_source']['aww'],1)

    #tests search ranking of videos
    def test_search(self):
        videos = search_videos("Machine Learning",["yass"],self.es,self.index,self.doc_type)
        self.assertEqual(videos[0]["id"],'ij124')

if __name__ == '__main__':
    unittest.main()

