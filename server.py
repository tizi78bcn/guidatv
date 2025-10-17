import requests
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import date, timedelta
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'Backend is running!'

@app.route('/matches')
def get_matches():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(4)]
    matches = []
    for single_day in days:
        day_str = single_day.isoformat()
        url = f"https://www.thesportsdb.com/api/v1/json/1/eventsday.php?d={day_str}&s=Soccer"
        response = requests.get(url)
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
            except Exception:
                continue
            if 'events' in data and data['events']:
                for event in data['events']:
                    home = event.get('strHomeTeam', '')
                    away = event.get('strAwayTeam', '')
                    competition = event.get('strLeague', '')
                    event_date = event.get('dateEvent', '')
                    event_time = event.get('strTime', '')
                    match_datetime = f"{event_date}T{event_time}" if event_time else f"{event_date}"
                    id_event = event.get('idEvent', '')
                    channel = ""
                    tv_url = f"https://www.thesportsdb.com/api/v1/json/1/lookuptv.php?id={id_event}"
                    tv_resp = requests.get(tv_url)
                    if tv_resp.status_code == 200 and tv_resp.text.strip():
                        try:
                            tv_data = tv_resp.json()
                            if tv_data and 'tvevents' in tv_data and tv_data['tvevents']:
                                tv_list = [tv['strTVStation'] for tv in tv_data['tvevents'] if tv.get('strTVStation')]
                                channel = ", ".join(tv_list)
                        except Exception:
                            pass
                    matches.append({
                        'date': match_datetime,
                        'home': home,
                        'away': away,
                        'competition': competition,
                        'channel': channel
                    })
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
