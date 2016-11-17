r"""
nomnom is a command line tool to browse zomato straight from your terminal

Usage:
nomnom surprise
nomnom configure
nomnom menu <restaurant-id>
nomnom (-h | --help)
nomnom
Options:
  -h --help     Show this screen.
  --version     Show version.

"""

from docopt import docopt
import requests
import random
import json
from tabulate import tabulate

try:
    config = json.loads(open("./config.json", "r").read())
except:
    print("Failed to find configuration file, run configure()")

__version__ = "0.0.2"
headers = {'Accept' : 'application/json', 'user_key': config['api_key'], 'User-Agent': 'curl/7.35.0'}

def configure():
    configure_file = open("config.json", "w")
    api_key = input("Enter API key: ") or "9822cee7e33b3418662df7f5703b9624"
    budget = input("Enter budget: ") or "100"
    lat = input("Enter your latitude: ") or "18.44"
    lon = input("Enter your longitude: ") or "73.89"
    headers = {'Accept' : 'application/json', 'user_key': api_key, 'User-Agent': 'curl/7.35.0'}
    url = "https://developers.zomato.com/api/v2.1/cities?lat={0}&lon={1}".format(lat, lon)
    city_id = ""
    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                city_id = data['location_suggestions'][0]['id']
        else:
            print("Error requesting, response code:"  + str(response.status_code))
    except:
        print("Error requesting")
        
    if city_id:
        configuration_settings = {"api_key": api_key, "budget": budget, "latitude": lat, "longitude": lon}
        configure_file.write(json.dumps(configuration_settings))
    else:
        print("Could not retrieve city id for specified coordinates")
            
def surprise():
    url = 'https://developers.zomato.com/api/v2.1/geocode?lat={0}&lon={1}'.format(config['latitude'],config['longitude'])
    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            data = response.json()
            restaurants = data['nearby_restaurants']
            res_len = len(restaurants)
            i = 0
            table = []
            while(i < res_len):
                cur_restaurant = restaurants[i]['restaurant']
                table.append([ cur_restaurant['id'] , cur_restaurant["name"], cur_restaurant["currency"] + " " + str(float(cur_restaurant['average_cost_for_two'])/2), cur_restaurant["user_rating"]["aggregate_rating"], cur_restaurant["location"]["address"][:50] ])
                i = i + 1
            print(tabulate(table, headers=["ID", "Name", "Budget", "Rating", "Location"]))
        else:
            print("Error requesting, response code:"  + str(response.status_code))
    except:
        print("Error requesting")

def menu(restaurant_id):
    import re
    import urllib.request
    url = 'https://developers.zomato.com/api/v2.1/restaurant?res_id={0}'.format(restaurant_id)
    print(url)
    headers = {'Accept' : 'application/json', 'user_key': config['api_key'], 'User-Agent': 'curl/7.35.0'}
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        data = response.json()
        print(data['menu_url'])
        html_source = requests.get(data['menu_url'])
        '''
        #html_source = open("file.txt", "r", encoding="utf8").read()
        x = re.search('zomato\.menuPage(.+}]);', html_source)
        matched_text = x.group(0)
        matched_text = matched_text[matched_text.find("["): -1]
        print(matched_text)
        menu_items = json.loads(matched_text)
        i = 0
        while(i < len(menu_items)):
            cur_menu_url = menu_items[i]['url']
            print(cur_menu_url)
            urllib.request.urlretrieve(cur_menu_url, str(i) + ".jpg")
            i += 1
        '''
    else:
        print("Error requesting, response code:"  + str(response.status_code))

def main():
    arguments = docopt(__doc__, version = __version__)
    if arguments['configure']:
        configure()
    elif arguments['surprise']:
        surprise()
    elif arguments['menu']:
        menu(arguments['<restaurant-id>'])
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
