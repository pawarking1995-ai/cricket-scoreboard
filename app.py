import streamlit as st
import pandas as pd

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
st.sidebar.header("⚙ Match Setup")
team1 = st.sidebar.text_input("Team A Name", "AUS")
team2 = st.sidebar.text_input("Team B Name", "PAK")
match_overs = st.sidebar.number_input("Total Match Overs", min_value=1, max_value=50, value=5)

if st.session_state.inning == 1:
    batting_team = st.sidebar.selectbox("1st Inning Batting Team", [team1, team2])
    bowling_team = team2 if batting_team == team1 else team1
    st.session_state.i1_batting = batting_team
    st.session_state.i1_bowling = bowling_team
    st.session_state.i2_batting = bowling_team
    st.session_state.i2_bowling = batting_team
else:
    batting_team = st.session_state.i2_batting
    bowling_team = st.session_state.i2_bowling
    st.sidebar.info(f"**2nd Inning Batting:** {batting_team} | **Bowling:** {bowling_team}")

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

# Main Header Stats
st.subheader(f"📍 Innings {curr}: {batting_team} (Batting) vs {bowling_team} (Bowling)")

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

# Match Summary Table Section
st.markdown("---")
st.subheader("📋 Match Summary & Scorecards")

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
