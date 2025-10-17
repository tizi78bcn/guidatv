from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

matches = [
    {
        "id": 1,
        "home": "Juventus",
        "away": "Inter",
        "datetime": "2025-10-20T20:45:00",
        "country": "Italia",
        "broadcast": True,
        "channel": "DAZN 1"
    },
    {
        "id": 2,
        "home": "Barcelona",
        "away": "Real Madrid",
        "datetime": "2025-10-21T21:00:00",
        "country": "Spagna",
        "broadcast": True,
        "channel": "Movistar LaLiga"
    },
    {
        "id": 3,
        "home": "Manchester United",
        "away": "Liverpool",
        "datetime": "2025-10-22T18:30:00",
        "country": "Inghilterra",
        "broadcast": True,
        "channel": "Sky Sport Premier"
    },
    {
        "id": 4,
        "home": "Napoli",
        "away": "Roma",
        "datetime": "2025-10-23T20:45:00",
        "country": "Italia",
        "broadcast": False,
        "channel": ""
    }
]

@app.route('/matches')
def get_matches():
    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True)
