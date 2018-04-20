OVERVIEW 

This program allows you to see 4 different visualizations related to emotions in the media.

DATA SOURCES USED 

1. State of the Union speech. I used BeautifulSoup to scrape the most recent State of the Union speech. More info here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
2. Twitter. I used Twitter's "Accounts" endpoint API to get Trump's 100 most recent Tweets. https://developer.twitter.com/
3. News API. I used "Everything" endpoint from News API to pull snippets from recent Fox News articles. More info available here: https://newsapi.org/docs/

KEY INFO TO RUN THE PROGRAM 

This program uses Plotly for visualizations. More info available here: https://plot.ly/python/getting-started/

This program uses Empath for emotion analysis. More info available here: https://github.com/Ejhfast/empath-client

CODE STRUCTURE 

This program has three main functions:
1. pre_process(). This function creates a database. It also pulls data from the three sources and stores it in 3 different tables in the DB. 
2. prep_empath(). This function uses the Empath package to analyze the emotion contained in each source. It also creates a table in the DB to store this information and populates it. 
3. interactive(). This function allows the user to see 4 different Plotly visualizations related to SQL pulls 

Data and Storage: 

The vast majority of the data is stored in a SQLite database.  

USER GUIDE 

\\ Here are the emotions we support:

- positive_emotion
- contentment
- negative_emotion
- power
- anger
- emotional
- sadness
- warmth
- disgust
- dominant_personality
- violence  
- healing
- ridicule  
- weakness  
- envy  
- cheerfulness
- hate

\\ Here are the media sources we support:

- news_api (uses articles from Fox News)
- sotu (uses text from President Trump's most recent State of the Union speech)
- twitter (uses text from President Trump's latest tweets)

\\ Here are the commands for  each visualization:

- compare_sources <emotion name>
    Shows the average score of a given emotion across the 3 different sources
- twitter_faves_emotion <emotion name>
    Shows correlation between the number of "favorites" on a tweet and how much
    it uses a given emotion
- twitter_time_emotion <emotion name>
    Shows how presence of a given emotion in Trump's tweets changes over time
- view_all_from_source <source>
    Shows the average use of each of the 16 emotions in a given source

PACKAGES REQUIRED 

Refer to requirements.txt 
