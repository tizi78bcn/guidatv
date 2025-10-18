import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'
SPORTMONKS_TOKEN = '7OKlYCEyMOngBGRF6zvnNsVMvFZi1Dua2sO7WCPX5iRhIeeNpEaTNWG5yIU9'
THESPORTSDB_APIKEY = '1'

FOOTBALL_DATA_ENDPOINT = 'https://api.football-data.org/v4/matches'
SPORTMONKS_ENDPOINT = 'https://api.sportmonks.com/v3/football/fixtures'

def get_tv_channel_thesportsdb(home, away, match_date):
    print(f"[TheSportsDB] Cerco match: {home} vs {away} ({match_date})")
    event_name = f"{home}_vs_{away}".replace(" ", "_")
    url_search = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_APIKEY}/searchevents.php?e={event_name}&d={match_date[:10]}"
    try:
        resp = requests.get(url_search, timeout=8)
        data = resp.json()
        print(f"[TheSportsDB] search response: {data}")
        if data and 'event' in data and data['event']:
            event_id = data['event'][0].get('idEvent', None)
            if event_id:
                url_tv = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_APIKEY}/eventstv.php?id={event_id}"
                tv_resp = requests.get(url_tv, timeout=8)
                tv_data = tv_resp.json()
                print(f"[TheSportsDB] tv response: {tv_data}")
                if tv_data and 'tvstations' in tv_data and tv_data['tvstations']:
                    canali = [tv['strTVStation'] for tv in tv_data['tvstations'] if 'strTVStation' in tv]
                    if canali:
                        return ", ".join(canali)
    except Exception as e:
        print(f"[TheSportsDB] ERRORE per {home} vs {away} ({match_date}):", e)
    return ""

@app.route('/matches')
def get_matches():
    headers = {'X-Auth-Token': API_TOKEN}
    today = date.today()
    date_from = today.isoformat()
    date_to = (today + timedelta(days=4)).isoformat()
    print(f"[FootballData] Fetch: {date_from} to {date_to}")

    params = {
        "competitions": "CL,SA,PD,PL,EL,ECL,WC,EC,FL1,BL1",
        "status": "SCHEDULED,LIVE",
        "dateFrom": date_from,
        "dateTo": date_to
    }

    try:
        response = requests.get(FOOTBALL_DATA_ENDPOINT, headers=headers, params=params, timeout=15)
        data = response.json()
    except Exception as e:
        print(f"[FootballData] ERRORE API: {e}")
        return jsonify([])

    matches = []
    for match in data.get('matches', []):
        try:
            match_date = match.get('utcDate', '')
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            competition = match['competition']['name']
        except Exception as e:
            print("[FootballData] ERRORE parsing match:", e)
            continue

        print(f"[Match] {home} vs {away} ({match_date}) in {competition}")

        channel = ""

        # Sportmonks TV info
        try:
            query_sportmonks = f"{SPORTMONKS_ENDPOINT}?api_token={SPORTMONKS_TOKEN}&date={match_date[:10]}"
            sm_response = requests.get(query_sportmonks, timeout=8)
            sm_data = sm_response.json()
            print(f"[SportMonks] response: {sm_data}")
            if 'data' in sm_data:
                for sm_match in sm_data['data']:
                    sm_home = sm_match.get('home_team_name', '').lower()
                    sm_away = sm_match.get('away_team_name', '').lower()
                    if home.lower() in sm_home and away.lower() in sm_away:
                        fixture_id = sm_match['id']
                        url_tv = f"https://api.sportmonks.com/v3/football/fixtures/{fixture_id}?include=tvstations&api_token={SPORTMONKS_TOKEN}"
                        tv_response = requests.get(url_tv, timeout=8)
                        tv_data = tv_response.json()
                        print(f"[SportMonks] tv response: {tv_data}")
                        if 'data' in tv_data and 'tvstations' in tv_data['data']:
                            tv_list = tv_data['data']['tvstations']
    import sys
    print("PYTHON VERSION:", sys.version)



