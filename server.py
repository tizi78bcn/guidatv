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

        # Italia — scraping diretta.it
        canale_ita = get_tv_channel_diretta(home, away)
        if canale_ita:
            canali.append("Italia: " + canale_ita)

        # Spagna — scraping marca.com
        canale_esp = get_tv_channel_marca(home, away)
        if canale_esp:
            canali.append("Spagna: " + canale_esp)

        # Champions League: fallback logica avanzata
        if "Champions League" in competition and not (canale_ita or canale_esp):
            entry = []
            if is_italian_club(home) or is_italian_club(away):
                entry.append("Canale 5")
            # Sempre aggiungi anche la pay spagnola (fallback se assente scraping!)
            entry.append("Movistar Liga de Campeones")
            entry.append("Sky Sport")
            entry.append("DAZN")
            canali.append(", ".join(entry))
        elif not canali:
            # altri fallback come da campionato
            fallback = get_fallback_channel(competition, home, away)
            if fallback:
                canali.append(fallback)
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
