import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIG & GRID DATA ---
st.set_page_config(page_title="Shelly's 2026 Box Pool Tracker", page_icon="🏀", layout="centered")

# The specific, randomly drawn sequence for the grid axes
WINNER_AXIS = ['3', '2', '1', '6', '8', '9', '5', '0', '7', '4']
LOSER_AXIS = ['8', '7', '3', '0', '4', '2', '9', '5', '1', '6']

GRID_DATA = {
    '8': {'3': 'Chrissy Gonzalez', '2': 'Jay & Larry', '1': 'CKel', '6': 'Ciara Conlon', '8': 'Syd & Drew', '9': 'Gene M', '5': 'Babeh 😘', '0': 'Smelly', '7': 'Tim McNelis', '4': 'Fuck Fatboy'},
    '7': {'3': 'Tim McNelis', '2': 'Denis', '1': 'Jenna Apgar', '6': 'Mom & Dad', '8': 'Craig McNelis', '9': 'Sam Greenstein', '5': 'Babeh 😘', '0': 'Loretta Kelly', '7': 'Lou T', '4': 'Mr. B'},
    '3': {'3': 'L Dog', '2': 'Jay & Casey', '1': 'Kev & Hayley', '6': 'Babeh 😘', '8': 'Rob Farr', '9': 'Strober', '5': 'Taylor Kelly', '0': 'Roberto', '7': 'Craig McNelis', '4': 'Vitolo/Doc'},
    '0': {'3': 'Casey Wood', '2': 'Fogler', '1': 'GKel', '6': 'Tyler Conlon', '8': 'Danny B', '9': 'Vinny G', '5': 'Burgess', '0': 'Joe V', '7': 'Shelly', '4': 'Eoin'},
    '4': {'3': 'Denis / Mr. B', '2': 'Ric Pych', '1': 'Dan Whitcraft', '6': 'Eoin', '8': 'Tortomasi', '9': 'Lynn Spins', '5': 'Taylor Kelly', '0': 'Ferro', '7': 'Justin Yuka', '4': 'Mike/Eric/Matt'},
    '2': {'3': 'Amanda Fahey', '2': 'Shelly', '1': 'PD', '6': 'Tim Callahan', '8': 'Terzis', '9': 'Fuck Fatboy', '5': 'Keith McTarsney', '0': 'Rob Farr', '7': 'Marty / Tommy', '4': 'Kelly Bradley'},
    '9': {'3': 'Lou T', '2': 'CKel', '1': 'Frank D', '6': 'Meg', '8': 'Tommy Scanlon', '9': 'Pat Repoli', '5': 'Al', '0': 'Sean Lynch', '7': 'Fuck Fatboy', '4': 'Alan Lapa'},
    '5': {'3': 'Maureen McTarnsey', '2': 'Gus', '1': 'Billy Sullivan', '6': 'Mike C', '8': 'Dan West', '9': 'Ashling', '5': 'Chris Murray', '0': 'Irv', '7': 'Amanda Fahey', '4': 'Justin Yuka'},
    '1': {'3': 'Lloyd', '2': 'Ferro', '1': 'Tommy B', '6': 'Tim McNelis', '8': 'CKel', '9': 'Greg Doc', '5': 'Jardonne', '0': 'Sean Wohltman', '7': 'Banky/Doc', '4': 'Chris Murray'},
    '6': {'3': 'Derek Wanner', '2': 'Eugene', '1': 'Alan Lapa', '6': 'Fuck Fatboy', '8': 'GKel', '9': 'Vitolo', '5': 'Amanda Fahey', '0': 'Rose & Ben', '7': 'Rob Bodnar', '4': 'Fatboy'}
}

# Payout tiers
PAYOUT_MAP = {
    "1st Round": 50, "2nd Round": 100, "Sweet 16": 200, 
    "Elite 8": 400, "Final 4": 800, "Championship Final": 1500
}

def get_payout_info(date_str):
    schedule = {
        "20260319": "1st Round", "20260320": "1st Round",
        "20260321": "2nd Round", "20260322": "2nd Round",
        "20260326": "Sweet 16",  "20260327": "Sweet 16",
        "20260328": "Elite 8",   "20260329": "Elite 8",
        "20260404": "Final 4",   "20260406": "Championship Final"
    }
    rnd = schedule.get(date_str, "1st Round")
    return PAYOUT_MAP.get(rnd, 50), rnd

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_tournament_data():
    tz = pytz.timezone('US/Eastern')
    start_date = tz.localize(datetime(2026, 3, 19))
    end_date = datetime.now(tz)
    final_games, live_games = [], []
    current = start_date
    while current <= end_date:
        d_str = current.strftime("%Y%m%d")
        pay, rnd = get_payout_info(d_str)
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={d_str}"
        try:
            data = requests.get(url).json()
            for ev in data.get('events', []):
                status = ev['status']['type']['name']
                comp = ev['competitions'][0]
                h = next(t for t in comp['competitors'] if t['homeAway'] == 'home')
                a = next(t for t in comp['competitors'] if t['homeAway'] == 'away')
                h_s, a_s = int(h['score']), int(a['score'])
                
                h_seed = h.get('curatedRank', {}).get('current', 99)
                a_seed = a.get('curatedRank', {}).get('current', 99)
                h_disp = f"({h_seed}) {h['team']['shortDisplayName']}" if h_seed <= 16 else h['team']['shortDisplayName']
                a_disp = f"({a_seed}) {a['team']['shortDisplayName']}" if a_seed <= 16 else a['team']['shortDisplayName']
                
                if h_s > a_s: w_d, l_d = h_s % 10, a_s % 10
                else: w_d, l_d = a_s % 10, h_s % 10

                if "STATUS_FINAL" in status:
                    final_games.append({
                        "Winner": GRID_DATA.get(str(l_d), {}).get(str(w_d), "??"),
                        "Payout": pay, "W": str(w_d), "L": str(l_d), "Date": current.strftime("%m/%d"),
                        "Matchup": f"{a_disp} @ {h_disp}", "Result": f"{a_s}-{h_s}", "Round": rnd
                    })
                elif "STATUS_IN_PROGRESS" in status or "STATUS_HALFTIME" in status:
                    live_games.append({
                        "Matchup": f"{a_disp} @ {h_disp}", "Score": f"{a_s}-{h_s}",
                        "Time": ev['status']['type']['shortDetail'],
                        "Leader": GRID_DATA.get(str(l_d), {}).get(str(w_d), "??"), "Potential": pay
                    })
        except: pass
        current += timedelta(days=1)
    return final_games, live_games

# --- 3. UI DISPLAY ---
st.title("🏀 Shelly's 2026 Box Pool Tracker")
final_data, live_data = fetch_tournament_data()

# 1. LEADERBOARD
if final_data:
    st.header("🏆 Cumulative Standings")
    df_f = pd.DataFrame(final_data)
    lead = df_f.groupby("Winner").agg(Wins=('Winner','count'), Total=('Payout','sum')).sort_values("Total", ascending=False).reset_index()
    lead['Total'] = lead['Total'].map('${:,.0f}'.format)
    st.dataframe(lead, use_container_width=True, hide_index=True)

# 2. LIVE TRACKER
if live_data:
    st.header("⏳ Live Games")
    for g in live_data:
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"**{g['Matchup']}**")
            c1.write(f"{g['Score']} | {g['Time']}")
            c2.metric("Leader", g['Leader'], f"${g['Potential']}")

# 3. GAME HISTORY (Chronological: Top to Bottom)
if final_data:
    st.divider()
    st.header("📜 Game History")
    for g in final_data:
        with st.expander(f"**{g['Winner']}** won **${g['Payout']}** — {g['Matchup']} ({g['Result']})", expanded=False):
            st.write(f"**Date:** {g['Date']} ({g['Round']})")
            st.write(f"**Final Score:** {g['Result']} (Winner:{g['W']} Loser:{g['L']})")

# 4. STATISTICS & GRID
if final_data:
    st.divider()
    st.header("📈 Tournament Statistics")
    
    # Frequency Tally
    w_digits = [g['W'] for g in final_data]
    l_digits = [g['L'] for g in final_data]
    w_counts = pd.Series(w_digits).value_counts().reindex(WINNER_AXIS, fill_value=0).sort_values(ascending=False)
    l_counts = pd.Series(l_digits).value_counts().reindex(LOSER_AXIS, fill_value=0).sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Hot/Cold Winner Digits")
        st.write("**Top 3 Hot:** " + ", ".join([f"**{i}** ({v})" for i, v in w_counts.head(3).items()]))
        st.write("**Bottom 3 Cold:** " + ", ".join([f"**{i}** ({v})" for i, v in w_counts.tail(3).items()]))
    with col2:
        st.subheader("❄️ Hot/Cold Loser Digits")
        st.write("**Top 3 Hot:** " + ", ".join([f"**{i}** ({v})" for i, v in l_counts.head(3).items()]))
        st.write("**Bottom 3 Cold:** " + ", ".join([f"**{i}** ({v})" for i, v in l_counts.tail(3).items()]))

    # --- THE RANDOMIZED HEATMAP GRID ---
    st.subheader("🔥 Grid Heatmap")
    heatmap_wins = pd.DataFrame(0, index=LOSER_AXIS, columns=WINNER_AXIS)
    for g in final_data:
        heatmap_wins.at[g['L'], g['W']] += 1
    
    # Recalculate original counts for axis shading
    w_orig = pd.Series(w_digits).value_counts().reindex(WINNER_AXIS, fill_value=0)
    l_orig = pd.Series(l_digits).value_counts().reindex(LOSER_AXIS, fill_value=0)
    max_w, max_l = w_orig.max() or 1, l_orig.max() or 1
    max_cell = heatmap_wins.max().max() or 1

    html = """
    <style>
        .grid-container { overflow-x: auto; margin-top: 20px; border-radius: 8px; }
        .mm-table { width: 100%; min-width: 900px; border-collapse: collapse; font-family: sans-serif; font-size: 0.75rem; color: inherit; }
        .mm-table td, .mm-table th { border: 1px solid rgba(128,128,128,0.3); padding: 10px; text-align: center; vertical-align: middle; }
        .header-main { background-color: #003366; color: white; font-weight: bold; font-size: 0.8rem; }
        .header-digit { font-weight: bold; font-size: 0.8rem; }
        .side-label { background-color: #003366 !important; color: white !important; font-weight: bold; writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); width: 45px; font-size: 0.8rem; }
    </style>
    <div class='grid-container'>
    <table class='mm-table'>
    """

    # ROW 1: GAME WINNER (Merged Header)
    html += "<tr><td colspan='2' style='border:none;'></td><td colspan='10' class='header-main'>GAME WINNER</td></tr>"
    
    # ROW 2: Winner Digits (Random Order)
    html += "<tr><td colspan='2' style='border:none;'></td>"
    for i in WINNER_AXIS:
        opacity = min(w_orig[i] / max_w, 1.0) if w_orig[i] > 0 else 0
        html += f"<td class='header-digit' style='background-color: rgba(255, 102, 0, {opacity});'>{i}</td>"
    html += "</tr>"

    # ROWS: Side Label + Digits + Randomized Cells
    for idx, r in enumerate(LOSER_AXIS):
        html += "<tr>"
        if idx == 0:
            html += f"<td rowspan='10' class='side-label'>GAME LOSER</td>"
        
        l_opacity = min(l_orig[r] / max_l, 1.0) if l_orig[r] > 0 else 0
        html += f"<td class='header-digit' style='background-color: rgba(255, 102, 0, {l_opacity});'>{r}</td>"
        
        for c in WINNER_AXIS:
            val = heatmap_wins.at[r, c]
            owner = GRID_DATA.get(str(r), {}).get(str(c), "??")
            c_opacity = min(val / max_cell, 1.0) if val > 0 else 0
            txt_color = "white" if c_opacity > 0.5 else "inherit"
            
            html += f"<td style='background-color: rgba(255, 102, 0, {c_opacity}); color: {txt_color}; min-width: 85px; height: 60px;'>"
            html += f"<b>{owner}</b>"
            if val > 0: html += f"<br>({val} wins)"
            html += "</td>"
        html += "</tr>"

    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)

if st.button('Update Scores'):
    st.cache_data.clear()
    st.rerun()
