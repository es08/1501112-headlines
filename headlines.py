import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
from urllib.request import urlopen
import urllib.parse

app = Flask(__name__)
app.config.from_object('config')

RSS_FEEDS = {'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
             'CNN': 'http://rss.cnn.com/rss/edition.rss',
             'FOX': 'http://feeds.foxnews.com/foxnews/latest',
             'IOL': 'http://www.iol.co.za/cmlink/1.640'}
             
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id={}"

DEFAULTS = {'publication':'BBC',
            'city': 'Chiang Rai,TH',
            'currency_from':'USD',
            'currency_to':'THB'}

@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    
    # get customized currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
          currency_to=DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)
    return render_template("home.html",
    publication = publication.upper(),
    articles=articles,
    weather=weather, 
    currency_from=currency_from, 
    currency_to=currency_to,    
    rate=rate,
    currencies=sorted(currencies))
    

def get_news(query):
        if not query or query.upper() not in RSS_FEEDS:
                publication = DEFAULTS["publication"]
        else:
                publication = query.upper()
        feed = feedparser.parse(RSS_FEEDS[publication])
        return feed['entries']

def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query,app.config['WEATHER_API'])
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"],"temperature":parsed["main"]["temp"],"city":parsed["name"]
                  }
    return weather

def get_rate(frm, to):
        all_currency = urlopen(CURRENCY_URL.format(app.config['CURRENCY_API'])).read()
        parsed = json.loads(all_currency).get('rates')
        frm_rate = parsed.get(frm.upper())
        to_rate = parsed.get(to.upper())
        return (to_rate / frm_rate, parsed.keys())

if __name__ == "__main__" :
    app.run(port=5000, debug=True)