from extract_videos import ExtractVideos
from elasticsearch import Elasticsearch

API_KEY= 'AIzaSyD3McHCDyrh1Ncf02EW9Sc_iW_hwhsr5js'
YOUTUBE_API_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

#extracts videos from different query seeds and returns a dictionary of videos
def get_videos(queries):
     videos = {}
     video_extractor = ExtractVideos(API_KEY,YOUTUBE_API_NAME,YOUTUBE_API_VERSION)
     for query in queries:
        videos.update(video_extractor.get_videos_from_query(query))
     return videos

#indexes dictionary of videos in ElasticSearch
def save_videos(videos, index, doc_type):
    es = Elasticsearch()
    for id,video in videos.items():
        es.index(index = index, id = id, doc_type=doc_type ,body =
        {'title':video["title"],
         'description': video["description"],
         'lol': video["lol"],
         'aww': video["aww"],
         'yass': video["yass"]} )

if __name__ == '__main__':
    queries = ["Python tutorial","Cats","Taylor Swift","Funny Vines"]
    videos = get_videos(queries)
    save_videos(videos,"videos","video")
