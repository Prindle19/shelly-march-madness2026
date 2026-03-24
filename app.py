import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURATION & POOL SETUP ---
st.set_page_config(page_title="2026 Box Pool Tracker", page_icon="🏀", layout="centered")
st_autorefresh(interval=60000, limit=None, key="hoops_refresh")

HISTORICAL_PROBS = {
    '0': 0.11, '1': 0.13, '2': 0.11, '3': 0.10, '4': 0.09,
    '5': 0.12, '6': 0.09, '7': 0.09, '8': 0.09, '9': 0.07
}

POOLS = {
    "Shelly": {
        "TITLE": "🏀 Shelly's 2026 Box Pool Tracker",
        "START_DATE": datetime(2026, 3, 19),
        "TOTAL_POOL": 9500,
        "EST_EVENTS": 63,
        "WINNER_AXIS": ['3', '2', '1', '6', '8', '9', '5', '0', '7', '4'],
        "LOSER_AXIS": ['8', '7', '3', '0', '4', '2', '9', '5', '1', '6'],
        "GRID_DATA": {
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
        },
        "SCHEDULE": {
            "20260319": "1st Round", "20260320": "1st Round",
            "20260321": "2nd Round", "20260322": "2nd Round",
            "20260326": "Sweet 16",  "20260327": "Sweet 16",
            "20260328": "Elite 8",   "20260329": "Elite 8",
            "20260404": "Final 4",   "20260406": "Championship Final"
        },
        "PAYOUTS": {
            "1st Round": [{"type": "Final", "amount": 50}],
            "2nd Round": [{"type": "Final", "amount": 100}],
            "Sweet 16": [{"type": "Final", "amount": 200}],
            "Elite 8": [{"type": "Final", "amount": 400}],
            "Final 4": [{"type": "Final", "amount": 800}],
            "Championship Final": [{"type": "Final", "amount": 1500}]
        }
    },
    
    "MRYC": {
        "TITLE": "🏀 MRYC 2026 Box Pool Tracker",
        "START_DATE": datetime(2026, 3, 26), # Starts directly at the Sweet 16
        "TOTAL_POOL": 1000,
        "EST_EVENTS": 17, # 8 + 4 + 2 + 3 payout events
        "WINNER_AXIS": ['8','7','0','1','5','2','3','6','9','4'],
        "LOSER_AXIS": ['5','9','8','3','0','2','1','4','7','6'],
        "GRID_DATA": {
            '0': {'8': 'Scott Kennedy', '7': 'Wohltman', '0': 'Dave Johnson', '1': 'Kelly Kenneally', '5': 'Maggy G', '2': 'Aaron Feldman', '3': 'Kathleen Trombly', '6': 'Bonavita', '9': 'Chris DeFuria', '4': 'Beth Baccaro'},
            '1': {'8': 'McEneny', '7': 'Kim Boedart Barry', '0': 'Evertt Tatarski', '1': 'Trombly Family', '5': 'Huch', '2': 'Pat Dennin', '3': 'A&D Schuett', '6': 'Harry Tatarski', '9': 'Nick Mills', '4': 'Alex Sporviero'},
            '2': {'8': 'K&C Laufer', '7': 'Wilder H', '0': 'Elisabth Finkenauer', '1': 'Huch', '5': 'Dawn Harriman', '2': 'Bob Fahey', '3': 'Logan Mills', '6': 'Isla Eastmond', '9': 'Fogarty', '4': 'Scala'},
            '3': {'8': 'Bob Fahey', '7': 'Polesky G&K', '0': 'Sheila Gonzalez', '1': 'Gina Kennedy', '5': 'George Polesky', '2': 'Todd Eastmond', '3': 'Wohltman', '6': 'Dave Leone', '9': 'Maggy G', '4': 'McEneny'},
            '4': {'8': 'Baglieri', '7': 'Fogarty', '0': 'Lexi Mills', '1': 'Baglieri', '5': 'Peter Gonzalez', '2': 'Bonavita', '3': 'Scott Kennedy', '6': 'Bob Crines', '9': 'Wohltman', '4': 'Baglieri'},
            '5': {'8': 'Aaaron Feldman', '7': 'Nina Tatarski', '0': 'Shayned Eastmond', '1': 'Kelly Kenneally', '5': 'Bart Dennin', '2': 'Rob Zebrowski', '3': 'Brown / Kernan', '6': 'Marty Barry', '9': 'Gina Kennedy (Julie)', '4': 'Baglieri'},
            '6': {'8': 'Gienna Kennedy Claudrex', '7': 'Tom McManis', '0': 'Alex Sproviero', '1': 'Scott Bilby', '5': 'Wohltman', '2': 'McEneny', '3': 'Brown / Kernan', '6': 'Polesky G&K', '9': 'Beth Baccarro', '4': 'K&C Laufer'},
            '7': {'8': 'Brown / Kernan', '7': 'Scala', '0': 'Rob Zebrowski', '1': 'Kelly Eastmond', '5': 'Mike Trom', '2': 'Chris DeFuria', '3': 'Baglieri', '6': 'Scott Bilby', '9': 'Trombly Family', '4': 'Tom McManis'},
            '8': {'8': 'Maggy G', '7': 'Bonavita', '0': 'Mike Trom', '1': 'Liz Mills', '5': 'Charlie Leone', '2': 'Joe Tatarski', '3': 'Dave Johnson', '6': 'Mike Trom', '9': 'Trish Brown', '4': 'Alex Sporviero'},
            '9': {'8': 'Kat Polesky', '7': 'Hank Trost', '0': 'Trish Brown', '1': 'Laura Leone', '5': 'Baglieri', '2': 'T.R & Darlens', '3': 'G Huch', '6': 'Kathleen Tombly', '9': 'Dawn Harriman', '4': 'Brown / Kernan'}
        }, 
        "SCHEDULE": {
            "20260326": "Sweet 16",  "20260327": "Sweet 16",
            "20260328": "Elite 8",   "20260329": "Elite 8",
            "20260404": "Final 4",   "20260406": "Championship Final"
        },
        "PAYOUTS": {
            "Sweet 16": [{"type": "Final", "amount": 25}],
            "Elite 8": [{"type": "Final", "amount": 75}],
            "Final 4": [{"type": "Final", "amount": 100}],
            "Championship Final": [
                {"type": "Halftime", "amount": 50},
                {"type": "Reverse", "amount": 50},
                {"type": "Final", "amount": 200}
            ]
        }
    }
}

# --- DYNAMIC INITIATION VIA STREAMLIT SECRETS ---
# Reads the 'POOL_ID' secret from the cloud deployment. Defaults to "Shelly" if none exists.
active_pool_id = st.secrets.get("POOL_ID", "Shelly")
config = POOLS[active_pool_id]

# --- 2. DYNAMIC COLOR ENGINE ---
def get_stretched_gradient(val, mx, mid):
    if val == mid: return "rgba(128, 128, 128, 0.2)", "inherit"
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
def fetch_tournament_data(pool_config):
    tz = pytz.timezone('US/Eastern')
    start_date = tz.localize(pool_config["START_DATE"])
    end_date = datetime.now(tz)
    final_payout_events, live_games = [], []
    current = start_date
    
    while current <= end_date:
        d_str = current.strftime("%Y%m%d")
        rnd_name = pool_config["SCHEDULE"].get(d_str)
        
        # Skip dates not in this specific pool's schedule
        if not rnd_name:
            current += timedelta(days=1)
            continue
            
        payout_rules = pool_config["PAYOUTS"].get(rnd_name, [])
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={d_str}"
        
        try:
            data = requests.get(url).json()
            for ev in data.get('events', []):
                status = ev['status']['type']['name']
                comp = ev['competitions'][0]
                h = next(t for t in comp['competitors'] if t['homeAway'] == 'home')
                a = next(t for t in comp['competitors'] if t['homeAway'] == 'away')
                h_s, a_s = int(h['score']), int(a['score'])
                
                h_half = int(h['linescores'][0]['value']) if 'linescores' in h and len(h['linescores']) > 0 else 0
                a_half = int(a['linescores'][0]['value']) if 'linescores' in a and len(a['linescores']) > 0 else 0
                
                h_disp = f"({h.get('curatedRank', {}).get('current', 99)}) {h['team']['shortDisplayName']}" if h.get('curatedRank', {}).get('current', 99) <= 16 else h['team']['shortDisplayName']
                a_disp = f"({a.get('curatedRank', {}).get('current', 99)}) {a['team']['shortDisplayName']}" if a.get('curatedRank', {}).get('current', 99) <= 16 else a['team']['shortDisplayName']
                
                w_d, l_d = (h_s % 10, a_s % 10) if h_s > a_s else (a_s % 10, h_s % 10)
                w_half_d, l_half_d = (h_half % 10, a_half % 10) if h_half > a_half else (a_half % 10, h_half % 10)
                
                dt_est = pd.to_datetime(ev.get('date')).tz_convert('US/Eastern') if ev.get('date') else None
                sort_time = dt_est.timestamp() if dt_est else 0
                display_time = dt_est.strftime("%I:%M %p").lstrip('0') if dt_est else "TBD"

                if "STATUS_FINAL" in status and payout_rules:
                    for rule in payout_rules:
                        p_type, pay = rule["type"], rule["amount"]
                        
                        if p_type == "Final":
                            win_digit, lose_digit, result_str = w_d, l_d, f"{a_s}-{h_s}"
                        elif p_type == "Halftime":
                            win_digit, lose_digit, result_str = w_half_d, l_half_d, f"{a_half}-{h_half} (Half)"
                        elif p_type == "Reverse":
                            win_digit, lose_digit, result_str = l_d, w_d, f"{a_s}-{h_s} (Reverse)"
                            
                        owner = pool_config['GRID_DATA'].get(str(lose_digit), {}).get(str(win_digit), "??")
                        
                        final_payout_events.append({
                            "Winner": owner, "Payout": pay, "W": str(win_digit), "L": str(lose_digit),
                            "Date": current.strftime("%m/%d"), "GameTime": sort_time, "DisplayTime": display_time,
                            "Matchup": f"{a_disp} @ {h_disp}", "Result": result_str, 
                            "Round": rnd_name, "Type": p_type
                        })
                        
                elif ("STATUS_IN_PROGRESS" in status or "STATUS_HALFTIME" in status) and payout_rules:
                    live_games.append({
                        "Matchup": f"{a_disp} @ {h_disp}", "Score": f"{a_s}-{h_s}",
                        "Time": ev['status']['type']['shortDetail'], "DisplayTime": display_time, "GameTime": sort_time,
                        "Leader": pool_config['GRID_DATA'].get(str(l_d), {}).get(str(w_d), "??"), 
                        "Potential": sum(r['amount'] for r in payout_rules if r['type'] == 'Final') 
                    })
        except: pass
        current += timedelta(days=1)
        
    final_payout_events.sort(key=lambda x: x.get('GameTime', 0))
    live_games.sort(key=lambda x: x.get('GameTime', 0))
    return final_payout_events, live_games

# --- 4. UI DISPLAY ---
st.title(config["TITLE"])
final_data, live_data = fetch_tournament_data(config)

if final_data:
    st.header("🏆 Cumulative Standings")
    df_f = pd.DataFrame(final_data)
    lead = df_f.groupby("Winner").agg(Hits=('Winner','count'), Total=('Payout','sum')).sort_values("Total", ascending=False).reset_index()
    lead['Total'] = lead['Total'].map('${:,.0f}'.format)
    st.dataframe(lead, use_container_width=True, hide_index=True)

if live_data:
    st.header("⏳ Live Games")
    for g in live_data:
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"**{g['Matchup']}**")
            c1.write(f"{g['Score']} | {g['Time']} (Tip-off: {g['DisplayTime']} ET)")
            c2.metric("Current Leader", g['Leader'], f"${g['Potential']}")

if final_data:
    st.divider()
    st.header("📜 Payout History")
    for g in reversed(final_data):
        type_badge = f"🔄 {g['Type']}" if g['Type'] in ['Reverse', 'Halftime'] else f"✅ {g['Type']}"
        with st.expander(f"**{g['Winner']}** won **${g['Payout']}** — {g['Matchup']} | {type_badge}", expanded=False):
            st.write(f"**Tip-off:** {g['Date']} at {g['DisplayTime']} ET ({g['Round']})")
            st.write(f"**Score Context:** {g['Result']} (Win Digit: {g['W']} | Lose Digit: {g['L']})")

if True: 
    st.divider()
    st.header("📈 Heatmap & Expected Value")
    
    events_played = len(final_data)
    awarded_prizes = sum(g['Payout'] for g in final_data)
    remaining_pool = config["TOTAL_POOL"] - awarded_prizes
    
    win_digits, lose_digits = [g['W'] for g in final_data], [g['L'] for g in final_data]
    win_counts = pd.Series(win_digits).value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    lose_counts = pd.Series(lose_digits).value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    
    max_w, mid_w = win_counts.max() or 1, win_counts.median() or (win_counts.max() / 2)
    max_l, mid_l = lose_counts.max() or 1, lose_counts.median() or (lose_counts.max() / 2)
    
    st.write(f"**Total Prize Pool Remaining:** ${remaining_pool:,.2f}")

    with st.expander("ℹ️ What does 'Est: $' mean? (Click to read)"):
        st.write("This is the mathematically projected final value of your box. It adds your current winnings to your expected future winnings. Future winnings are calculated by dynamically blending Historical NCAA Probabilities with the Current Tournament Hit Rates as more games are played.")
    
    heatmap_wins = pd.DataFrame(0, index=config["LOSER_AXIS"], columns=config["WINNER_AXIS"])
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
    for i in config["WINNER_AXIS"]:
        bg, tx = get_stretched_gradient(win_counts[i], max_w, mid_w)
        html_grid += f"<td style='background:{bg}; color:{tx}; font-weight:bold;'>{i}</td>"
    html_grid += "</tr>"

    for idx, r in enumerate(config["LOSER_AXIS"]):
        html_grid += "<tr>"
        if idx == 0: html_grid += f"<td rowspan='10' class='side-label'>GAME LOSER</td>"
        bg_l, tx_l = get_stretched_gradient(lose_counts[r], max_l, mid_l)
        html_grid += f"<td style='background:{bg_l}; color:{tx_l}; font-weight:bold;'>{r}</td>"
        
        for c in config["WINNER_AXIS"]:
            wins = heatmap_wins.at[r, c]
            bg_cell, tx_cell = get_stretched_gradient(wins, max_win, mid_win) if wins > 0 else ("rgba(128,128,128,0.05)", "inherit")
            owner = config['GRID_DATA'].get(str(r), {}).get(str(c), "??")
            
            # --- EV Calculation with Dynamic Blending ---
            weight_current = min(events_played / config["EST_EVENTS"], 1.0)
            weight_hist = 1.0 - weight_current
            
            p_win_current = win_counts[c] / events_played if events_played > 0 else 0
            p_win_blended = (p_win_current * weight_current) + (HISTORICAL_PROBS[c] * weight_hist)
            
            p_lose_current = lose_counts[r] / events_played if events_played > 0 else 0
            p_lose_blended = (p_lose_current * weight_current) + (HISTORICAL_PROBS[r] * weight_hist)
            
            p_box = p_win_blended * p_lose_blended
            projected_future_value = p_box * remaining_pool
                
            current_earned = sum(g['Payout'] for g in final_data if g['W'] == c and g['L'] == r)
            total_ev = current_earned + projected_future_value
            
            html_grid += f"<td style='background:{bg_cell}; color:{tx_cell}; min-width:85px; height:60px;'>"
            html_grid += f"<b>{owner}</b>"
            if wins > 0: html_grid += f"<br><span style='font-size: 0.65rem; opacity: 0.8;'>({wins} Hits)</span>"
            html_grid += f"<br><span style='font-size: 0.85rem; font-weight: 800;'>Est: ${total_ev:.2f}</span>"
            html_grid += "</td>"
        html_grid += "</tr>"
    html_grid += "</table></div>"
    st.markdown(html_grid, unsafe_allow_html=True)
