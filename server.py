import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'             # Football-Data API
SPORTMONKS_TOKEN = '7OKlYCEyMOngBGRF6zvnNsVMvFZi1Dua2sO7WCPX5iRhIeeNpEaTNWG5yIU9'  # Sportmonks API

FOOTBALL_DATA_ENDPOINT = 'https://api.football-data.org/v4/matches'
SPORTMONKS_ENDPOINT = 'https://api.sportmonks.com/v3/football/fixtures'

@app.route('/matches')
def get_matches():
    headers = {'X-Auth-Token': API_TOKEN}
    today = date.today()
    date_from = today.isoformat()
    date_to = (today + timedelta(days=4)).isoformat()

    params = {
        "competitions": "CL,SA,PD,PL,EL,ECL,WC,EC,FL1,BL1",
        "status": "SCHEDULED,LIVE",
        "dateFrom": date_from,
        "dateTo": date_to
    }

    response = requests.get(FOOTBALL_DATA_ENDPOINT, headers=headers, params=params)
    data = response.json()

    matches = []
    for match in data.get('matches', []):
        match_date = match.get('utcDate', '')
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        competition = match['competition']['name']
        print(f"Team Football-Data: {home} - {away}")

        # Cerca fixture Sportmonks per data
        query_sportmonks = f"{SPORTMONKS_ENDPOINT}?api_token={SPORTMONKS_TOKEN}&date={match_date[:10]}"
        sm_response = requests.get(query_sportmonks)
        print(f"Sportmonks Response for date {match_date[:10]}: {sm_response.text}")  # Debug
        sm_data = sm_response.json()

        channel = ""
        # Matching tra squadre: per ogni partita trovata su Sportmonks
        if 'data' in sm_data:
            for sm_match in sm_data['data']:
                sm_home = sm_match.get('name', '').split(' vs ')[0].lower()
                sm_away = sm_match.get('name', '').split(' vs ')[-1].lower()
                print(f"Team Sportmonks: {sm_home} - {sm_away}")  # Debug
                # Matching su home/away
                if home.lower() in sm_home and away.lower() in sm_away:
                    fixture_id = sm_match['id']
                    url_tv = f"https://api.sportmonks.com/v3/football/fixtures/{fixture_id}?include=tvstations&api_token={SPORTMONKS_TOKEN}"
                    tv_response = requests.get(url_tv)
                    print("TVstations raw response:", tv_response.text)
                    tv_data = tv_response.json()
                    channels = tv_data['data'].get('tvstations', [])
                    print("Channels found:", channels)  # Debug
                    if channels:
                        channel = ", ".join([ch['name'] for ch in channels])
                    break

        matches.append({
            'date': match_date,
            'home': home,
            'away': away,
            'competition': competition,
            'channel': channel
        })
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
