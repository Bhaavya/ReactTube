from flask import Flask,jsonify,render_template,request,redirect,url_for
from oauth2client import client, crypt
from create_user_db import *
from ret_update_videos import *
import json

app = Flask(__name__)
CLIENT_ID = '444408769051-59atkr4ne088j3q01bt49gh1hl0nt3ar.apps.googleusercontent.com'
conn = MongoClient('mongodb://bhavya:Radhika24@ds013901.mlab.com:13901/react_tube')
db = conn['react_tube']
es = Elasticsearch()
userId='571a5259dd4fbd754018ef87'
# route for handling the login page logic
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        token = request.form['idtoken']
        try:
            idinfo = client.verify_id_token(token, CLIENT_ID)
            #verify if token id is sent by google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
        except crypt.AppIdentityError as e:
            # Invalid token
            return render_template('login.html',error =e)

        userid = idinfo['sub']
        #add new users to database
        sign_in(userid,db)
        return (url_for('main_page'))
    return render_template('login.html')

@app.route('/main_page',methods=['GET','POST'])

def main_page():
    return render_template('search.html')

@app.route('/search',methods=['POST'])
def search():
    if request.method == 'POST':
        tags = []
        query = ""
        all_query_words = request.form['query']
        print(all_query_words)
        for q in all_query_words.split(','):
            if q.lower() in ["cute","funny","popular"]:
                tags.append(q)
            else:
                query += " " + q
        print (tags)
        relevant_videos = search_videos(query.strip(),tags,es,index='videos',doc_type='video')
        print(relevant_videos)
        return (jsonify(result=relevant_videos))
    return redirect('login.html')

@app.route('/update_votes',methods=['POST'])
def update_votes():
        video_id = request.form['videoId']
        type = request.form['type']

        if up_vote(userId,type,video_id,db):
            type= get_vote_type(type)
            new_votes= update_es_votes(video_id,es,'videos','video',type,1)
        else:
            type= get_vote_type(type)
            new_votes = update_es_votes(video_id,es,'videos','video',type,1,False)
        return (jsonify({"videoId":video_id,"numVotes":new_votes,"type":type}))



@app.route('/')
def index():
    return render_template('login.html')

def get_vote_type(type):
    if type.lower() == "good":
        return "yass"
    elif type.lower() =="cute":
        return "aww"
    else:
        return "lol"

if __name__ == '__main__':
    app.run(host='localhost',port=8081,debug=True)