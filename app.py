from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from queries import *
import datetime
import requests
from urllib.parse import quote
import re

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    user = request.form['username']
    return redirect(url_for('user_home', user=user))
    

@app.route('/home/<user>')
def user_home(user):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(get_all_meetups_query, (user, '%'+user+'%'))
    rows = cur.fetchall()
    upcoming = []
    previous = []
    for r in rows:
        if datetime.datetime.strptime(r['meetup_date'], '%Y-%m-%d') >= datetime.datetime.today():
            upcoming.append(r)
        else:
            previous.append(r)
    
    return render_template('home.html', upcoming = upcoming, previous = previous, user = user)

@app.route('/newmeetup/<user>')
def new_meetup(user):
    
    return render_template('newmeetup.html', user = user)

@app.route('/create', methods=['POST'])
def create():
    user = request.form['user']
    name = request.form['name']
    address = request.form['address']
    meetup_date = request.form['meetup_date']
    meetup_time = request.form['meetup_time']
    invites = request.form['invites'].replace('\r\n', ', ')
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute(add_meetup_query,
                    [user, name, address, meetup_date, meetup_time, invites])
        con.commit()
        
    return user_home(user)

@app.route('/meetup/<user>/<name>', methods=['GET', 'POST'])
def existing_meetup(user, name):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if request.method == 'POST':
        cur.execute(add_update_query, [name, user, request.form['distance'], str(datetime.datetime.time(datetime.datetime.now()))])
        con.commit()
        return redirect(url_for('existing_meetup', user=user, name=name))
    else:
        cur.execute(get_all_updates_query, (name,))
        # this is all the updates
        rows = cur.fetchall()
    
        cur.execute(get_meetup_query, (name,))
        row = cur.fetchall()[0]
        address = row['address']
        date = row['meetup_date']
    
        dest_geo = get_geo(address)
        weathers = get_hourly_weather(dest_geo.split(',')[0],dest_geo.split(',')[1], date)
        position = get_position()
        
        try:
            route = get_route(position, dest_geo)
            start = route['response']['route'][0]['leg'][0]['maneuver']
        except:
            return 'could not find route, please check address'
        distance = route['response']['route'][0]['summary']['distance']
        directions = []
    
        for s in start:
            directions.append(remove_tags(s['instruction']))

        json_restaurants = get_places(dest_geo, 'restaurant')
        restaurants = json_restaurants['results']['items']
    
        return render_template('meetup.html', info = row, weathers = weathers, user = user, directions = directions, restaurants = restaurants, distance = distance, updates = rows)

def get_geo(address):
    r = requests.get(geocoder_url + quote(address)).json()
    lat = str(r['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude'])
    long = str(r['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude'])
    return lat + "," + long

def get_hourly_weather(lat, long, date):
    r = requests.get(weather_url + "latitude=" + lat + "&longitude=" + long).json()
    #return weather_url + "latitude=" + lat + "&longitude=" + long
    #return str(r)
    days = r['hourlyForecasts']['forecastLocation']['forecast']

    weathers = []
    for d in days:
        if date in d['utcTime']:
            weathers.append(d)
    return weathers

def get_position():
    ip = requests.get('http://bot.whatismyipaddress.com/').text
    r = requests.get('http://ip-api.com/json/' + ip).json()
    return str(r['lat']) + ',' + str(r['lon'])

def get_route(cur, des):

    r = requests.get(routing_url % (cur, des))
    return r.json()

def get_places(at, query):
    r = requests.get(places_url % (at, query))
    return r.json()

if __name__ == '__main__':
    app.run(debug=True)
