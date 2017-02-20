from googleapiclient.discovery import build
import googleapiclient.errors
from nltk.corpus import wordnet
import re
#tool for extracting youtube videos and assigning funny,cute votes and likes using bag of words
class ExtractVideos():
    expression_words = {"funny":[],"cute":[],"good":[]}         #dictionary of words representing emotions
    funny_regex = 'lol(ol)*|haha(ha)*'
    cute_regex = 'aww(w)*'
    like_regex = 'ya(a)*ss(s)*'

    def __init__(self,key,api_name, api_version):
        self.api_key= key
        self.youtube_api_name = api_name
        self.youtube_api_version = api_version
        self.build_expression_words_dict()

    #get videos related to the query using search.list API
    def get_videos_from_query(self, query):
        service = build(self.youtube_api_name,self.youtube_api_version ,developerKey=self.api_key)
        response = service.search().list(
        q = query,type="video",
        part="id,snippet",
        maxResults=30
        ).execute()
        videos ={}
        for result in response.get("items", []):
            if result["id"]["kind"] == "youtube#video":
                video_id = result["id"]["videoId"]
                if video_id not in videos.keys():
                    videos[video_id] = self.get_video_info(result,service)
                    self.get_related_videos(video_id,0,service,videos)
            print(videos)
        return (videos)

    #get video id,title,description and votes in each category from a json result of search.list API
    def get_video_info(self,result,service):
        title = result["snippet"]["title"]
        description = result["snippet"]["description"]
        #calculate votes from title and description
        funny_votes, cute_votes, likes = self.calc_votes(title+description)
        video_id = result["id"]["videoId"]
        #calculate votes from comments
        votes = self.get_votes_from_comments(service,video_id)
        funny_votes += votes[0]
        cute_votes += votes[1]
        likes += votes[2]
        info={"title":title,"description":description,"lol":funny_votes,"aww":cute_votes,"yass":likes}
        return info

    #find videos related to a video_id recursively
    def get_related_videos(self,video_id,depth,service,videos):
        if depth<1:
            response = service.search().list(
            type="video",
            part="id,snippet",
            maxResults=30,
            relatedToVideoId = video_id
            ).execute()
            for result in response.get("items", []):
                if result["id"]["kind"] == "youtube#video":
                    id = result["id"]["videoId"]
                    if id not in videos.keys():
                        videos[id] = self.get_video_info(result,service)
                        self.get_related_videos(id,depth+1,service,videos)

    #calculate votes in each category from comments
    def get_votes_from_comments(self, service,video_id):
        try:
            #find comment threads
            thread_results = service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText"
            ).execute()
            comment_text = ""
            for item in thread_results["items"]:
                comment = item["snippet"]["topLevelComment"]
                comment_text+= comment["snippet"]["textDisplay"]
                parent_id = comment["id"]
                #find replies to comment
                replies = service.comments().list(
                part="snippet",
                parentId=parent_id,
                textFormat="plainText"
                ).execute()
                for item in replies["items"]:
                    comment_text+= item["snippet"]["textDisplay"]
            return self.calc_votes(comment_text)
        #in case comments are disabled
        except googleapiclient.errors.HttpError:
            return (0,0,0)

    #find synonyms of a word from WordNet
    def find_synonyms(self,word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
        return set(synonyms)

    #calculate votes in each category using words in text and return a tuple of votes
    def calc_votes(self,text):
        funny_votes = 0
        cute_votes = 0
        likes = 0
        #find regex representing funnu,cute and good videos
        funny_votes += len(re.findall(ExtractVideos.funny_regex,text,re.IGNORECASE))
        cute_votes += len(re.findall(ExtractVideos.cute_regex,text,re.IGNORECASE))
        likes += len(re.findall(ExtractVideos.like_regex,text,re.IGNORECASE))
        prev_word = ""
        #count number of expression words in text
        for word in text.split():
            #if previous word is "not",votes should not be added
            if prev_word.lower()!="not":
                if word.lower() in ExtractVideos.expression_words["funny"]:
                    funny_votes += 1
                elif word.lower() in ExtractVideos.expression_words["cute"]:
                    cute_votes += 1
                elif word.lower() in ExtractVideos.expression_words["good"]:
                    likes += 1
            prev_word = word
        return (funny_votes,cute_votes,likes)

    #builds dictionary of words signifying emotions in the 3 categories
    def build_expression_words_dict(self):
        ExtractVideos.expression_words["funny"]+=self.find_synonyms("funny")
        ExtractVideos.expression_words["cute"]+=self.find_synonyms("cute")
        #common words under good videos are synonyms of good and enjoy
        ExtractVideos.expression_words["good"]+=self.find_synonyms("good")
        ExtractVideos.expression_words["good"]+=self.find_synonyms("enjoy")
        #add some words not given by wordnet
        ExtractVideos.expression_words["funny"].append("hilarious")
        ExtractVideos.expression_words["cute"].append(["adorable","sweet"])
        ExtractVideos.expression_words["good"].append(["awesome","amazing","nice","great"])

