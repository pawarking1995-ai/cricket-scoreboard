import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Cricket Scoreboard Manager Pro", layout="wide")

st.title("🏏 Cricket Scoreboard Manager Pro (Web Version)")

# Initialize Global Session States
if 'inning' not in st.session_state: st.session_state.inning = 1
if 'target' not in st.session_state: st.session_state.target = 0

# Innings 1 State Initialization
if 'i1_runs' not in st.session_state: st.session_state.i1_runs = 0
if 'i1_wickets' not in st.session_state: st.session_state.i1_wickets = 0
if 'i1_balls' not in st.session_state: st.session_state.i1_balls = 0
if 'i1_overs' not in st.session_state: st.session_state.i1_overs = 0
if 'i1_extras' not in st.session_state: st.session_state.i1_extras = 0
if 'i1_fours' not in st.session_state: st.session_state.i1_fours = 0
if 'i1_sixes' not in st.session_state: st.session_state.i1_sixes = 0
if 'i1_history' not in st.session_state: st.session_state.i1_history = []

# Innings 2 State Initialization
if 'i2_runs' not in st.session_state: st.session_state.i2_runs = 0
if 'i2_wickets' not in st.session_state: st.session_state.i2_wickets = 0
if 'i2_balls' not in st.session_state: st.session_state.i2_balls = 0
if 'i2_overs' not in st.session_state: st.session_state.i2_overs = 0
if 'i2_extras' not in st.session_state: st.session_state.i2_extras = 0
if 'i2_fours' not in st.session_state: st.session_state.i2_fours = 0
if 'i2_sixes' not in st.session_state: st.session_state.i2_sixes = 0
if 'i2_history' not in st.session_state: st.session_state.i2_history = []

# Sidebar for Team & Match Setup
st.sidebar.header("⚙ Match Setup & Logos")
team1 = st.sidebar.text_input("Team A Name", "AUS")
team1_logo = st.sidebar.file_uploader(f"Upload {team1} Logo", type=["png", "jpg", "jpeg"], key="t1_logo")

team2 = st.sidebar.text_input("Team B Name", "PAK")
team2_logo = st.sidebar.file_uploader(f"Upload {team2} Logo", type=["png", "jpg", "jpeg"], key="t2_logo")

match_overs = st.sidebar.number_input("Total Match Overs", min_value=1, max_value=50, value=5)

st.sidebar.markdown("---")
st.sidebar.header("🪙 Toss Decision")
toss_winner = st.sidebar.selectbox("Who won the Toss?", [team1, team2])
toss_decision = st.sidebar.selectbox("Toss Decision", ["Batting", "Bowling"])

# Determine 1st and 2nd Innings batting teams based on Toss
if toss_winner == team1:
    i1_bat = team1 if toss_decision == "Batting" else team2
    i1_bowl = team2 if toss_decision == "Batting" else team1
else:
    i1_bat = team2 if toss_decision == "Batting" else team1
    i1_bowl = team1 if toss_decision == "Batting" else team2

i2_bat = i1_bowl
i2_bowl = i1_bat

st.session_state.i1_batting = i1_bat
st.session_state.i1_bowling = i1_bowl
st.session_state.i2_batting = i2_bat
st.session_state.i2_bowling = i2_bowl

batting_team = i1_bat if st.session_state.inning == 1 else i2_bat
bowling_team = i1_bowl if st.session_state.inning == 1 else i2_bowl

st.sidebar.markdown("---")
st.sidebar.header("👥 Player Squads (Top 5+)")
default_squad_1 = ", ".join([f"Player {i}" for i in range(1, 12)])
default_squad_2 = ", ".join([f"Player {chr(65+i)}" for i in range(11)])

team1_players_input = st.sidebar.text_area(f"{team1} Players (Comma separated)", default_squad_1)
team2_players_input = st.sidebar.text_area(f"{team2} Players (Comma separated)", default_squad_2)

team1_players = [p.strip() for p in team1_players_input.split(",") if p.strip()]
team2_players = [p.strip() for p in team2_players_input.split(",") if p.strip()]

batting_squad_1 = team1_players if i1_bat == team1 else team2_players
bowling_squad_1 = team2_players if i1_bowl == team2 else team1_players

batting_squad_2 = team1_players if i2_bat == team1 else team2_players
bowling_squad_2 = team2_players if i2_bowl == team2 else team1_players

# Initialize 1st Innings Scorecards (Top 5 Batters, Top 5 Bowlers)
if 'i1_batting_df' not in st.session_state:
    st.session_state.i1_batting_df = pd.DataFrame({
        "Batsman": batting_squad_1[:5] if len(batting_squad_1) >= 5 else batting_squad_1 + [""]*(5-len(batting_squad_1)),
        "Runs": [0]*5,
        "Balls": [0]*5,
        "4s": [0]*5,
        "6s": [0]*5,
        "SR": [0.0]*5
    })

if 'i1_bowling_df' not in st.session_state:
    st.session_state.i1_bowling_df = pd.DataFrame({
        "Bowler": bowling_squad_1[:5] if len(bowling_squad_1) >= 5 else bowling_squad_1 + [""]*(5-len(bowling_squad_1)),
        "Overs": [0.0]*5,
        "Dots": [0]*5,
        "Runs": [0]*5,
        "Wickets": [0]*5,
        "Economy": [0.0]*5
    })

# Initialize 2nd Innings Scorecards
if 'i2_batting_df' not in st.session_state:
    st.session_state.i2_batting_df = pd.DataFrame({
        "Batsman": batting_squad_2[:5] if len(batting_squad_2) >= 5 else batting_squad_2 + [""]*(5-len(batting_squad_2)),
        "Runs": [0]*5,
        "Balls": [0]*5,
        "4s": [0]*5,
        "6s": [0]*5,
        "SR": [0.0]*5
    })

if 'i2_bowling_df' not in st.session_state:
    st.session_state.i2_bowling_df = pd.DataFrame({
        "Bowler": bowling_squad_2[:5] if len(bowling_squad_2) >= 5 else bowling_squad_2 + [""]*(5-len(bowling_squad_2)),
        "Overs": [0.0]*5,
        "Dots": [0]*5,
        "Runs": [0]*5,
        "Wickets": [0]*5,
        "Economy": [0.0]*5
    })

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Match Score"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Dynamic Mapping for Current Inning
curr = st.session_state.inning
runs = st.session_state.i1_runs if curr == 1 else st.session_state.i2_runs
wickets = st.session_state.i1_wickets if curr == 1 else st.session_state.i2_wickets
balls = st.session_state.i1_balls if curr == 1 else st.session_state.i2_balls
overs = st.session_state.i1_overs if curr == 1 else st.session_state.i2_overs
extras = st.session_state.i1_extras if curr == 1 else st.session_state.i2_extras
fours = st.session_state.i1_fours if curr == 1 else st.session_state.i2_fours
sixes = st.session_state.i1_sixes if curr == 1 else st.session_state.i2_sixes
history = st.session_state.i1_history if curr == 1 else st.session_state.i2_history

def update_curr(r, w, b, o, e, f, s):
    if curr == 1:
        st.session_state.i1_runs = r
        st.session_state.i1_wickets = w
        st.session_state.i1_balls = b
        st.session_state.i1_overs = o
        st.session_state.i1_extras = e
        st.session_state.i1_fours = f
        st.session_state.i1_sixes = s
    else:
        st.session_state.i2_runs = r
        st.session_state.i2_wickets = w
        st.session_state.i2_balls = b
        st.session_state.i2_overs = o
        st.session_state.i2_extras = e
        st.session_state.i2_fours = f
        st.session_state.i2_sixes = s

def save_history():
    history.append({'runs': runs, 'wickets': wickets, 'balls': balls, 'overs': overs, 'extras': extras, 'fours': fours, 'sixes': sixes})

def add_ball_logic(is_legal=True):
    b = balls
    o = overs
    if is_legal:
        b += 1
        if b == 6:
            o += 1
            b = 0
    return b, o

# Display Logos and Header Stats
col_l1, col_title, col_l2 = st.columns([1, 4, 1])
with col_l1:
    if team1_logo:
        st.image(Image.open(team1_logo), width=80)
    else:
        st.markdown(f"**{team1}**")

with col_title:
    st.subheader(f"📍 Innings {curr}: {batting_team} (Batting) vs {bowling_team} (Bowling)")
    st.info(f"🪙 **Toss:** {toss_winner} won the toss and elected to **{toss_decision}** first.")

with col_l2:
    if team2_logo:
        st.image(Image.open(team2_logo), width=80)
    else:
        st.markdown(f"**{team2}**")

# On-field Players Selection
active_batting_squad = batting_squad_1 if curr == 1 else batting_squad_2
active_bowling_squad = bowling_squad_1 if curr == 1 else bowling_squad_2

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    striker = st.selectbox("🏏 Striker", active_batting_squad if active_batting_squad else ["No Players"])
with col_p2:
    non_striker = st.selectbox("🏃 Non-Striker", active_batting_squad if active_batting_squad else ["No Players"])
with col_p3:
    current_bowler = st.selectbox("⚾ Current Bowler", active_bowling_squad if active_bowling_squad else ["No Players"])

if curr == 2:
    runs_needed = st.session_state.target - runs
    total_legal_balls = (match_overs * 6) - (overs * 6 + balls)
    if runs_needed <= 0:
        st.success(f"🎉 **{batting_team} Won the Match by chasing the target!**")
    elif wickets >= 10 or total_legal_balls <= 0:
        if runs < st.session_state.target - 1:
            st.error(f"🏁 **Match Ended! {bowling_team} Won the Match!**")
        else:
            st.warning(f"🤝 **Match Tied!**")
    else:
        st.warning(f"🎯 **Target:** {st.session_state.target} | **Need {runs_needed} runs** in {total_legal_balls} balls")

total_ov_float = overs + (balls / 6.0)
crr = f"{runs / total_ov_float:.2f}" if total_ov_float > 0 else "0.00"

st.markdown("---")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Score", f"{runs}/{wickets}")
col2.metric("Overs", f"{overs}.{balls}")
col3.metric("CRR", crr)
col4.metric("Extras", extras)
col5.metric("4s", fours)
col6.metric("6s", sixes)

st.markdown("---")

# Scoring Controls
st.subheader("🎮 Live Scoring Controls")

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    if st.button("0 Run (Dot)"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs, wickets, nb, no, extras, fours, sixes)
        st.rerun()
with c2:
    if st.button("+1 Run"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs + 1, wickets, nb, no, extras, fours, sixes)
        st.rerun()
with c3:
    if st.button("+2 Runs"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs + 2, wickets, nb, no, extras, fours, sixes)
        st.rerun()
with c4:
    if st.button("+3 Runs"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs + 3, wickets, nb, no, extras, fours, sixes)
        st.rerun()
with c5:
    if st.button("🔥 4 Runs"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs + 4, wickets, nb, no, extras, fours+1, sixes)
        st.rerun()
with c6:
    if st.button("🚀 6 Runs"):
        save_history()
        nb, no = add_ball_logic(True)
        update_curr(runs + 6, wickets, nb, no, extras, fours, sixes+1)
        st.rerun()
with c7:
    if st.button("↩️ Undo"):
        if history:
            last = history.pop()
            update_curr(last['runs'], last['wickets'], last['balls'], last['overs'], last['extras'], last['fours'], last['sixes'])
            st.success("Last action undone!")
            st.rerun()
        else:
            st.warning("Nothing to undo!")

st.markdown("### Extras & Wickets")
e1, e2, e3 = st.columns(3)

with e1:
    if st.button("Wide (+1 Extra)"):
        save_history()
        update_curr(runs + 1, wickets, balls, overs, extras + 1, fours, sixes)
        st.rerun()
with e2:
    if st.button("No Ball (+1 Extra)"):
        save_history()
        update_curr(runs + 1, wickets, balls, overs, extras + 1, fours, sixes)
        st.rerun()
with e3:
    if st.button("❌ Wicket"):
        save_history()
        if wickets < 10:
            nb, no = add_ball_logic(True)
            update_curr(runs, wickets + 1, nb, no, extras, fours, sixes)
        st.rerun()

# Innings Switch / End Button
st.markdown("---")
if curr == 1:
    if st.button("🏁 End 1st Innings & Start 2nd Innings"):
        st.session_state.target = runs + 1
        st.session_state.inning = 2
        st.rerun()

# 1st Innings Detailed Scorecards (Top 5 Batters & Bowlers)
if curr == 1 or st.session_state.get('i1_runs', 0) > 0:
    st.markdown("---")
    st.subheader(f"📊 1st Innings Scorecard: {i1_bat} (Batting) vs {i1_bowl} (Bowling)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown(f"#### 🏏 {i1_bat} - Top 5 Batting")
        st.session_state.i1_batting_df['SR'] = st.session_state.i1_batting_df.apply(
            lambda row: round((row['Runs'] / row['Balls']) * 100, 2) if row['Balls'] > 0 else 0.0, axis=1
        )
        st.session_state.i1_batting_df = st.data_editor(st.session_state.i1_batting_df, key="bat_1", num_rows="fixed")
    with col_b2:
        st.markdown(f"#### ⚾ {i1_bowl} - Bowling")
        st.session_state.i1_bowling_df['Economy'] = st.session_state.i1_bowling_df.apply(
            lambda row: round(row['Runs'] / row['Overs'], 2) if row['Overs'] > 0 else 0.0, axis=1
        )
        st.session_state.i1_bowling_df = st.data_editor(st.session_state.i1_bowling_df, key="bowl_1", num_rows="fixed")

# 2nd Innings Detailed Scorecards (Top 5 Batters & Bowlers)
if curr == 2 or st.session_state.get('i2_runs', 0) > 0:
    st.markdown("---")
    st.subheader(f"📊 2nd Innings Scorecard: {i2_bat} (Batting) vs {i2_bowl} (Bowling)")
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        st.markdown(f"#### 🏏 {i2_bat} - Top 5 Batting")
        st.session_state.i2_batting_df['SR'] = st.session_state.i2_batting_df.apply(
            lambda row: round((row['Runs'] / row['Balls']) * 100, 2) if row['Balls'] > 0 else 0.0, axis=1
        )
        st.session_state.i2_batting_df = st.data_editor(st.session_state.i2_batting_df, key="bat_2", num_rows="fixed")
    with col_cb2:
        st.markdown(f"#### ⚾ {i2_bowl} - Bowling")
        st.session_state.i2_bowling_df['Economy'] = st.session_state.i2_bowling_df.apply(
            lambda row: round(row['Runs'] / row['Overs'], 2) if row['Overs'] > 0 else 0.0, axis=1
        )
        st.session_state.i2_bowling_df = st.data_editor(st.session_state.i2_bowling_df, key="bowl_2", num_rows="fixed")

# Match Summary Table Section
st.markdown("---")
st.subheader("📋 Match Summary Overview")

i1_ov_f = st.session_state.i1_overs + (st.session_state.i1_balls / 6.0)
i1_crr = f"{st.session_state.i1_runs / i1_ov_f:.2f}" if i1_ov_f > 0 else "0.00"

i2_ov_f = st.session_state.i2_overs + (st.session_state.i2_balls / 6.0)
i2_crr = f"{st.session_state.i2_runs / i2_ov_f:.2f}" if i2_ov_f > 0 else "0.00"

summary_data = [
    {
        "Innings": "1st Innings",
        "Batting Team": st.session_state.i1_batting,
        "Bowling Team": st.session_state.i1_bowling,
        "Score": f"{st.session_state.i1_runs}/{st.session_state.i1_wickets}",
        "Overs": f"{st.session_state.i1_overs}.{st.session_state.i1_balls}",
        "Extras": st.session_state.i1_extras,
        "4s / 6s": f"{st.session_state.i1_fours} / {st.session_state.i1_sixes}",
        "CRR": i1_crr
    },
    {
        "Innings": "2nd Innings",
        "Batting Team": st.session_state.i2_batting,
        "Bowling Team": st.session_state.i2_bowling,
        "Score": f"{st.session_state.i2_runs}/{st.session_state.i2_wickets}",
        "Overs": f"{st.session_state.i2_overs}.{st.session_state.i2_balls}",
        "Extras": st.session_state.i2_extras,
        "4s / 6s": f"{st.session_state.i2_fours} / {st.session_state.i2_sixes}",
        "CRR": i2_crr
    }
]

df_summary = pd.DataFrame(summary_data)
st.table(df_summary)

# Download CSV Button
csv = df_summary.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Complete Match Summary (CSV)",
    data=csv,
    file_name='cricket_match_complete_summary.csv',
    mime='text/csv',
)
