import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'  # Football-Data API
SPORTMONKS_TOKEN = '7OKlYCEyMOngBGRF6zvnNsVMvFZi1Dua2sO7WCPX5iRhIeeNpEaTNWG5yIU9'
THESPORTSDB_APIKEY = '1'

FOOTBALL_DATA_ENDPOINT = 'https://api.football-data.org/v4/matches'
SPORTMONKS_ENDPOINT = 'https://api.sportmonks.com/v3/football/fixtures'

def get_tv_channel_thesportsdb(home, away, match_date):
    event_name = f"{home}_vs_{away}".replace(" ", "_")
    url_search = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_APIKEY}/searchevents.php?e={event_name}&d={match_date[:10]}"
    try:
        resp = requests.get(url_search, timeout=8)
        data = resp.json()
        if data and 'event' in data and data['event']:
            event_id = data['event'][0].get('idEvent', None)
            if event_id:
                url_tv = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_APIKEY}/eventstv.php?id={event_id}"
                tv_resp = requests.get(url_tv, timeout=8)
                tv_data = tv_resp.json()
                if tv_data and 'tvstations' in tv_data and tv_data['tvstations']:
                    canali = [tv['strTVStation'] for tv in tv_data['tvstations'] if 'strTVStation' in tv]
                    if canali:
                        return ", ".join(canali)
    except Exception as e:
        print("Errore TV SportsDB:", e)
    return ""

@app.route('/matches')
def get_matches():
    headers = {'X-Auth-Token': API_TOKEN}
    today = date.today()
    date_from = today.isoformat()
    date_to
