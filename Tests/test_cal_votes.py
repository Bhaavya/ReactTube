import unittest
from extract_videos import ExtractVideos

API_KEY= 'AIzaSyD3McHCDyrh1Ncf02EW9Sc_iW_hwhsr5js'
YOUTUBE_API_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
#tests number of votes are calculated correctly
class TestIndex(unittest.TestCase):
    def setUp(self):
        self.vid_extractor= ExtractVideos(API_KEY,YOUTUBE_API_NAME,YOUTUBE_API_VERSION)

    def test_cal_votes(self):
        #regex and dictionry words
        text1 = "Hilarious video! LOLOL"
        #presence of not, funny should not be counted
        text2 = "Not funny at all"
        votes = self.vid_extractor.calc_votes(text1)
        self.assertEqual(votes, (2,0,0))
        votes = self.vid_extractor.calc_votes(text2)
        self.assertEqual(votes, (0,0,0))

