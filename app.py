import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

from flask import Flask, render_template, redirect, url_for, request
from nltk_depression import greeting,response
import emoji
import pandas as pd


def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())


def get_tweet_sentiment(tweet):
    # analysis = TextBlob(clean_tweet(tweet), analyzer=NaiveBayesAnalyzer())

    # if analysis.sentiment.classification == "pos":
    #     return 'positive'
    # elif analysis.sentiment.classification == "neg":
    #     return 'negative'

    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"


def get_tweets(api, query, c):
    count = int(c)
    tweets = []
    tweets = api.user_timeline(screen_name=query, count=count,
                               tweet_mode='extended')

    # create DataFrame
    m = []
    data = []
    x = []
    for tweet in tweets:
        j = emoji.demojize(tweet.full_text)

        data.append([tweet.user.screen_name, j])
        x.append(j)

    

    po = ne = n = 0 # positive, negative, neutral variable =0
    for text in x:
        blob = TextBlob(text)
        key = text
        if blob.sentiment.polarity > 0:
            text_sentiment = "positive"
            po += 1

        elif blob.sentiment.polarity == 0:
            text_sentiment = "neutral"
            ne += 1
        else:
            text_sentiment = "negative"
            n += 1
        sentiment = text_sentiment
        m.append({"text": key, "sentiment": sentiment})
    return m  # returning nested dictionary



app = Flask(__name__)
app.static_folder = 'static'


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/psychometric')
def qna():
  return render_template("qna.html")


@app.route('/wellbeing')
def updates():
  return render_template("updates.html")

#Chatbot using NLTK
#Reading in the corpus
xls = pd.read_excel(r"QNA.xlsx") #use r before absolute file path

xls = xls.applymap(str)
@app.route("/chat")
def index():
	return render_template("index1.html",template_folder='templates')
@app.route("/get", methods=["GET","POST"])
def chatbot_response():
    msg = request.form["msg"]
    msg=msg.lower()
    if(msg!='bye'):
        if(msg=='thanks' or msg=='thank you' ):
            
            return "ROBO: You are welcome.."
        else:
            if(greeting(msg)!=None):
                return "ROBO: "+greeting(msg)
            else:
                try:
                    xls.drop(xls.tail(1).index, inplace=True)
        
                    return "ROBO: "+response(msg)
                except:
                    return "I don't understand"
                    
                
    else:
        
        return "ROBO: Bye! take care.."




# ******Phrase level sentiment analysis
@app.route("/predict", methods=['POST', 'GET'])
def pred():
    if request.method == 'POST':
        query = request.form['query']
        count = request.form['num']
        fetched_tweets = get_tweets(api, query, count)
        return render_template('result.html', result=fetched_tweets)


# fetched_tweets


# *******Sentence level sentiment analysis
@app.route("/predict1", methods=['POST', 'GET'])
def pred1():
    if request.method == 'POST':
        text = request.form['txt']
        blob = TextBlob(text)
        if blob.sentiment.polarity > 0:
            text_sentiment = "positive"
        elif blob.sentiment.polarity == 0:
            text_sentiment = "neutral"
        else:
            text_sentiment = "negative"
        return render_template('result1.html', msg=text, result=text_sentiment)


if __name__ == '__main__':

    consumerKey = "kyRQF7cFHe4qgecZG0knT26xM"
    consumerSecret = "ksQcnURKquWNOeiq1NBUmRvF1Q3mntwK5GS1Z8idP55s9R5F9j"
    accessToken = "1574783882091642880-xDPEEHEYJp1I7PVuoVdYSJjqdlh2Ct"
    accessTokenSecret = "sKCjx2Q3iGlIg1FctYGbLdpy5jgDGkpIbIyNwgruhuMQo"

    try:
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth)
    except:
        print("Error: Authentication Failed")

    app.debug = True
    app.run(host='localhost')
