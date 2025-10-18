import requests
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'
SPORTMONKS_TOKEN = '7OKlYCEyMOngBGRF6zvnNsVMvFZi1Dua2sO7WCPX5iRhIeeNpEaTNWG5yIU9'

def get_tv_channel_thesportsdb(home, away, match_date):
    # Cerca evento con API SportsDB
    event_name = f"{home}_vs_{away}".replace(" ", "_")
    url_search = f"https://www.thesportsdb.com/api/v1/json/1/searchevents.php?e={event_name}&d={match_date[:10]}"
    try:
        resp = requests.get(url_search, timeout=6)
        data = resp.json()
        if data and 'event' in data and data['event']:
            event_id = data['event'][0].get('idEvent', None)
            if event_id:
                url_tv = f"https://www.thesportsdb.com/api/v1/json/1/eventstv.php?id={event_id}"
                tv_resp = requests.get(url_tv, timeout=6)
                tv_data = tv_resp.json()
                if tv_data and 'tvstations' in tv_data and tv_data['tvstations']:
                    canali = [tv['strTVStation'] for tv in tv_data['tvstations'] if 'strTVStation' in tv]
                    if canali:
                        return ", ".join(canali)
    except Exception as e:
        print(f"[TheSportsDB][ERROR] {home} vs {away}: {e}")
    return ""

def get_tv_channel_diretta(home, away, match_date):
    from bs4 import BeautifulSoup
    import requests
    # Esempio scraping: va revisionato in base alla struttura reale!
    url = "https://www.diretta.it/partite/"
    try:
        resp = requests.get(url, timeout=6)
        soup = BeautifulSoup(resp.text, "html.parser")
        tv_divs = soup.find_all("div", class_="tv")
        for tvd in tv_divs:
            channel = tvd.get_text(strip=True)
            if channel:
                return channel
    except Exception as e:
        print(f"[diretta.it][ERROR] {home} vs {away}:", e)
    return ""

@app.route('/matches')
def get_matches():
    FOOTBALL_DATA_ENDPOINT = 'https://api.football-data.org/v4/matches'
    SPORTMONKS_ENDPOINT = 'https://api.sportmonks.com/v3/football/fixtures'
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

        channel = ""
        # Sportmonks (come prima)
        try:
            query_sportmonks = f"{SPORTMONKS_ENDPOINT}?api_token={SPORTMONKS_TOKEN}&date={match_date[:10]}"
            sm_response = requests.get(query_sportmonks, timeout=6)
            sm_data = sm_response.json()
            if 'data' in sm_data:
                for sm_match in sm_data['data']:
                    sm_home = sm_match.get('home_team_name', '').lower()
                    sm_away = sm_match.get('away_team_name', '').lower()
                    if home.lower() in sm_home and away.lower() in sm_away:
                        fixture_id = sm_match['id']
                        url_tv = f"https://api.sportmonks.com/v3/football/fixtures/{fixture_id}?include=tvstations&api_token={SPORTMONKS_TOKEN}"
                        tv_response = requests.get(url_tv, timeout=6)
                        tv_data = tv_response.json()
                        if 'data' in tv_data and 'tvstations' in tv_data['data']:
                            tv_list = tv_data['data']['tvstations']
                            if tv_list:
                                channel = ", ".join([ch['name'] for ch in tv_list])
                        break
        except Exception as e:
            print("[Sportmonks error]:", e)

        # Fallback 1: TheSportsDB
        if not channel:
            channel = get_tv_channel_thesportsdb(home, away, match_date)
        # Fallback 2: Diretta.it solo per Serie A/Italia
        if not channel and "Serie A" in competition:
            channel = get_tv_channel_diretta(home, away, match_date)
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

