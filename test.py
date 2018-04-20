import unittest
from main import *


class TestDatabase(unittest.TestCase):

    def test_emotions_sotu(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT round(avg(Anger)) FROM Emotions
            WHERE source = "sotu"
        '''
        cur.execute(sql)
        result_list = []
        for row in cur: 
            result_list.append(row)
        self.assertEqual((1.0,), result_list[0])
        conn.close()

    def test_emotions_twitter(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT round(avg(positive_emotion)) FROM Emotions
            WHERE source = "twitter"
        '''
        cur.execute(sql)
        result_list = []
        for row in cur: 
            result_list.append(row)
        self.assertEqual((8.0,), result_list[0])
        conn.close()

    def test_emotions_news(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT round(avg(violence)) FROM Emotions
            WHERE source = "news_api"
        '''
        cur.execute(sql)
        result_list = []
        for row in cur: 
            result_list.append(row)
        self.assertEqual((5.0,), result_list[0])
        conn.close()

    def test_join_sotu(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT sotu.text
            FROM sotu
                JOIN Emotions
                ON Emotions.sotu_id = sotu.ID
            WHERE source = "sotu"
        '''
        cur.execute(sql)
        result_list = []
        for row in cur: 
            result_list.append(row)
        self.assertIn(('Thank you, and God bless America.',), result_list)
        conn.close()

    def test_join_tweet(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT retweet_count
            FROM Tweets
                JOIN Emotions
                ON Emotions.tweets_id = Tweets.ID
            WHERE source = "twitter"
        '''
        cur.execute(sql)
        result_list = []
        for row in cur: 
            result_list.append(row)
        self.assertIn((12919,), result_list)
        conn.close()


class TestTweetSearch(unittest.TestCase):

    def atweet_is_in_tweet_list(self, favorite_count, created_at, tweet_obj_list):
        for atweet in tweet_obj_list:
            if favorite_count == atweet.favorite_count and created_at == atweet.created_at:
                return True
        return False

    def get_atweet_from_list(self, favorite_count, tweet_obj_list):
        for atweet in tweet_obj_list:
            if favorite_count == atweet.favorite_count:
                return atweet
        return None

    def setUp(self):
        self.tweet_obj_list = t_pop_db()
        self.t59494 = self.get_atweet_from_list(59494, self.tweet_obj_list)
        self.t65996 = self.get_atweet_from_list(65996, self.tweet_obj_list)

    def test_basic_search(self):
        self.assertEqual(len(self.tweet_obj_list), 100)
        self.assertTrue(self.atweet_is_in_tweet_list(59494, 'Fri Apr 20 10:57:12 +0000 2018', self.tweet_obj_list))   
        self.assertTrue(self.atweet_is_in_tweet_list(65996, 'Fri Apr 20 10:50:38 +0000 2018', self.tweet_obj_list))  

    def test_tweet_class(self):
        c = Tweet("Russia and China are playing the Currency Devaluation game as the U.S. keeps raising interest rates. Not acceptable!", 21294, 95519, 985858100149309441, "Mon Apr 16 12:31:02 +0000 2018")
        self.assertEqual(c.__str__(),"text:Russia and China are playing the Currency Devaluation game as the U.S. keeps raising interest rates. Not acceptable!")

class TestPlotting(unittest.TestCase):

    # we can't test to see if the plots are correct, but we can test that
    # the functions don't return an error!

    def test_show_compare_sources_plot(self):
        try:
            compare_sources('anger')
            compare_sources('warmth')
        except:
            self.fail()

    def test_show_twitter_faves_emotion(self):
        try:
            t_plot_emotion_by_favs('power')
            t_plot_emotion_by_favs('weakness')
        except:
            self.fail()

    def test_show_twitter_time_emotion(self):
        try:
            t_emotion_over_time('emotional')
            t_emotion_over_time('sadness')
        except:
            self.fail()

    def test_view_all_from_source(self):
        try:
            view_all_from_source('news_api')
            view_all_from_source('sotu')
        except:
            self.fail()


unittest.main()