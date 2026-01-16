
import json,time,math
import requests
from restaurant import CENTER_LNG, PLACES_URL, API_KEY

OUTFILE = "restaurants_dakar.xlsx"
CENTER_LAT =14.776678146680506
CENTER_LONG= -17.321405211578192

RADIUS_M=5000

PLACES_URL="https://maps.googleapis.com/maps/api/place/nearbysearch/json"

API_KEY="AIzaSyCZLwrpH2lfQw4I-1dbNZ2zrnGPX1xTtM8"

def fetch_pages():
    params={
        "location": f"{CENTER_LAT},{CENTER_LONG}",
        "radius": RADIUS_M,
        "type": "restaurant",
        "key": API_KEY,

    }

    r= requests.get(PLACES_URL,params=params)
    return r.json()




data =fetch_pages()
print(data.keys())
quantite = len(data["results"])
print(quantite)
#print(data["results"])

