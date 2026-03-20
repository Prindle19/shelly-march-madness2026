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

PAYOUT_MAP = {
    "1st Round": 50, "2nd Round": 100, "Sweet 16": 200, 
    "Elite 8": 400, "Final 4": 800, "Championship Final": 1500
}

TOTAL_PRIZE_POOL = 9500

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

# --- 2. DYNAMIC COLOR & GRAMMAR ENGINE ---
def get_stretched_gradient(val, mx, mid):
    if val == mid:
        return "rgba(128, 128, 128, 0.2)", "inherit"
    
    if val > mid:
        ratio = (val - mid) / (mx - mid) if (mx - mid) > 0 else 0
        r = int(128 + (127 * ratio))
        g = int(128 - (123 * ratio))
        b = int(128 - (123 * ratio))
        txt = "white" if ratio > 0.4 else "black"
        return f"rgb({r}, {g}, {b})", txt
    else:
        ratio = val / mid if mid > 0 else 0
        r = int(5 + (123 * ratio))
        g = int(255 - (127 * ratio))
        b = int(255 - (127 * ratio))
        txt = "white" if ratio < 0.6 else "black"
        return f"rgb({r}, {g}, {b})", txt

# --- 3. DATA ENGINE ---
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
                
                # --- EXTRACT AND CONVERT EXACT GAME TIME ---
                dt_raw = ev.get('date')
                if dt_raw:
                    dt = pd.to_datetime(dt_raw)
                    if dt.tz is None:
                        dt = dt.tz_localize('UTC')
                    dt_est = dt.tz_convert('US/Eastern')
                    sort_time = dt_est.timestamp()
                    display_time = dt_est.strftime("%I:%M %p").lstrip('0')
                else:
                    sort_time = 0
                    display_time = "TBD"

                if "STATUS_FINAL" in status:
                    final_games.append({
                        "Winner": GRID_DATA.get(str(l_d), {}).get(str(w_d), "??"),
                        "Payout": pay, "W": str(w_d), "L": str(l_d), "Date": current.strftime("%m/%d"),
                        "GameTime": sort_time, "DisplayTime": display_time,
                        "Matchup": f"{a_disp} @ {h_disp}", "Result": f"{a_s}-{h_s}", "Round": rnd
                    })
                elif "STATUS_IN_PROGRESS" in status or "STATUS_HALFTIME" in status:
                    live_games.append({
                        "Matchup": f"{a_disp} @ {h_disp}", "Score": f"{a_s}-{h_s}",
                        "Time": ev['status']['type']['shortDetail'],
                        "DisplayTime": display_time,
                        "Leader": GRID_DATA.get(str(l_d), {}).get(str(w_d), "??"), "Potential": pay
                    })
        except: pass
        current += timedelta(days=1)
        
    # Sort the final games list purely by the exact UTC timestamp before returning
    final_games.sort(key=lambda x: x.get('GameTime', 0))
    return final_games, live_games

# --- 4. UI DISPLAY ---
st.title("🏀 Shelly's 2026 Box Pool Tracker")
final_data, live_data = fetch_tournament_data()

# LEADERBOARD
if final_data:
    st.header("🏆 Cumulative Standings")
    df_f = pd.DataFrame(final_data)
    lead = df_f.groupby("Winner").agg(Wins=('Winner','count'), Total=('Payout','sum')).sort_values("Total", ascending=False).reset_index()
    lead['Total'] = lead['Total'].map('${:,.0f}'.format)
    st.dataframe(lead, use_container_width=True, hide_index=True)

# LIVE TRACKER
if live_data:
    st.header("⏳ Live Games")
    for g in live_data:
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"**{g['Matchup']}**")
            # Added Tip-off time here
            c1.write(f"{g['Score']} | {g['Time']} (Tip-off: {g['DisplayTime']} ET)")
            c2.metric("Leader", g['Leader'], f"${g['Potential']}")

# GAME HISTORY
if final_data:
    st.divider()
    st.header("📜 Game History")
    for g in final_data:
        # Added the DisplayTime so users can see exactly when the game started
        with st.expander(f"**{g['Winner']}** won **${g['Payout']}** — {g['Matchup']} ({g['Result']})", expanded=False):
            st.write(f"**Tip-off:** {g['Date']} at {g['DisplayTime']} ET ({g['Round']})")
            st.write(f"**Final Score:** {g['Result']} (Winner:{g['W']} Loser:{g['L']})")

# STATISTICS & GRID
if final_data:
    st.divider()
    st.header("📈 Tournament Statistics & Expected Value")
    
    # Mathematical Variables for EV
    games_played = len(final_data)
    awarded_prizes = sum(g['Payout'] for g in final_data)
    remaining_pool = TOTAL_PRIZE_POOL - awarded_prizes
    
    win_digits = [g['W'] for g in final_data]
    lose_digits = [g['L'] for g in final_data]
    
    win_counts = pd.Series(win_digits).value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    lose_counts = pd.Series(lose_digits).value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    
    max_w = win_counts.max() or 1
    mid_w = win_counts.median() or (max_w / 2)
    max_l = lose_counts.max() or 1
    mid_l = lose_counts.median() or (max_l / 2)
    
    st.write(f"**Games Finished:** {games_played} / 63")
    st.write(f"**Prize Pool Remaining:** ${remaining_pool:,.2f}")
    
    st.subheader("🔥 Fire & ❄️ Ice Digits")
    
    st.markdown("##### Winner Team Score")
    w_sorted = win_counts.sort_values(ascending=False)
    col1, col2 = st.columns(2)
    with col1:
        html_h = "<div style='display:flex; gap:8px; flex-wrap:wrap;'>"
        for digit, count in w_sorted.head(5).items():
            bg, tx = get_stretched_gradient(count, max_w, mid_w)
            html_h += f"<div style='background:{bg}; color:{tx}; padding:8px 12px; border-radius:6px; border:1px solid rgba(128,128,128,0.3);'><b>{digit}</b> ({count})</div>"
        html_h += "</div>"
        st.markdown(html_h, unsafe_allow_html=True)
    with col2:
        html_c = "<div style='display:flex; gap:8px; flex-wrap:wrap;'>"
        for digit, count in w_sorted.tail(5).items():
            bg, tx = get_stretched_gradient(count, max_w, mid_w)
            html_c += f"<div style='background:{bg}; color:{tx}; padding:8px 12px; border-radius:6px; border:1px solid rgba(128,128,128,0.3);'><b>{digit}</b> ({count})</div>"
        html_c += "</div>"
        st.markdown(html_c, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### Loser Team Score")
    l_sorted = lose_counts.sort_values(ascending=False)
    col3, col4 = st.columns(2)
    with col3:
        html_h = "<div style='display:flex; gap:8px; flex-wrap:wrap;'>"
        for digit, count in l_sorted.head(5).items():
            bg, tx = get_stretched_gradient(count, max_l, mid_l)
            html_h += f"<div style='background:{bg}; color:{tx}; padding:8px 12px; border-radius:6px; border:1px solid rgba(128,128,128,0.3);'><b>{digit}</b> ({count})</div>"
        html_h += "</div>"
        st.markdown(html_h, unsafe_allow_html=True)
    with col4:
        html_c = "<div style='display:flex; gap:8px; flex-wrap:wrap;'>"
        for digit, count in l_sorted.tail(5).items():
            bg, tx = get_stretched_gradient(count, max_l, mid_l)
            html_c += f"<div style='background:{bg}; color:{tx}; padding:8px 12px; border-radius:6px; border:1px solid rgba(128,128,128,0.3);'><b>{digit}</b> ({count})</div>"
        html_c += "</div>"
        st.markdown(html_c, unsafe_allow_html=True)

    # GRID
    st.subheader("🔥 Expected Value (EV) Heatmap")
    
    with st.expander("ℹ️ What does 'Est: $' mean? (Click to read)"):
        st.write("""
        This is the mathematically projected final value of your box. It takes the money you have *already won* and adds your expected future winnings. Future winnings are estimated dynamically by looking at the current tournament hit rate of your Winner Digit multiplied by the hit rate of your Loser Digit, applied to the remaining unawarded prize pool. *(Note: We use statistical "smoothing" so that even if a number hasn't hit yet, it never drops to a 0% probability—keeping everyone's board alive!)*
        """)
    
    heatmap_wins = pd.DataFrame(0, index=LOSER_AXIS, columns=WINNER_AXIS)
    for g in final_data: heatmap_wins.at[g['L'], g['W']] += 1
    max_win = heatmap_wins.max().max() or 1
    mid_win = heatmap_wins[heatmap_wins > 0].median().median() if not heatmap_wins[heatmap_wins > 0].empty else 0.5

    html_grid = """
    <style>
        .grid-container { overflow-x: auto; margin-top: 10px; border-radius: 8px; }
        .mm-table { width: 100%; min-width: 900px; border-collapse: collapse; font-family: sans-serif; font-size: 0.8rem; }
        .mm-table td, .mm-table th { border: 1px solid rgba(128,128,128,0.3); padding: 10px; text-align: center; vertical-align: middle; }
        .header-main { background-color: #31333F; color: white; font-weight: bold; text-transform: uppercase; border: none !important; }
        .side-label { background-color: #31333F !important; color: white !important; font-weight: bold; writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); width: 45px; text-transform: uppercase; border: none !important; }
    </style>
    <div class='grid-container'><table class='mm-table'>
    """

    html_grid += "<tr><td colspan='2' style='border:none;'></td><td colspan='10' class='header-main'>GAME WINNER</td></tr>"
    html_grid += "<tr><td colspan='2' style='border:none;'></td>"
    for i in WINNER_AXIS:
        bg, tx = get_stretched_gradient(win_counts[i], max_w, mid_w)
        html_grid += f"<td style='background:{bg}; color:{tx}; font-weight:bold;'>{i}</td>"
    html_grid += "</tr>"

    for idx, r in enumerate(LOSER_AXIS):
        html_grid += "<tr>"
        if idx == 0: html_grid += f"<td rowspan='10' class='side-label'>GAME LOSER</td>"
        bg_l, tx_l = get_stretched_gradient(lose_counts[r], max_l, mid_l)
        html_grid += f"<td style='background:{bg_l}; color:{tx_l}; font-weight:bold;'>{r}</td>"
        
        for c in WINNER_AXIS:
            wins = heatmap_wins.at[r, c]
            bg_cell, tx_cell = get_stretched_gradient(wins, max_win, mid_win) if wins > 0 else ("rgba(128,128,128,0.05)", "inherit")
            owner = GRID_DATA.get(str(r), {}).get(str(c), "??")
            
            # --- EV Calculation with Laplace Smoothing ---
            if games_played > 0:
                p_win = (win_counts[c] + 1) / (games_played + 10)
                p_lose = (lose_counts[r] + 1) / (games_played + 10)
                p_box = p_win * p_lose
                projected_future_value = p_box * remaining_pool
            else:
                projected_future_value = remaining_pool / 100 
                
            current_earned = sum(g['Payout'] for g in final_data if g['W'] == c and g['L'] == r)
            total_ev = current_earned + projected_future_value
            
            html_grid += f"<td style='background:{bg_cell}; color:{tx_cell}; min-width:85px; height:60px;'>"
            html_grid += f"<b>{owner}</b>"
            if wins > 0:
                win_label = "Win" if wins == 1 else "Wins"
                html_grid += f"<br><span style='font-size: 0.65rem; opacity: 0.8;'>({wins} {win_label})</span>"
            
            html_grid += f"<br><span style='color: #2e7d32; font-size: 0.85rem; font-weight: 800;'>Est: ${total_ev:.2f}</span>"
            
            html_grid += "</td>"
        html_grid += "</tr>"
    html_grid += "</table></div>"
    st.markdown(html_grid, unsafe_allow_html=True)

if st.button('Update Scores'):
    st.cache_data.clear()
    st.rerun()
