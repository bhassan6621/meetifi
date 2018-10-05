
add_meetup_query = """
INSERT INTO meetups(user, name, address, meetup_date, meetup_time, invites)
VALUES (?, ?, ?, ?, ?, ?)"""

get_all_meetups_query = """
SELECT * FROM meetups
WHERE user = ? OR invites LIKE ?"""

get_meetup_query = """
SELECT * FROM meetups
WHERE name = ?"""

add_update_query = """
INSERT INTO updates(meetup_name, user, distance, time)
VALUES (?, ?, ?, ?)"""

get_all_updates_query = """
SELECT * FROM updates
WHERE meetup_name = ?"""



geocoder_url = "https://geocoder.api.here.com/6.2/geocode.json?app_id=uhIYrWPnuNlLk1tUWsfd&app_code=4DxLDAVJdKZy6uLvWof3jA&searchtext="

weather_url = "https://weather.api.here.com/weather/1.0/report.json?app_id=uhIYrWPnuNlLk1tUWsfd&app_code=4DxLDAVJdKZy6uLvWof3jA&product=forecast_hourly&"
routing_url = """https://route.api.here.com/routing/7.2/calculateroute.json?app_id=uhIYrWPnuNlLk1tUWsfd&app_code=4DxLDAVJdKZy6uLvWof3jA&waypoint0=geo!%s&waypoint1=geo!%s&departure=now&mode=fastest;publicTransport&combineChange=true"""
places_url = """
https://places.cit.api.here.com/places/v1/discover/search?app_id=uhIYrWPnuNlLk1tUWsfd&app_code=4DxLDAVJdKZy6uLvWof3jA&at=%s&q=%s"""
