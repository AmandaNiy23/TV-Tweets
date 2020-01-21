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


@app.route("/<show_name>/<episode_name>/<date>")
def get_tweets(show_name, episode_name, date):

    date = date.replace(',', '')
    date = date.split()
    start_date = datetime.datetime(int(date[3]),int(months.get(date[1])),int(date[2]))
    end_date = start_date + datetime.timedelta(days=1)

    start_date_str = '{:%Y-%m-%d}'.format(start_date)
    end_date_str = '{:%Y-%m-%d}'.format(end_date)

    result =  {
        'list' : scrape_tweets(show_name, start_date_str, end_date_str),

        }
    return render_template('tweets.html', result=result, show_name=show_name.replace("-", " ").title(), episode_name=episode_name)

@app.route("/show/<name>/<season>")
def get_seasons_episodes(name, season):


    print("SHOW ROUTE2")
    result =  {
        'episodes': get_season_info(name, season)
        }
    return render_template('episodes.html', result=result, name=name)

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

if __name__ == "__main__":
    app.run()                   # run the flask app
