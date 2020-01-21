
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import csv
import io
import pprint as pp
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


def tweet_scroller(url):

    browser.get(url)

    #define initial page height for 'while' loop
    lastHeight = browser.execute_script("return document.body.scrollHeight")

    count = 0
    while count<2:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #define how many seconds to wait while dynamic page content loads
        time.sleep(3)
        newHeight = browser.execute_script("return document.body.scrollHeight")

        if newHeight == lastHeight:
            break
        else:
            lastHeight = newHeight

        count+=1
        print(count)

    html = browser.page_source
    return html

def get_html(url):

    browser.get(url)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    html = browser.page_source
    return html


def scrape_tweets(name, start_date, end_date):
    url = 'https://twitter.com/search?q=' + name + '%20since%3A'+start_date+'%20until%3A'+end_date+'&src=typd'
    soup = BeautifulSoup(tweet_scroller(url), "html.parser")

    list = []
    for i in soup.find_all('li', {"data-item-type":"tweet"}):

            tweet_link = 'https://twitter.com/' + i.find('div', class_="tweet").attrs['data-screen-name'] + '/status/' + i.find('div', class_="tweet").attrs['data-tweet-id']

            date = (i.small.a['title'] if i.small is not None else "")
            user = (i.find('span', {'class':"username u-dir u-textTruncate"}).get_text() if i.find('span', {'class':"username js-action-profile-name"}) is not None else "")
            tweets = i.find("p", class_="tweet-text").strings
            tweet_text = "".join(tweets)
            user_image = i.find('img', class_="avatar").attrs['src']
            try:
                image = i.find('div', class_="AdaptiveMedia-singlePhoto")
                image = image.find('img', {"aria-label-part":""}).attrs['src']
            except AttributeError:
                image=""

            try:
                name = (i.find_all("strong", class_="fullname")[0].string).strip()
            except AttributeError:
                name = "Anonymous"

            try:
                user_handle = ''.join(i.find("span", class_="username").strings)

            except AttributeError:
                user_handle = "Anonymous"

            link = i.find("span", class_="js-display-url")
            if link is not None:
                link = "".join(link.strings)


            tweet = {
                'date' : date,
                'user_image': user_image,
                'tweet_text' : tweet_text,
                'name' : name,
                'user_handle' : user_handle,
                'image': image,
                'tweet_link': tweet_link,
                'link': link,
            }

            list.append(tweet)

    return(list)

def get_show_info(name):
    show_url = 'https://next-episode.net/' + name
    soup = BeautifulSoup(get_html(show_url), "html.parser")

    find_time = re.compile(r'\d{1,2}:\d{2} [APap][mM]')
    find_date = re.compile(r'\w{3} \w{3} \d{1,2}, \d{4}')

    show_info = soup.find("div", id="middle_section")
    show_info = "".join(show_info.strings)

    #air_time = soup.find_all("div", class_="sub_main")
    air_time = find_time.findall(show_info)

    if(air_time !=[]):
        air_time = air_time[0]


    #extracting the image
    image = soup.find('img', id='big_image').attrs['src']

    #extracting the previous episode's date
    prev = soup.find('div', id="previous_episode")

    episode_name = "".join(prev.find('div', class_="sub_main").strings)
    if prev==None:
        prev_date =""

    else:
        prev_date = find_date.findall("".join(prev.strings))[0]

    seasons = soup.find_all("a", class_="season_href")
    season_list =[]
    for i in seasons:
        season = {
            'name': "".join(i.find('span', {"itemprop":"name"}).strings),
            'link': i.attrs['href'].split("/")[-1]
        }
        season_list.append(season)

    show = {
        'air_time': air_time,
        'image': image,
        'prev_date': prev_date,
        'name': name,
        'episode_name': episode_name,
        'seasons': season_list,
    }


    return(show)

def get_season_info(show, season):

    url = 'https://next-episode.net/' + show + "/" + season
    soup = BeautifulSoup(get_html(url), "html.parser")

    all_episodes = soup.find_all('tr', {'itemprop':"episode"})
    print(all_episodes)

    list=[]
    for ep in all_episodes:
        episode = {
            'date': "".join(ep.find('span', {'itemprop': 'datePublished'}).strings),
            'episode_number': "".join(ep.find('td', {'itemprop': 'episodeNumber'}).strings),
            'name': "".join(ep.find('a').strings)
        }
        list.append(episode)

    return(list)



def search_show_options(name):


    name = (name.strip()).replace(" ", "+")
    url = 'https://next-episode.net/site-search-'+name+'.html'
    soup = BeautifulSoup(get_html(url), "html.parser")
    list = []
    for i in soup.find_all('div', class_='list_item'):
        name = "".join(i.find('span', class_='headlinehref').strings)
        image = (i.find('img', class_='item_image').attrs['src'])
        link = i.find('span', class_='headlinehref').find('a').attrs['href']
        summary = "".join(i.find('div', class_='summary').strings)
        info = "".join(i.find('span', class_='channel_name').strings)

        show = {
            'name': name,
            'image': image,
            'link': link[1:],
            'summary': summary,
            'info': info,
        }
        list.append(show)

    return list
