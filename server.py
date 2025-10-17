import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'
ENDPOINT = 'https://api.football-data.org/v4/matches'

@app.route('/matches')
def get_matches():
    headers = {'X-Auth-Token': API_TOKEN}
    today = date.today()
    date_from = today.isoformat()
    date_to = (today + timedelta(days=4)).isoformat()  # Modifica qui il range in giorni se vuoi più/meno partite

    params = {
        "competitions": "CL,SA,PD,PL,EL,ECL,WC,EC,FL1,BL1",  # Puoi aggiungere altri codici campionato
        "status": "SCHEDULED,LIVE",
        "dateFrom": date_from,
        "dateTo": date_to
    }

    response = requests.get(ENDPOINT, headers=headers, params=params)
    data = response.json()
    print(data)  # Rimuovi o commenta questa linea quando hai finito il debug

    matches = []
    for match in data.get('matches', []):
        matches.append({
            'date': match.get('utcDate', ''),
            'home': match['homeTeam']['name'],
            'away': match['awayTeam']['name'],
            'competition': match['competition']['name'],
            'channel': ''   # Rimane vuoto, da popolare se hai una fonte per i canali TV
        })
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
