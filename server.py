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

ITALIAN_CLUBS = [
    "Inter", "AC Milan", "Milan", "Juventus", "Napoli", "Lazio",
    "Roma", "Fiorentina", "Atalanta", "Torino", "Udinese", "Bologna",
    "Genoa", "Sampdoria", "Cagliari", "Verona", "Sassuolo", "Empoli",
    "Venezia", "Palermo", "Parma", "Brescia", "Spezia", "Salernitana", "Cremonese",
    "Monza", "Pisa", "Como"   # aggiungi club Serie A/B recenti
]

def normalize_team(name):
    return unidecode(name.lower().replace("'", "").replace("-", "").strip())

def is_italian_club(name):
    norm = normalize_team(name)
    for club in ITALIAN_CLUBS:
        if normalize_team(club) in norm:
            return True
    return False

def get_tv_channel_diretta(home, away):
    try:
        url = "https://www.diretta.it/partite/"
        resp = requests.get(url, timeout=8)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        home_s = normalize_team(home)
        away_s = normalize_team(away)
        for row in soup.find_all("div", class_="event__match"):
            text = normalize_team(row.text)
            if home_s in text and away_s in text:
                channel_div = row.find("div", class_="event__tv")
                canale = None
                if channel_div:
                    canale = channel_div.get_text(strip=True)
                if canale:
                    print(f"[DIRETTA.IT] Match {home}-{away}: canale esatto {canale}")
                    return canale
        print(f"[DIRETTA.IT] Match {home}-{away}: NESSUN canale esatto trovato")
        return ""
    except Exception as e:
        print(f"[Scraping diretta.it ERROR] Match {home}-{away}:", e)
        return ""

def get_tv_channel_marca(home, away):
    try:
        url = "https://www.marca.com/agenda-tv.html"
        resp = requests.get(url, timeout=8)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        home_s = normalize_team(home)
        away_s = normalize_team(away)
        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                match = normalize_team(tds[1].get_text(""))
                if home_s in match and away_s in match:
                    canale = tds[-1].get_text(strip=True)
                    if canale:
                        print(f"[MARCA.COM] Match {home}-{away}: canale esatto {canale}")
                        return canale
        print(f"[MARCA.COM] Match {home}-{away}: NESSUN canale trovato")
        return ""
    except Exception as e:
        print(f"[Scraping marca.com ERROR] Match {home}-{away}:", e)
        return ""

def get_fallback_channel(competition, home, away):
    if "Champions League" in competition:
        # Solo se club italiano
        if is_italian_club(home) or is_italian_club(away):
            return "Canale 5"
        else:
            return ""  # nessun fallback per non italiani
    elif "Serie A" in competition:
        return "DAZN, Sky Sport"
    elif "La Liga" in competition or "Primera Division" in competition or "Liga" in competition:
        return "DAZN (ES), Movistar Liga de Campeones"
    elif "Premier League" in competition:
        return "Sky Sport"
    elif "Bundesliga" in competition:
        return "Sky Sport"
    elif "Ligue 1" in competition:
        return "Sky Sport"
    elif "Europa League" in competition or "Conference League" in competition:
        return "DAZN"
    else:
        return ""

@app.route('/matches')
def get_matches():
    FOOTBALL_DATA_ENDPOINT = 'https://api.football-data.org/v4/matches'
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

        canale_ita = get_tv_channel_diretta(home, away)
        if canale_ita:
            canali.append("Italia: " + canale_ita)
        canale_esp = get_tv_channel_marca(home, away)
        if canale_esp:
            canali.append("Spagna: " + canale_esp)
        if not canali:
            fallback = get_fallback_channel(competition, home, away)
            if fallback:
                canali.append(fallback)
            print(f"[FALLBACK] {home}-{away} ({competition}): {fallback if fallback else 'nessun canale'}")
        channel = " — ".join(canali)

        matches.append({
            'date': match_date,
            'home': home,
            'away': away,
            'competition': competition,
            'channel': channel
        })
    print(f"NUMERO PARTITE FINALIZZATE: {len(matches)}")
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


