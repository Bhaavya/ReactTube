from elasticsearch import Elasticsearch

#gives a list of videos ranked by relevance and number of votes in the required tag categories
def search_videos(query,tags,es,index,doc_type):
    es_query = {
        "query": {
            "function_score": {
                "query": {
                     "multi_match": {
                        "fields": [ "title", "description" ]}
                },
      "boost_mode": "sum",
            }
        }
    }
    #document score = relevance score [+ 0.1*log(1+number of votes in tag1) + ..]
    for tag in tags:
        if tag.lower() == "cute":
            tag="aww"
        elif tag.lower() == "funny":
            tag="lol"
        elif tag.lower() =="popular":
            tag = "yass"
        es_query["query"]["function_score"]["field_value_factor"] = { "modifier": "log1p", "field": tag, "factor":0.1 }
    es_query["query"]["function_score"]["query"]["multi_match"]["query"] = query
    result = es.search(index,doc_type,body = es_query)
    videos = []
    for hit in result["hits"]["hits"]:
        id =  {"id" :hit["_id"]}
        info = hit["_source"]
        info.update(id)
        videos.append(info)
    return videos

#increments or decrements the vote_type by num_votes
def update_es_votes(video_id,es,index,doc_type,vote_type,num_votes,inc=True):
    video= es.get(index= index,doc_type=doc_type,id=video_id)
    old_votes= video["_source"][vote_type]
    if inc:
        es.update(index= index,doc_type=doc_type,id=video_id,body={"doc":{vote_type:old_votes+num_votes}})
        return old_votes+num_votes
    else:
        es.update(index= index,doc_type=doc_type,id=video_id,body={"doc":{vote_type:old_votes-num_votes}})
        return old_votes-num_votes

if __name__ == '__main__':
    es = Elasticsearch()
    print("Total videos: "+str(es.count(index='videos',doc_type='video')["count"]))
    print("\nGood and funny programming videos:")
    result = search_videos("programming", ["lol","yass"],es,index='videos',doc_type='video')
    for video in result:
        print('\nTitle:' +video['title']+'\nDescription:'+video['description']+'\n\nLikes:'+str(video["yass"])+'\nFunny votes:'+str(video["lol"])+'\n')
        print('-------------------------------------------')
    print('-------------------------------------------')
    result = search_videos("programming", [],es,index='videos',doc_type='video')
    print("\nProgramming videos without tag filters:")
    for video in result:
        print('\nTitle:' +video['title']+'\nDescription:'+video['description']+'\n\nLikes:'+str(video["yass"])+'\nFunny votes:'+str(video["lol"])+'\n')
        print('-------------------------------------------')
