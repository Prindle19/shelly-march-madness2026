import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIG & GRID DATA ---
st.set_page_config(page_title="Shelly's 2026 Box Pool Tracker", page_icon="🏀", layout="centered")

# Randomized sequence for the grid axes
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

# --- 2. DYNAMIC COLOR & GRAMMAR ENGINE ---
def get_stretched_gradient(val, mx, mid):
    if val == mid:
        return "rgba(128, 128, 128, 0.2)", "inherit"
    if val > mid:
        ratio = (val - mid) / (mx - mid) if (mx - mid) > 0 else 0
        r, g, b = int(128 + (127 * ratio)), int(128 - (123 * ratio)), int(128 - (123 * ratio))
        return f"rgb({r}, {g}, {b})", ("white" if ratio > 0.4 else "black")
    else:
        ratio = val / mid if mid > 0 else 0
        r, g, b = int(5 + (123 * ratio)), int(255 - (127 * ratio)), int(255 - (127 * ratio))
        return f"rgb({r}, {g}, {b})", ("white" if ratio < 0.6 else "black")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_tournament_data():
    tz = pytz.timezone('US/Eastern')
    start_date, end_date = tz.localize(datetime(2026, 3, 19)), datetime.now(tz)
    final_games, live_games = [], []
    current = start_date
    while current <= end_date:
        d_str = current.strftime("%Y%m%d")
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={d_str}"
        try:
            data = requests.get(url).json()
            for ev in data.get('events', []):
                status = ev['status']['type']['name']
                comp = ev['competitions'][0]
                h = next(t for t in comp['competitors'] if t['homeAway'] == 'home')
                a = next(t for t in comp['competitors'] if t['homeAway'] == 'away')
                h_s, a_s = int(h['score']), int(a['score'])
                w_d, l_d = (h_s % 10, a_s % 10) if h_s > a_s else (a_s % 10, h_s % 10)
                if "STATUS_FINAL" in status:
                    final_games.append({"Winner": GRID_DATA.get(str(l_d), {}).get(str(w_d), "??"), "W": str(w_d), "L": str(l_d), "Matchup": f"{a['team']['shortDisplayName']} @ {h['team']['shortDisplayName']}", "Result": f"{a_s}-{h_s}"})
        except: pass
        current += timedelta(days=1)
    return final_games, []

# --- 4. UI DISPLAY ---
st.title("🏀 Shelly's 2026 Box Pool Tracker")
final_data, _ = fetch_tournament_data()

if final_data:
    all_digits = [g['W'] for g in final_data] + [g['L'] for g in final_data]
    counts = pd.Series(all_digits).value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    max_c, mid_c = counts.max() or 1, counts.median() or (counts.max() / 2)
    
    heatmap_wins = pd.DataFrame(0, index=LOSER_AXIS, columns=WINNER_AXIS)
    for g in final_data: heatmap_wins.at[g['L'], g['W']] += 1
    max_win = heatmap_wins.max().max() or 1
    mid_win = heatmap_wins[heatmap_wins > 0].median().median() if not heatmap_wins[heatmap_wins > 0].empty else 0.5

    html_grid = """
    <style>
        .grid-container { overflow-x: auto; margin-top: 20px; border-radius: 8px; }
        .mm-table { width: 100%; min-width: 900px; border-collapse: collapse; font-family: sans-serif; font-size: 0.8rem; }
        .mm-table td { border: 1px solid rgba(128,128,128,0.3); padding: 10px; text-align: center; vertical-align: middle; }
        .header-main { background-color: #31333F; color: white; font-weight: bold; text-transform: uppercase; }
        .side-label { background-color: #31333F !important; color: white !important; font-weight: bold; writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); width: 45px; }
    </style>
    <div class='grid-container'><table class='mm-table'>
    """
    html_grid += "<tr><td colspan='2' style='border:none;'></td><td colspan='10' class='header-main'>GAME WINNER</td></tr>"
    html_grid += "<tr><td colspan='2' style='border:none;'></td>"
    for i in WINNER_AXIS:
        bg, tx = get_stretched_gradient(counts[i], max_c, mid_c)
        html_grid += f"<td style='background:{bg}; color:{tx}; font-weight:bold;'>{i}</td>"
    html_grid += "</tr>"

    for idx, r in enumerate(LOSER_AXIS):
        html_grid += "<tr>"
        if idx == 0: html_grid += f"<td rowspan='10' class='side-label'>GAME LOSER</td>"
        bg_l, tx_l = get_stretched_gradient(counts[r], max_c, mid_c)
        html_grid += f"<td style='background:{bg_l}; color:{tx_l}; font-weight:bold;'>{r}</td>"
        for c in WINNER_AXIS:
            wins = heatmap_wins.at[r, c]
            bg_cell, tx_cell = get_stretched_gradient(wins, max_win, mid_win) if wins > 0 else ("rgba(128,128,128,0.05)", "inherit")
            html_grid += f"<td style='background:{bg_cell}; color:{tx_cell}; min-width:85px; height:60px;'><b>{GRID_DATA.get(r,{}).get(c,'??')}</b>"
            if wins > 0: html_grid += f"<br><span style='font-size: 0.65rem; opacity: 0.8;'>({wins} {'Win' if wins==1 else 'Wins'})</span>"
            html_grid += "</td>"
        html_grid += "</tr>"
    st.markdown(html_grid + "</table></div>", unsafe_allow_html=True)

if st.button('Update Scores'):
    st.cache_data.clear()
    st.rerun()
