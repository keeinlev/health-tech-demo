import requests
from health.settings import GOOGLE_MAPS_API_KEY as key

nearby_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
find_by_text_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
find_by_id_url = 'https://maps.googleapis.com/maps/api/place/details/json'

def get_nearby(location, t):
    params = { 'location':location, 'type':t, 'radius':'5000', 'key':key }
    r = requests.get(nearby_url, params=params)
    print(r.status_code)
    return r.json()

def geocode(address, postal_code):
    s = address + ', ' + postal_code
    params = { 'address': s, 'key': key }
    r = requests.get(geocode_url, params=params)
    print(r.status_code)
    return r.json()

def find_place_by_text(search_str):
    params = { 'input':search_str, 'inputtype':'textquery', 'fields':'formatted_address,name,place_id', 'key':key }
    r = requests.get(find_by_text_url, params=params)
    print(r.status_code)
    return r.json()

def find_place_by_place_id(pid):
    params = { 'place_id':pid, 'fields':'formatted_address,name', 'key':key }
    r = requests.get(find_by_id_url, params=params)
    print(r.status_code)
    return r.json()