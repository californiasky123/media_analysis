import requests
import json
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup
import codecs
import sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
from empath import Empath
import sqlite3 as sqlite3
#import twitter_secret_data # file that contains OAuth credentials
import nltk 
from nltk.corpus import stopwords
import plotly.plotly as py
import plotly.graph_objs as go


#############
#############
##### SET UP
#############
#############

################# API KEYS 

news_key = ''
client_key = ''
client_secret = ''
resource_owner_key = ''
resource_owner_secret = ''

################# Global variables set up 

CATS = ["positive_emotion", "contentment", "negative_emotion", "power", "anger", "emotional", "sadness", "warmth", "disgust", "dominant_personality", "violence", "healing", "ridicule", "weakness", "envy", "cheerfulness", "hate"]
CATS_DICT = dict(enumerate(CATS))
SOURCES = ["news_api", "twitter", "sotu"]
DBNAME = 'final.db'

################# Twitter set up 

username = "realDonaldTrump"
num_tweets = 100

class Tweet:
    def __init__(self, full_text, retweet_count, favorite_count, id, created_at):
        self.full_text = full_text
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.id = id
        self.created_at = created_at

    def __str__(self):
        descrip = "text:" + self.full_text
        return descrip

################# Cache set up 
 
### Sotu 

U_CACHE_FNAME = 'union_cache.json'

try:
    cache_file = open(U_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    U_CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    U_CACHE_DICTION = {}

### Twitter

T_CACHE_FNAME = "twitter_cache.json"

try:
    cache_file=open(T_CACHE_FNAME,"r")
    cache_contents=cache_file.read()
    T_CACHE_DICTION=json.loads(cache_contents)
    cache_file.close()
except:
    T_CACHE_DICTION = {}

### News API 

N_CACHE_FNAME = 'news_api_cache.json'

try:
    cache_file = open(N_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    N_CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    N_CACHE_DICTION = {}


#############
#############
##### FETCH DATA
#############
#############

##########################
##########################
################## FETCH DATA: sotu 
##########################
##########################

def u_get_unique_key(url):
    return url

def u_make_request_using_cache(url):
    unique_ident = u_get_unique_key(url)
    global header
    ## first, look in the cache to see if we already have this data
    if unique_ident in U_CACHE_DICTION:
        print("Getting cached data from SOTU...")
        return U_CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data from SOTU...")
        # Make the request and cache the new data
        baseurl = 'https://www.whitehouse.gov/briefings-statements/president-donald-j-trumps-state-union-address/'
        complete_url = baseurl
        resp = requests.get(complete_url)
        U_CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(U_CACHE_DICTION)
        fw = open(U_CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return U_CACHE_DICTION[unique_ident]

def scrape_union():
    print("starting to get data from State of the Union")
    baseurl = 'https://www.whitehouse.gov/briefings-statements/president-donald-j-trumps-state-union-address/'
    complete_url = baseurl
    page_text = u_make_request_using_cache(complete_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    content = page_soup.find(class_='page-content')
    paras = content.find_all('p')

    para_list = []
    for p in paras:
        para_list.append(p.text)
    return para_list

##########################
##########################
################## FETCH DATA: Twitter 
##########################
##########################

def get_tweets(username, num_tweets):
    print("Starting to get tweets")
    protected_url = 'https://api.twitter.com/1.1/account/settings.json'
    python_obj = []
    oauth = OAuth1Session(client_key,
                              client_secret=client_secret,
                              resource_owner_key=resource_owner_key,
                              resource_owner_secret=resource_owner_secret)
    protected_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    params={'screen_name':username, 'count': num_tweets}
    python_obj = t_make_request_using_cache(protected_url, params)
    return python_obj

def t_params_unique_combination(protected_url, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return protected_url + "_".join(res)

def t_make_request_using_cache(protected_url, params):
    unique_ident = t_params_unique_combination(protected_url,params)
    print("Making request using cache")
    if unique_ident in T_CACHE_DICTION:
        print("Getting cached data...")
        python_obj = T_CACHE_DICTION[unique_ident]
        return python_obj
    else:
        print("Making a request for new data...")
        protected_url = 'https://api.twitter.com/1.1/account/settings.json'
        oauth = OAuth1Session(client_key,
                                  client_secret=client_secret,
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret)

        protected_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {'screen_name': username, 'count': num_tweets, 'tweet_mode': 'extended'} # need to add counts
        resp = oauth.get(protected_url, params=params)
        T_CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(T_CACHE_DICTION)
        fw = open(T_CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        python_obj = T_CACHE_DICTION[unique_ident]
        print("Getting the python obj")
        return python_obj

##########################
##########################
################## FETCH DATA: News API 
##########################
##########################

def n_params_unique_combination(n_baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return n_baseurl + "_".join(res)

def n_make_request_using_cache(n_baseurl, params):
    unique_ident = n_params_unique_combination(n_baseurl,params)
    if unique_ident in N_CACHE_DICTION:
        print("Getting cached data from News API...")
        return N_CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data from News API...")
        resp = requests.get(n_baseurl, params)
        N_CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(N_CACHE_DICTION)
        fw = open(N_CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        #print(N_CACHE_DICTION[unique_ident])
        return N_CACHE_DICTION[unique_ident]

def get_stories():
    print("starting to get stories from News API")
    #global n_baseurl
    n_baseurl = 'https://newsapi.org/v2/everything?'
    params_diction = {}
    params_diction["apiKey"] = news_key
    params_diction['sources'] = "fox-news"
    params_diction['pageSize'] = 100
    return n_make_request_using_cache(n_baseurl, params_diction)

#############
#############
##### CREATE DATABASES
#############
#############

##########################
##########################
################## CREATE DATABASES: Empath 
##########################
##########################

def em_create_db():
    print("Creating emotions table.")
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Emotions'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Emotions'
        ('ID' INTEGER PRIMARY KEY AUTOINCREMENT,
        'tweets_id' INTEGER NOT NULL,
        'sotu_id' INTEGER NOT NULL, 
        'news_id' INTEGER NOT NULL,
        'source' TEXT NOT NULL,
        'positive_emotion' INTEGER NOT NULL, 
        'contentment' INTEGER NOT NULL,
        'negative_emotion' INTEGER NOT NULL,
        'power' INTEGER NOT NULL,
        'anger' INTEGER NOT NULL,
        'emotional' INTEGER NOT NULL,
        'sadness' INTEGER NOT NULL, 
        'warmth' INTEGER NOT NULL,
        'disgust' INTEGER NOT NULL,
        'dominant_personality' INTEGER NOT NULL,
        'violence' INTEGER NOT NULL,
        'healing' INTEGER NOT NULL,
        'ridicule' INTEGER NOT NULL,
        'weakness' INTEGER NOT NULL,
        'envy' INTEGER NOT NULL,
        'cheerfulness' INTEGER NOT NULL,
        'hate' INTEGER NOT NULL
        );
        '''
    cur.execute(statement)
    conn.commit()

##########################
##########################
################## CREATE DATABASES: Union 
##########################
##########################


def u_create_db():
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS 'sotu'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'sotu'
        ('ID' INTEGER PRIMARY KEY AUTOINCREMENT,
        'text' TEXT NOT NULL
        );
        '''
    cur.execute(statement)
    conn.commit()

def u_pop_db(para_list): 
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for p in para_list:
        insertion = (None, p)
        statement = '''
            INSERT INTO "sotu"
            VALUES (?, ?)
            '''
        cur.execute(statement, insertion)
        conn.commit()

def u_analyze_emotion():
    print("Analyzing emotions from SOTU")
    global CATS, CATS_DICT
    lexicon = Empath()
    descrip_list = []
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = 'SELECT text from sotu'
    cur.execute(statement)
    for row in cur: 
        descrip_list.append(row[0])
    
    ### entire corpus
    str1 = ''.join(descrip_list)
    u_empath_dict = lexicon.analyze(str1, categories=CATS, normalize=True)
    u_empath_dict_new = {}
    for key in u_empath_dict:
        #print (key, 'corresponds to', u_empath_dict[key]*1000)
        u_empath_dict_new[key] = u_empath_dict[key]*1000

    ## Row by Row: 
    counter = 0
    for row in descrip_list: 
        u_row_empath_dict = lexicon.analyze(row, categories=CATS, normalize=True)
        u_row_empath_dict_new = {}
        for key in u_row_empath_dict:
            u_row_empath_dict_new[key] = u_row_empath_dict[key]*1000
        counter +=1
        vals_list = list(u_row_empath_dict_new.values())
        vals_list.insert(0, None)
        vals_list.insert(1, 999)
        vals_list.insert(2, counter)
        vals_list.insert(3, 999)
        vals_list.insert(4, "sotu")
        insertion = tuple(vals_list)
        statement = ''' 
            INSERT INTO "Emotions"
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        cur.execute(statement, insertion)
        conn.commit()

    return u_empath_dict_new

##########################
##########################
################## CREATE DATABASES: Twitter 
##########################
##########################


def t_create_db():
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Tweets'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
    CREATE TABLE 'Tweets'
    ('ID' INTEGER PRIMARY KEY AUTOINCREMENT,
    'text' TEXT NOT NULL,
    'retweet_count' INTEGER NOT NULL,
    'fav_count' INTEGER NOT NULL, 
    'tweet_id_from_twitter' INTEGER NOT NULL, 
    'created_at' TEXT NOT NULL
    );
    '''
    cur.execute(statement)
    conn.commit()

def t_pop_db():
    #print("Creating Twitter database")
    file = open('twitter_cache.json', encoding="utf8")
    file_str = file.read()
    file.close()
    file_dic = json.loads(file_str)
    data = list(file_dic.values())
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    tweet_obj_list = []
    for alist in data:
    #for alist in data:
        #print(alist)
        for adict in alist:
            #print(adict)
            #print(type(adict))
            atweet = Tweet(adict["full_text"], adict["retweet_count"], adict["favorite_count"], adict["id"], adict["created_at"])
            tweet_obj_list.append(atweet)
        for atweet in tweet_obj_list:
            insertion = (None, atweet.full_text, atweet.retweet_count, atweet.favorite_count, atweet.id, atweet.created_at)
            statement = '''
                INSERT INTO "Tweets"
                VALUES (?, ?, ?, ?, ?, ?)
                '''
            cur.execute(statement, insertion)
            conn.commit()
            #conn.close()
    return tweet_obj_list

def t_analyze_emotion():
    print("Analyzing emotions from Twitter")
    global CATS, CATS_DICT
    lexicon = Empath()
    descrip_list = []
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = 'SELECT text from Tweets'
    cur.execute(statement)
    for row in cur: 
        descrip_list.append(row[0])
    #print(len(descrip_list))
     ### entire corpus
    str1 = ''.join(descrip_list)
    t_empath_dict = lexicon.analyze(str1, categories=CATS, normalize=True)
    t_empath_dict_new = {}
    for key in t_empath_dict:
        #print (key, 'corresponds to', t_empath_dict[key]*1000)
        t_empath_dict_new[key] = t_empath_dict[key]*1000

    ## Row by Row: 
    counter = 0
    for row in descrip_list: 
        t_row_empath_dict = lexicon.analyze(row, categories=CATS, normalize=True)
        #print(len((list(u_row_empath_dict.keys())))) # This is 17 long 
        t_row_empath_dict_new = {}
        for key in t_row_empath_dict:
            t_row_empath_dict_new[key] = t_row_empath_dict[key]*1000
        #print(len((list(u_row_empath_dict_new.keys())))) # This is 17 long
        counter +=1
        vals_list = list(t_row_empath_dict_new.values())
        vals_list.insert(0, None)
        vals_list.insert(1, counter)
        vals_list.insert(2, 999)
        vals_list.insert(3, 999)
        vals_list.insert(4, "twitter")
        insertion = tuple(vals_list)
        statement = ''' 
            INSERT INTO "Emotions"
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        cur.execute(statement, insertion)
        conn.commit()
    return t_empath_dict_new

##########################
##########################
################## CREATE DATABASES: News API
##########################
##########################

def n_create_db():
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'News_API'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
    CREATE TABLE 'News_API'
    ('ID' INTEGER PRIMARY KEY AUTOINCREMENT,
    'title' TEXT NOT NULL,
    'text' TEXT NOT NULL,
    'url' TEXT NOT NULL
    );
    '''
    cur.execute(statement)
    conn.commit()

def n_pop_db():
    file = open('news_api_cache.json', encoding="utf8")
    file_str = file.read()
    file_dic = json.loads(file_str)
    data = list(file_dic.values())
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for adict in data:
        #print(type(adict), "Type of adict, should be a dictionary")
        #print(alist)
        #print("here's the dict\n\n\n")
        #print(adict)
        lst = adict["articles"]  # This should be a list of dictionaries, one for each article
        #print(type(lst))
        for adict in lst:
            insertion = (None, adict["title"], adict["description"], adict["url"])
            statement = '''
                INSERT INTO "News_API"
                VALUES (?, ?, ?, ?)
                '''
            cur.execute(statement, insertion)
            conn.commit()

def n_analyze_emotion():
    print("Analyzing emotions from News API")
    global CATS, CATS_DICT
    lexicon = Empath()
    descrip_list = []
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = 'SELECT text from news_api'
    cur.execute(statement)
    for row in cur: 
        descrip_list.append(row[0])
    
     ### entire corpus
    str1 = ''.join(descrip_list)
    print(str1)
    n_empath_dict = lexicon.analyze(str1, categories=CATS, normalize=True)
    n_empath_dict_new = {}
    for key in n_empath_dict:
        n_empath_dict_new[key] = n_empath_dict[key]*1000

    ## Row by Row: 
    counter = 0
    for row in descrip_list: 
        n_row_empath_dict = lexicon.analyze(row, categories=CATS, normalize=True)
        #print(len((list(u_row_empath_dict.keys())))) # This is 17 long 
        n_row_empath_dict_new = {}
        for key in n_row_empath_dict:
            n_row_empath_dict_new[key] = n_row_empath_dict[key]*1000
        #print(len((list(u_row_empath_dict_new.keys())))) # This is 17 long
        counter +=1
        vals_list = list(n_row_empath_dict_new.values())
        vals_list.insert(0, None)
        vals_list.insert(1, 999)
        vals_list.insert(2, 999)
        vals_list.insert(3, counter)
        vals_list.insert(4, "news_api")
        insertion = tuple(vals_list)
        DBNAME = 'final.db'
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = ''' 
            INSERT INTO "Emotions"
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        cur.execute(statement, insertion)
        conn.commit()

    return n_empath_dict_new


#############
#############
##### CREATE VISUALIZATIONS
#############
#############

##########################
##########################
################## CREATE VISUALIZATIONS: compare_sources
##########################
##########################

def compare_sources(given_emotion): 
    global SOURCES
   
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    vals = []

    for source in SOURCES:
        params = (source, )
        statement_beg = "SELECT AVG(" + given_emotion + ")"
        statement_end =  " FROM Emotions WHERE Source = ?"
        statement = statement_beg + statement_end
        cur.execute(statement, params)
        for row in cur: 
            vals.append(row[0])

    data = [go.Bar(
            x=SOURCES,
            y=vals
    )]
    py.plot(data, filename='bar_chart')

##########################
##########################
################## CREATE VISUALIZATIONS: twitter_faves_emotion
##########################
##########################

def t_plot_emotion_by_favs(given_emotion): 
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement_beg = "SELECT " + given_emotion + ", " + "fav_count "
    statement_end =  "FROM Emotions JOIN Tweets on Tweets.ID = Emotions.tweets_id"
    statement = statement_beg + statement_end
    cur.execute(statement)
    emotion_list = []
    fav_list = []
    for row in cur:
        emotion_list.append(row[0])
        fav_list.append(row[1])

    trace = go.Scatter(
            x=emotion_list,
            y=fav_list, 
            mode = 'markers'
    )

    data = [trace]
    py.plot(data, filename='basic-scatter')


##########################
##########################
################## CREATE VISUALIZATIONS: twitter_time_emotion
##########################
##########################

def t_emotion_over_time(given_emotion):
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement_beg = "SELECT " + given_emotion + ", " + "created_at "
    statement_end =  "FROM Emotions JOIN Tweets on Tweets.ID = Emotions.tweets_id"
    statement = statement_beg + statement_end
    cur.execute(statement)
    created_at_list = []
    emotion_list = []
    for row in cur:
        created_at_list.append(row[1])
        emotion_list.append(row[0])
    trace = go.Scatter(
            x=created_at_list,
            y=emotion_list, 
            mode = 'lines+markers'
    )

    data = [trace]
    py.plot(data, filename='basic-scatter')

##########################
##########################
################## CREATE VISUALIZATIONS: view_all_from_source
##########################
##########################

def view_all_from_source(given_source):
    global CATS
    print("Starting up...")
    if given_source == "twitter":
        print("Source = Twitter")
        t_empath_dict_new = t_analyze_emotion()
        data = [go.Bar(
                x=CATS,
                y=list(t_empath_dict_new.values())
        )]
        py.plot(data, filename='source-bar')
    elif given_source == "news_api": 
        print("Source = News API")
        n_empath_dict_new = n_analyze_emotion()
        data = [go.Bar(
                x=CATS,
                y=list(n_empath_dict_new.values())
        )]
        py.plot(data, filename='source-bar')
    elif given_source == "sotu": 
        print("Source = State of the Union")
        u_empath_dict_new = u_analyze_emotion()
        data = [go.Bar(
                x=CATS,
                y=list(u_empath_dict_new.values())
        )]
        py.plot(data, filename='source-bar')
    else: 
        print("Sorry, that source won't work.")


#############
#############
##### RUN MAINS
#############
#############

def pre_process():
    print("Pre-processing data...")

    print("Pre-processing data for SOTU")
    para_list = scrape_union()
    u_create_db()
    u_pop_db(para_list)

    #twitter
    print("Pre-processing data for Twitter")
    get_tweets(username, num_tweets)
    t_create_db()
    t_pop_db()

    #news_API
    print("Pre-processing data for News API")
    get_stories()
    n_create_db()
    n_pop_db()

def prep_empath():
    print("Prepping empath")
    em_create_db()
    u_analyze_emotion()
    t_analyze_emotion()
    n_analyze_emotion()

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive():
    print("Starting up the interactive function.")
    help_text = load_help_text()
    global CATS, SOURCES
    user_inp = "starting value"
    while user_inp != "exit":
        user_inp = input("Please enter a command: ")
        user_str = user_inp.split()
        command = user_str[0]
        try:
            detail = user_str[1]
        except:
            pass
        if command == "compare_sources":
            if detail in CATS:
                print("Great. Creating a bar chart showing how different sources use that emotion.")
                compare_sources(detail)
            else: 
                print("Sorry, we don't have data for that emotion. Type help to see the emotions we do cover.")
            # Detail should be an emotion 

        elif command == "twitter_faves_emotion":
            if detail in CATS:
                print("Great. Creating a scatter plot showing the relationship that emotion and favorites.")
                t_plot_emotion_by_favs(detail)
            else: 
                print("Sorry, we don't have data for that emotion. Type help to see the emotions we do cover.")
             # Detail should be an emotion 
        elif command == "twitter_time_emotion":
            if detail in CATS:
                print("Great. Creating a line plot of Trump's use of that emotion over time.")
                t_emotion_over_time(detail)
            else: 
                print("Sorry, we don't have data for that emotion. Type help to see the emotions we do cover.")

        elif command == "view_all_from_source": 
            if detail in SOURCES: 
                print("Great. Creating a bar chart of how that source uses each emotion.")
                view_all_from_source(detail)
            else: 
                print("Sorry, we don't have data for that source. Type help to see the sources we do cover.")
        elif command == "help":
            print(help_text)

        elif command == "exit":
            print("Goodbye!")
        else: 
            print("Sorry, I don't recognize that command. Type help to see a list of commands.")

#n_analyze_emotion()
# pre_process()
# prep_empath()
interactive()