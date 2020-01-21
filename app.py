from flask import Flask, flash, redirect, render_template, request, session, abort
from tweets import search_show_options, get_show_info, scrape_tweets, get_season_info
import datetime


app = Flask(__name__)    # create an app instance

months = {
    'Jan' : '1',
    'Feb' : '2',
    'Mar' : '3',
    'Apr' : '4',
    'May' : '5',
    'Jun' : '6',
    'Jul' : '7',
    'Aug' : '8',
    'Sep' : '9',
    'Oct' : '10',
    'Nov' : '11',
    'Dec' : '12',
 }


@app.route("/")                   # at the end point /
def index():                      # call method hello

    return render_template('home.html')


@app.route("/<show_name>/<date>")
def get_tweets(show_name, date):
    print(date)
    start_date = convert_date(date)
    end_date = addDays(start_date ,1)

    start_date_str = '{:%Y-%m-%d}'.format(start_date)
    end_date_str = '{:%Y-%m-%d}'.format(end_date)

    result =  {
        'list' : scrape_tweets(show_name, start_date_str, end_date_str),

        }
    return render_template('tweets.html', result=result, date=date, tweet_query=show_name, show_name=show_name)

def convert_date(datestring):
    date = datestring.replace(',', '')
    date = date.split()
    return datetime.datetime(int(date[3]),int(months.get(date[1])),int(date[2]))


def addDays(dateobj, numdays):
    return dateobj + datetime.timedelta(days=numdays)

@app.route("/show/<name>/<season>")
def get_seasons_episodes(name, season):


    print("SHOW ROUTE2")
    result =  {
        'episodes': get_season_info(name, season)
        }
    return render_template('episodes.html', result=result, name=name, season=season.replace("-"," ").title())

@app.route("/show/<name>")
def show(name):
    print("SHOW ROUTE")
    result =  {
        'show_info': get_show_info(name)
        }
    return render_template('show.html', result=result)



@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        #result = request.form['search']
        result = {
            'list': search_show_options(request.form['search'])
            }
        return render_template("search_results.html", result=result)

@app.route('/<show_name>/<date>', methods=['POST', 'GET'])
def tweetsearch(show_name, date):
    if request.method == 'POST':
        # ogdate = request.form['date']
        # date = ogdate.replace("-", " ")

        tweet_query=request.form['tweet-search']
        # #result = request.form['search']

        start_date = convert_date(date)
        end_date = addDays(start_date ,1)

        start_date_str = '{:%Y-%m-%d}'.format(start_date)
        end_date_str = '{:%Y-%m-%d}'.format(end_date)
        result = {
            'list': scrape_tweets(tweet_query, start_date_str, end_date_str),
            }
        return render_template('tweets.html', result=result, date=date, tweet_query=tweet_query , show_name=show_name)


if __name__ == "__main__":
    app.run()                   # run the flask app
