import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Cricket Scoreboard Manager Pro", layout="wide")

# ==========================================
# CUSTOM CSS FOR UNIQUE PER-SECTION COLORS
# ==========================================
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Section 1: Header / Match Info (Deep Blue Gradient) */
    .match-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
        margin-bottom: 20px;
        border: 1px solid #4a90e2;
    }

    /* Section 2: Wicket Details (Dark Red/Crimson Gradient) */
    .wicket-section {
        background: linear-gradient(135deg, #512b2b 0%, #301010 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        margin-bottom: 20px;
        border: 2px solid #ff4b5c;
    }

    /* Section 3: Live Scoring Controls (Emerald/Green Gradient) */
    .scoring-section {
        background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(113, 178, 128, 0.3);
        margin-bottom: 20px;
        border: 1px solid #a8ff78;
    }

    /* Section 4: Scorecards (Purple/Indigo Gradient) */
    .scorecard-section {
        background: linear-gradient(135deg, #2b1055 0%, #7597de 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(117, 151, 222, 0.3);
        margin-bottom: 20px;
        border: 1px solid #99c2ff;
    }

    /* Section 5: Match Summary (Dark Orange/Gold Gradient) */
    .summary-section {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(242, 153, 74, 0.3);
        margin-bottom: 20px;
        color: #000000 !important;
        border: 1px solid #ffe58f;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: rgba(0, 0, 0, 0.3);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    div[data-testid="stMetric"] label { color: #f0f0f0 !important; font-size: 15px !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 26px !important; }
</style>
""", unsafe_allow_html=True)

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
st.sidebar.header("👥 Player Squads (1 to 11)")
default_squad_1 = ", ".join([f"Player {i}" for i in range(1, 12)])
default_squad_2 = ", ".join([f"Player {chr(65+i)}" for i in range(11)])

team1_players_input = st.sidebar.text_area(f"{team1} Players (11 names comma separated)", default_squad_1)
team2_players_input = st.sidebar.text_area(f"{team2} Players (11 names comma separated)", default_squad_2)

team1_players = [p.strip() for p in team1_players_input.split(",") if p.strip()]
team2_players = [p.strip() for p in team2_players_input.split(",") if p.strip()]

batting_squad_1 = team1_players if i1_bat == team1 else team2_players
bowling_squad_1 = team2_players if i1_bowl == team2 else team1_players

batting_squad_2 = team1_players if i2_bat == team1 else team2_players
bowling_squad_2 = team2_players if i2_bowl == team2 else team1_players

# Initialize DataFrames
if 'i1_batting_df' not in st.session_state:
    st.session_state.i1_batting_df = pd.DataFrame({
        "Batsman": batting_squad_1[:11] if len(batting_squad_1) >= 11 else batting_squad_1 + [""]*(11-len(batting_squad_1)),
        "Runs": [0]*11, "Balls": [0]*11, "4s": [0]*11, "6s": [0]*11, "SR": [0.0]*11,
        "How Out / Status": ["Yet to Bat"]*11, "Bowled / Fielder": ["-"]*11
    })

if 'i1_bowling_df' not in st.session_state:
    st.session_state.i1_bowling_df = pd.DataFrame({
        "Bowler": bowling_squad_1[:11] if len(bowling_squad_1) >= 11 else bowling_squad_1 + [""]*(11-len(bowling_squad_1)),
        "Overs": [0.0]*11, "Dots": [0]*11, "Runs": [0]*11, "Wickets": [0]*11, "Economy": [0.0]*11
    })

if 'i2_batting_df' not in st.session_state:
    st.session_state.i2_batting_df = pd.DataFrame({
        "Batsman": batting_squad_2[:11] if len(batting_squad_2) >= 11 else batting_squad_2 + [""]*(11-len(batting_squad_2)),
        "Runs": [0]*11, "Balls": [0]*11, "4s": [0]*11, "6s": [0]*11, "SR": [0.0]*11,
        "How Out / Status": ["Yet to Bat"]*11, "Bowled / Fielder": ["-"]*11
    })

if 'i2_bowling_df' not in st.session_state:
    st.session_state.i2_bowling_df = pd.DataFrame({
        "Bowler": bowling_squad_2[:11] if len(bowling_squad_2) >= 11 else bowling_squad_2 + [""]*(11-len(bowling_squad_2)),
        "Overs": [0.0]*11, "Dots": [0]*11, "Runs": [0]*11, "Wickets": [0]*11, "Economy": [0.0]*11
    })

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Match Score"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

curr = st.session_state.inning
runs = st.session_state.i1_runs if curr == 1 else st.session_state.i2_runs
wickets = st.session_state.i1_wickets if curr == 1 else st.session_state.i2_wickets
balls = st.session_state.i1_balls if curr == 1 else st.session_state.i2_balls
overs = st.session_state.i1_overs if curr == 1 else st.session_state.i2_overs
extras = st.session_state.i1_extras if curr == 1 else st.session_state.i2_extras
fours = st.session_state.i1_fours if curr == 1 else st.session_state.i1_fours
sixes = st.session_state.i1_sixes if curr == 1 else st.session_state.i2_sixes
history = st.session_state.i1_history if curr == 1 else st.session_state.i2_history

def update_curr(r, w, b, o, e, f, s):
    if curr == 1:
        st.session_state.i1_runs = r; st.session_state.i1_wickets = w
        st.session_state.i1_balls = b; st.session_state.i1_overs = o
        st.session_state.i1_extras = e; st.session_state.i1_fours = f
        st.session_state.i1_sixes = s
    else:
        st.session_state.i2_runs = r; st.session_state.i2_wickets = w
        st.session_state.i2_balls = b; st.session_state.i2_overs = o
        st.session_state.i2_extras = e; st.session_state.i2_fours = f
        st.session_state.i2_sixes = s

def save_history():
    history.append({'runs': runs, 'wickets': wickets, 'balls': balls, 'overs': overs, 'extras': extras, 'fours': fours, 'sixes': sixes})

def add_ball_logic(is_legal=True):
    b = balls; o = overs
    if is_legal:
        b += 1
        if b == 6: o += 1; b = 0
    return b, o

# ==========================================
# SECTION 1: MATCH HEADER (BLUE GRADIENT)
# ==========================================
st.markdown('<div class="match-header">', unsafe_allow_html=True)
col_l1, col_title, col_l2 = st.columns([1, 4, 1])
with col_l1:
    if team1_logo: st.image(Image.open(team1_logo), width=70)
    else: st.markdown(f"### 🛡️ {team1}")
with col_title:
    st.markdown(f"<h2 style='text-align: center; color: #ffffff; margin:0;'>Innings {curr}: {batting_team} vs {bowling_team}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #a0c4ff; margin:5px;'>🪙 Toss: {toss_winner} won and elected to <b>{toss_decision}</b> first.</p>", unsafe_allow_html=True)
with col_l2:
    if team2_logo: st.image(Image.open(team2_logo), width=70)
    else: st.markdown(f"### ⚔️ {team2}")

active_batting_squad = batting_squad_1 if curr == 1 else batting_squad_2
active_bowling_squad = bowling_squad_1 if curr == 1 else bowling_squad_2

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1: striker = st.selectbox("🏏 Striker", active_batting_squad if active_batting_squad else ["No Players"])
with col_p2: non_striker = st.selectbox("🏃 Non-Striker", active_batting_squad if active_batting_squad else ["No Players"])
with col_p3: current_bowler = st.selectbox("⚾ Current Bowler", active_bowling_squad if active_bowling_squad else ["No Players"])

if curr == 2:
    runs_needed = st.session_state.target - runs
    total_legal_balls = (match_overs * 6) - (overs * 6 + balls)
    if runs_needed <= 0: st.success(f"🎉 **{batting_team} Won the Match!**")
    elif wickets >= 10 or total_legal_balls <= 0: st.error(f"🏁 **Match Ended!**")
    else: st.warning(f"🎯 **Target:** {st.session_state.target} | **Need {runs_needed} runs** in {total_legal_balls} balls")

total_ov_float = overs + (balls / 6.0)
crr = f"{runs / total_ov_float:.2f}" if total_ov_float > 0 else "0.00"

st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Score", f"{runs}/{wickets}")
c2.metric("Overs", f"{overs}.{balls}")
c3.metric("CRR", crr)
c4.metric("Extras", extras)
c5.metric("4s", fours)
c6.metric("6s", sixes)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 2: WICKET DETAILS (RED GRADIENT)
# ==========================================
st.markdown('<div class="wicket-section">', unsafe_allow_html=True)
st.markdown("<h3 style='color: #ff8088; margin-top:0;'>🔴 WICKET DETAILS</h3>", unsafe_allow_html=True)
w_col1, w_col2, w_col3, w_col4, w_col5 = st.columns(5)
with w_col1: out_batsman = st.selectbox("OUT BATSMAN", active_batting_squad)
with w_col2: fielder_name = st.selectbox("FIELDER", active_bowling_squad)
with w_col3: out_type = st.selectbox("OUT TYPE", ["Caught", "Bowled", "Run Out", "Stumped", "LBW", "Hit Wicket", "Retired Hurt", "Obstructing the Field"])
with w_col4: wicket_bowler = st.selectbox("BOWLER", active_bowling_squad, index=active_bowling_squad.index(current_bowler) if current_bowler in active_bowling_squad else 0)
with w_col5:
    st.markdown("<br>", unsafe_allow_html=True)
    set_wicket_btn = st.button("🔴 SET WICKET", use_container_width=True)

if set_wicket_btn:
    save_history()
    new_wickets = wickets + 1 if wickets < 10 else 10
    nb, no = add_ball_logic(True)
    update_curr(runs, new_wickets, nb, no, extras, fours, sixes)
    
    bat_df = st.session_state.i1_batting_df if curr == 1 else st.session_state.i2_batting_df
    if out_batsman in bat_df['Batsman'].values:
        idx = bat_df.index[bat_df['Batsman'] == out_batsman][0]
        bat_df.loc[idx, 'How Out / Status'] = out_type
        if out_type in ["Caught", "Stumped"]:
            bat_df.loc[idx, 'Bowled / Fielder'] = f"{wicket_bowler} (b) / {fielder_name} (c)"
        elif out_type == "Run Out":
            bat_df.loc[idx, 'Bowled / Fielder'] = f"Run Out ({fielder_name})"
        else:
            bat_df.loc[idx, 'Bowled / Fielder'] = wicket_bowler

    bowl_df = st.session_state.i1_bowling_df if curr == 1 else st.session_state.i2_bowling_df
    if wicket_bowler in bowl_df['Bowler'].values and out_type not in ["Run Out", "Retired Hurt"]:
        b_idx = bowl_df.index[bowl_df['Bowler'] == wicket_bowler][0]
        bowl_df.loc[b_idx, 'Wickets'] += 1

    st.success(f"Wicket Set: {out_batsman} ({out_type})!")
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 3: LIVE SCORING CONTROLS (GREEN GRADIENT)
# ==========================================
st.markdown('<div class="scoring-section">', unsafe_allow_html=True)
st.markdown("<h3 style='color: #a8ff78; margin-top:0;'>🎮 LIVE SCORING CONTROLS</h3>", unsafe_allow_html=True)

def record_ball(r_add=0, is_legal=True, is_four=False, is_six=False, is_dot=False):
    save_history()
    new_runs = runs + r_add
    new_fours = fours + (1 if is_four else 0)
    new_sixes = sixes + (1 if is_six else 0)
    nb, no = add_ball_logic(is_legal)
    update_curr(new_runs, wickets, nb, no, extras, new_fours, new_sixes)
    
    bat_df = st.session_state.i1_batting_df if curr == 1 else st.session_state.i2_batting_df
    if striker in bat_df['Batsman'].values:
        idx = bat_df.index[bat_df['Batsman'] == striker][0]
        bat_df.loc[idx, 'Runs'] += r_add
        if is_legal: bat_df.loc[idx, 'Balls'] += 1
        if is_four: bat_df.loc[idx, '4s'] += 1
        if is_six: bat_df.loc[idx, '6s'] += 1
        if bat_df.loc[idx, 'How Out / Status'] == "Yet to Bat":
            bat_df.loc[idx, 'How Out / Status'] = "Batting"

    bowl_df = st.session_state.i1_bowling_df if curr == 1 else st.session_state.i2_bowling_df
    if current_bowler in bowl_df['Bowler'].values:
        b_idx = bowl_df.index[bowl_df['Bowler'] == current_bowler][0]
        bowl_df.loc[b_idx, 'Runs'] += r_add
        if is_dot: bowl_df.loc[b_idx, 'Dots'] += 1
        if is_legal:
            curr_ov = bowl_df.loc[b_idx, 'Overs']
            full_ov = int(curr_ov)
            ball_part = round((curr_ov - full_ov) * 10) + 1
            if ball_part >= 6: bowl_df.loc[b_idx, 'Overs'] = full_ov + 1.0
            else: bowl_df.loc[b_idx, 'Overs'] = full_ov + (ball_part / 10.0)

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
with c1:
    if st.button("⚪ 0 Run"): record_ball(0, True, False, False, True); st.rerun()
with c2:
    if st.button("➕ 1 Run"): record_ball(1, True, False, False, False); st.rerun()
with c3:
    if st.button("➕ 2 Runs"): record_ball(2, True, False, False, False); st.rerun()
with c4:
    if st.button("➕ 3 Runs"): record_ball(3, True, False, False, False); st.rerun()
with c5:
    if st.button("🔥 4 Runs"): record_ball(4, True, True, False, False); st.rerun()
with c6:
    if st.button("🚀 6 Runs"): record_ball(6, True, False, True, False); st.rerun()
with c7:
    if st.button("↩️ Undo"):
        if history:
            last = history.pop()
            update_curr(last['runs'], last['wickets'], last['balls'], last['overs'], last['extras'], last['fours'], last['sixes'])
            st.success("Undone!"); st.rerun()

e1, e2 = st.columns(2)
with e1:
    if st.button("🟡 Wide (+1 Extra)"):
        save_history()
        if curr == 1: st.session_state.i1_extras += 1
        else: st.session_state.i2_extras += 1
        update_curr(runs + 1, wickets, balls, overs, extras + 1, fours, sixes); st.rerun()
with e2:
    if st.button("🟠 No Ball (+1 Extra)"):
        save_history()
        if curr == 1: st.session_state.i1_extras += 1
        else: st.session_state.i2_extras += 1
        update_curr(runs + 1, wickets, balls, overs, extras + 1, fours, sixes); st.rerun()

if curr == 1:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏁 End 1st Innings & Start 2nd Innings", use_container_width=True):
        st.session_state.target = runs + 1
        st.session_state.inning = 2
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 4: SCORECARDS (PURPLE GRADIENT)
# ==========================================
st.markdown('<div class="scorecard-section">', unsafe_allow_html=True)
st.markdown("<h3 style='color: #d4bfff; margin-top:0;'>📊 SCORECARDS & STATS</h3>", unsafe_allow_html=True)

st.subheader(f"1st Innings Scorecard ({i1_bat} vs {i1_bowl})")
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.session_state.i1_batting_df['SR'] = st.session_state.i1_batting_df.apply(lambda r: round((r['Runs'] / r['Balls']) * 100, 2) if r['Balls'] > 0 else 0.0, axis=1)
    st.session_state.i1_batting_df = st.data_editor(st.session_state.i1_batting_df, key="i1_bat_full", num_rows="fixed")
with col_s2:
    st.session_state.i1_bowling_df['Economy'] = st.session_state.i1_bowling_df.apply(lambda r: round(r['Runs'] / r['Overs'], 2) if r['Overs'] > 0 else 0.0, axis=1)
    st.session_state.i1_bowling_df = st.data_editor(st.session_state.i1_bowling_df, key="i1_bowl_full", num_rows="fixed")

st.markdown("---")
st.subheader(f"2nd Innings Scorecard ({i2_bat} vs {i2_bowl})")
col_s3, col_s4 = st.columns(2)
with col_s3:
    st.session_state.i2_batting_df['SR'] = st.session_state.i2_batting_df.apply(lambda r: round((r['Runs'] / r['Balls']) * 100, 2) if r['Balls'] > 0 else 0.0, axis=1)
    st.session_state.i2_batting_df = st.data_editor(st.session_state.i2_batting_df, key="i2_bat_full", num_rows="fixed")
with col_s4:
    st.session_state.i2_bowling_df['Economy'] = st.session_state.i2_bowling_df.apply(lambda r: round(r['Runs'] / r['Overs'], 2) if r['Overs'] > 0 else 0.0, axis=1)
    st.session_state.i2_bowling_df = st.data_editor(st.session_state.i2_bowling_df, key="i2_bowl_full", num_rows="fixed")
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 5: MATCH SUMMARY (ORANGE/GOLD GRADIENT)
# ==========================================
st.markdown('<div class="summary-section">', unsafe_allow_html=True)
st.markdown("<h3 style='color: #000000; margin-top:0;'>📋 MATCH SUMMARY OVERVIEW</h3>", unsafe_allow_html=True)
summary_data = [
    {"Innings": "1st Innings", "Batting Team": st.session_state.i1_batting, "Bowling Team": st.session_state.i1_bowling, "Score": f"{st.session_state.i1_runs}/{st.session_state.i1_wickets}", "Overs": f"{st.session_state.i1_overs}.{st.session_state.i1_balls}"},
    {"Innings": "2nd Innings", "Batting Team": st.session_state.i2_batting, "Bowling Team": st.session_state.i2_bowling, "Score": f"{st.session_state.i2_runs}/{st.session_state.i2_wickets}", "Overs": f"{st.session_state.i2_overs}.{st.session_state.i2_balls}"}
]
df_summary = pd.DataFrame(summary_data)
st.table(df_summary)

csv = df_summary.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Match Summary as CSV",
    data=csv,
    file_name='cricket_match_summary.csv',
    mime='text/css',
)
st.markdown('</div>', unsafe_allow_html=True)
