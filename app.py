import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIG & GRID ---
st.set_page_config(page_title="2026 Box Pool", page_icon="🏀", layout="centered")

# Hardcoded from your spreadsheet image
GRID_DATA = {
    '8': {'3': 'Chrissy Gonzalez', '2': 'Jay & Larry', '1': 'CKel', '6': 'Ciara Conlon', '8': 'Syd & Drew', '9': 'Gene M', '5': 'Babeh 😘', '0': 'Smelly', '7': 'Tim McNelis', '4': 'Fuck Fatboy'},
    '7': {'3': 'Tim McNelis', '2': 'Denis', '1': 'Jenna Apgar', '6': 'Mom & Dad', '8': 'Craig McNelis', '9': 'Sam Greenstein', '5': 'Babeh 😘', '0': 'Loretta Kelly', '7': 'Lou T', '4': 'Mr. B'},
    '3': {'3': 'L Dog', '2': 'Jay & Casey', '1': 'Kev & Hayley', '6': 'Babeh 😘', '8': 'Rob Farr', '9': 'Strober', '5': 'Taylor Kelly', '0': 'Roberto', '7': 'Craig McNelis', '4': 'Vitolo/Doc'},
    '0': {'3': 'Casey Wood', '2': 'Fogler', '1': 'GKel', '6': 'Tyler Conlon', '8': 'Danny B', '9': 'Vinny G', '5': 'Burgess', '0': 'Joe V', '7': 'Shelly', '4': 'Eoin'},
    '4': {'3': 'Denis / Mr. B', '2': 'Ric Pych', '1': 'Dan Whitcraft', '6': 'Eoin', '8': 'Tortomasi', '9': 'Lynn Spins', '5': 'Taylor Kelly', '0': 'Ferro', '7': 'Justin Yuka', '4': 'Mike/Eric/Matt'},
    '2': {'3': 'Amanda Fahey', '2': 'Shelly', '1': 'PD', '6': 'Tim Callahan', '8': 'Terzis', '9': 'Fuck Fatboy', '5': 'Keith McTarsney', '0': 'Rob Farr', '7': 'Marty / Tommy', '4': 'Kelly Bradley'},
    '9': {'3': 'Lou T', '2': 'CKel', '1': 'Frank D', '6': 'Meg', '8': 'Tommy Scanlon', '9': 'Pat Repoli', '5': 'Al', '0': 'Sean Lynch', '7': 'Fuck Fatboy', '4': 'Alan Lapa'},
    '5': {'3': 'Maureen McTarnsey', '2': 'Gus', '1': 'Billy Sullivan', '6': 'Mike C', '8': 'Dan West', '9': 'Ashling', '5': 'Chris Murray', '0': 'Irv', '7': 'Amanda Fahey', '4': 'Justin Yuka'},
    '1': {'3': 'Lloyd', '2': 'Ferro', '1': 'Tommy B', '6': 'Tim McNelis', '8': 'CKel', '9': 'Greg Doc', '5': 'Jardonne', '0': 'Sean Wohltman', '7': 'Mike/Eric/Matt', '4': 'Chris Murray'},
    '6': {'3': 'Derek Wanner', '2': 'Eugene', '1': 'Alan Lapa', '6': 'Fuck Fatboy', '8': 'GKel', '9': 'Vitolo', '5': 'Amanda Fahey', '0': 'Rose & Ben', '7': 'Rob Bodnar', '4': 'Fatboy'}
}

def get_payout_for_date(date_str):
    schedule = {
        "20260319": (50, "1st Round"), "20260320": (50, "1st Round"),
        "20260321": (100, "2nd Round"), "20260322": (100, "2nd Round"),
        "20260326": (200, "Sweet 16"), "20260327": (200, "Sweet 16"),
        "20260328": (400, "Elite 8"), "20260329": (400, "Elite 8"),
        "20260404": (800, "Final 4"), "20260406": (1500, "Finals")
    }
    return schedule.get(date_str, (0, "Off Day"))

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=600) # Cache for 10 minutes to stay fast
def fetch_tournament_data():
    tz = pytz.timezone('US/Eastern')
    start_date = tz.localize(datetime(2026, 3, 19))
    end_date = datetime.now(tz)
    
    games_list = []
    current = start_date
    while current <= end_date:
        d_str = current.strftime("%Y%m%d")
        payout, rnd = get_payout_for_date(d_str)
        if payout > 0:
            url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={d_str}"
            try:
                data = requests.get(url).json()
                for event in data.get('events', []):
                    if "FINAL" in event['status']['type']['name']:
                        comp = event['competitions'][0]
                        h = next(t for t in comp['competitors'] if t['homeAway'] == 'home')
                        a = next(t for t in comp['competitors'] if t['homeAway'] == 'away')
                        h_score, a_score = int(h['score']), int(a['score'])
                        
                        winner = GRID_DATA.get(str(a_score%10), {}).get(str(h_score%10), "Unknown")
                        games_list.append({
                            "Date": current.strftime("%m/%d"),
                            "Matchup": f"{a['team']['shortDisplayName']} @ {h['team']['shortDisplayName']}",
                            "Result": f"{a_score}-{h_score}",
                            "Winner": winner,
                            "Payout": payout,
                            "Round": rnd
                        })
            except: pass
        current += timedelta(days=1)
    return games_list

# --- 3. UI LAYOUT ---
st.title("🏀 2026 Box Pool")
st.write("Live standings and payouts.")

data = fetch_tournament_data()

if data:
    df = pd.DataFrame(data)
    
    # Leaderboard Section
    st.header("🏆 Leaderboard")
    leader = df.groupby("Winner").agg(Wins=('Winner','count'), Payout=('Payout','sum')).sort_values("Payout", ascending=False)
    st.table(leader)

    # Game History Section
    st.header("📜 Game History")
    for g in reversed(data):
        with st.expander(f"{g['Winner']} won ${g['Payout']} - {g['Matchup']}", expanded=False):
            st.write(f"**Date:** {g['Date']} ({g['Round']})")
            st.write(f"**Final Score:** {g['Result']}")
            st.write(f"**Pool Winner:** {g['Winner']}")
else:
    st.info("The tournament is just starting! Check back once games go Final.")

if st.button('Update Scores'):
    st.cache_data.clear()
    st.rerun()
