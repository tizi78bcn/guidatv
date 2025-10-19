import requests
from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from unidecode import unidecode
import os
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

API_TOKEN = '25587c5b08c3454280851f933ca0cc19'
SPORTMONKS_TOKEN = '7OKlYCEyMOngBGRF6zvnNsVMvFZi1Dua2sO7WCPX5iRhIeeNpEaTNWG5yIU9'

def normalize_team(name):
    # Rende la stringa insensibile ad accenti, apostrofi e maiuscole
    return unidecode(name.lower().replace("'", "").replace("-", "").strip())

def get_tv_channel_diretta(home, away):
    # Cerca broadcaster Italia su diretta.it
    try:
        url = "https://www.diretta.it/partite/"
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        home_s = normalize_team(home)
        away_s = normalize_team(away)
        for row in soup.find_all("div", class_="event__match--scheduled"):
            text = normalize_team(row.text)
            if home_s in text and away_s in text:
                channel_div = row.find_next("div", class_="event__tv")
                if channel_div:
                    canale = channel_div.get_text(strip=True)
                    if canale:
                        return canale
        return ""
    except Exception as e:
        print("[Scraping diretta.it ERROR]", e)
        return ""

def get_tv_channel_marca(home, away):
    # Cerca broadcaster Spagna su marca.com
    try:
        url = "https://www.marca.com/agenda-tv.html"
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        home_s = normalize_team(home)
        away_s = normalize_team(away)
        for td in soup.find_all("td"):
            match = normalize_team(td.get_text(""))
            # Cerca team in cella (match tipo "Real Sociedad - Getafe")
            if home_s in match and away_s in match:
                for sibling in td.find_next_siblings("td"):
                    canale = sibling.get_text(strip=True)
                    if canale and canale.upper() != "Hora":
                        return canale
        return ""
    except Exception as e:
        print("[Scraping marca.com ERROR]", e)
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

        canali = []

        # Italia: diretta.it
        canale_ita = get_tv_channel_diretta(home, away)
        if canale_ita:
            canali.append("Italia: " + canale_ita)
        # Spagna: marca.com
        canale_esp = get_tv_channel_marca(home, away)
        if canale_esp:
            canali.append("Spagna: " + canale_esp)
        channel = " — ".join(canali)

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
