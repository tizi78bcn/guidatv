import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'
ENDPOINT = 'https://api.football-data.org/v4/matches'

@app.route('/matches')
def get_matches():
    headers = {'X-Auth-Token': API_TOKEN}
   params = {
    "competitions": "CL,SA,PD,PL,EL,ECL,WC,EC,FL1",
    "status": "SCHEDULED"
}
    response = requests.get(ENDPOINT, headers=headers, params=params)
    data = response.json()
    print(data)
    matches = []
    for match in data.get('matches', []):
        matches.append({
            'date': match['utcDate'],
            'home': match['homeTeam']['name'],
            'away': match['awayTeam']['name'],
            'competition': match['competition']['name'],
            'channel': ''   # Da riempire se trovi anche nomi canali TV
        })
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


