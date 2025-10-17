import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)
print(f"Team Football-Data: {home} - {away}")

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
        # Estrai nome squadre e altri dati dal match
        match_date = match.get('utcDate', '')
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        competition = match['competition']['name']
        # In Football-Data API non c'è il canale TV, dobbiamo recuperarlo da Sportmonks
        # Proviamo il match tramite Sportmonks: serve l'id della partita Sportmonks, qui puoi mappare tramite nome/data/squadre

        # Esempio: chiama cerca fixure da Sportmonks per nome e data (migliorabile con id campionato)
        query_sportmonks = f"{SPORTMONKS_ENDPOINT}?api_token={SPORTMONKS_TOKEN}&date={match_date[:10]}"
        sm_response = requests.get(query_sportmonks)
        sm_data = sm_response.json()
for match in data.get('matches', []):
    # (codice per estrarre home, away, match_date ...)
    print(f"Football-Data: {home} vs {away} on {match_date}")
    
    # Fai qui la chiamata Sportmonks → sm_response = requests.get(...)
    print(f"Sportmonks Response for date {match_date[:10]}: {sm_response.text}")  # Mostra la raw response qui

    # QUI: dopo la chiamata dettaglio tvstations
    tv_response = requests.get(url_tv)  # URL dettagliata include=tvstations
    tv_data = tv_response.json()
    
    channels = tv_data['data'].get('tvstations', [])
    if channels:
        channel = ", ".join([ch['name'] for ch in channels])
    else:
        channel = ""  # O 'Non disponibile'
    
    matches.append({
        'date': match_date,
        'home': home,
        'away': away,
        'competition': competition,
        'channel': channel
    })

    if 'data' in sm_data:
    for sm_match in sm_data['data']:
        print(f"Team Sportmonks: {sm_match.get('home_team_name', '')} - {sm_match.get('away_team_name', '')}")


        channel = ""
        # Ricerca partita corrispondente (per data, nome squadre): semplificata!
        if 'data' in sm_data:
            for sm_match in sm_data['data']:
                sm_home = sm_match.get('home_team_name', '').lower()
                sm_away = sm_match.get('away_team_name', '').lower()
                if home.lower() in sm_home and away.lower() in sm_away:
                    fixture_id = sm_match['id']
                    # Richiesta dettagli con canali TV per il fixture_id
                    url_tv = f"https://api.sportmonks.com/v3/football/fixtures/{fixture_id}?include=tvstations&api_token={SPORTMONKS_TOKEN}"
                    tv_response = requests.get(url_tv)
                    tv_data = tv_response.json()
                    if 'data' in tv_data and 'tvstations' in tv_data['data']:
                        tv_list = tv_data['data']['tvstations']
                        # Prendi tutti i broadcaster disponibili separati da virgola
                        channel = ", ".join([ch['name'] for ch in tv_list])
                    break  # Abbiamo trovato la partita

        if home.lower() in sm_home and away.lower() in sm_away:
    fixture_id = sm_match['id']
    url_tv = f"https://api.sportmonks.com/v3/football/fixtures/{fixture_id}?include=tvstations&api_token={SPORTMONKS_TOKEN}"
    tv_response = requests.get(url_tv)
    print("TVstations raw response:", tv_response.text)
    tv_data = tv_response.json()
    # Subito dopo parsing:
    channels = tv_data['data'].get('tvstations', [])
    print("Channels found:", channels)
        
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




