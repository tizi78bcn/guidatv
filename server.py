import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)  # <-- Qui DEVE essere "app"
CORS(app)

THESPORTSDB_KEY = "1"  # Sostituisci con la tua key personale se ce l'hai

@app.route('/')
def index():
    return 'Backend is running!'

def collect_events_and_tvstations():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(4)]
    matches = []
    for single_day in days:
        day_str = single_day.isoformat()
        url = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_KEY}/eventsday.php?d={day_str}&s=Soccer"
        response = requests.get(url)
        data = response.json()
        if 'events' in data and data['events']:
            for event in data['events']:
                home = event.get('strHomeTeam', '')
                away = event.get('strAwayTeam', '')
                competition = event.get('strLeague', '')
                event_date = event.get('dateEvent', '')  # formato "YYYY-MM-DD"
                event_time = event.get('strTime', '')
                match_datetime = f"{event_date}T{event_time}" if event_time else f"{event_date}"
                id_event = event.get('idEvent', '')

                # Chiamata TV broadcaster
                channel = ""
                tv_url = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_KEY}/lookuptv.php?id={id_event}"
                tv_resp = requests.get(tv_url).json()
                if tv_resp and 'tvevents' in tv_resp and tv_resp['tvevents']:
                    tv_list = [tv['strTVStation'] for tv in tv_resp['tvevents'] if tv.get('strTVStation')]
                    channel = ", ".join(tv_list)

                matches.append({
                    'date': match_datetime,
                    'home': home,
                    'away': away,
                    'competition': competition,
                    'channel': channel
                })
    return matches

@app.route('/matches')
def get_matches():
    matches = collect_events_and_tvstations()
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
