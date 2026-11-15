import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cricket Scoreboard Manager Pro", layout="wide")

st.title("🏏 Cricket Scoreboard Manager Pro (Web Version)")

# Initialize Session State
if 'inning' not in st.session_state: st.session_state.inning = 1
if 'target' not in st.session_state: st.session_state.target = 0
if 'history' not in st.session_state: st.session_state.history = []

# Match data storage for both innings
if 'match_records' not in st.session_state:
    st.session_state.match_records = {
        "Inning 1": {"batting": "", "bowling": "", "runs": 0, "wickets": 0, "overs": "0.0", "extras": 0, "fours": 0, "sixes": 0, "crr": "0.00"},
        "Inning 2": {"batting": "", "bowling": "", "runs": 0, "wickets": 0, "overs": "0.0", "extras": 0, "fours": 0, "sixes": 0, "crr": "0.00"}
    }

current_key = f"Inning {st.session_state.inning}"

if current_key not in st.session_state:
    st.session_state.runs = 0
    st.session_state.wickets = 0
    st.session_state.balls = 0
    st.session_state.overs = 0
    st.session_state.extras = 0
    st.session_state.fours = 0
    st.session_state.sixes = 0

def save_state_to_history():
    state_snapshot = {
        'runs': st.session_state.runs,
        'wickets': st.session_state.wickets,
        'balls': st.session_state.balls,
        'overs': st.session_state.overs,
        'extras': st.session_state.extras,
        'fours': st.session_state.fours,
        'sixes': st.session_state.sixes
    }
    st.session_state.history.append(state_snapshot)

# Sidebar for Team & Match Setup
st.sidebar.header("⚙ Match Setup")
team1 = st.sidebar.text_input("Team A Name", "AUS")
team2 = st.sidebar.text_input("Team B Name", "PAK")
match_overs = st.sidebar.number_input("Total Match Overs", min_value=1, max_value=50, value=5)

if st.session_state.inning == 1:
    batting_team = st.sidebar.selectbox("1st Inning Batting Team", [team1, team2], key="b1")
    bowling_team = team2 if batting_team == team1 else team1
else:
    # In 2nd inning, batting and bowling teams swap automatically
    batting_team = team2 if st.session_state.match_records["Inning 1"]["batting"] == team1 else team1
    bowling_team = team1 if batting_team == team2 else team2
    st.sidebar.info(f"**2nd Inning Batting:** {batting_team} | **Bowling:** {bowling_team}")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Match Score"):
    st.session_state.runs = 0
    st.session_state.wickets = 0
    st.session_state.balls = 0
    st.session_state.overs = 0
    st.session_state.extras = 0
    st.session_state.fours = 0
    st.session_state.sixes = 0
    st.session_state.inning = 1
    st.session_state.target = 0
    st.session_state.history = []
    st.session_state.match_records = {
        "Inning 1": {"batting": "", "bowling": "", "runs": 0, "wickets": 0, "overs": "0.0", "extras": 0, "fours": 0, "sixes": 0, "crr": "0.00"},
        "Inning 2": {"batting": "", "bowling": "", "runs": 0, "wickets": 0, "overs": "0.0", "extras": 0, "fours": 0, "sixes": 0, "crr": "0.00"}
    }
    st.rerun()

# Calculate CRR
total_ov_float = st.session_state.overs + (st.session_state.balls / 6.0)
crr = f"{st.session_state.runs / total_ov_float:.2f}" if total_ov_float > 0 else "0.00"

# Update live stats in records dictionary
st.session_state.match_records[current_key] = {
    "batting": batting_team,
    "bowling": bowling_team,
    "runs": st.session_state.runs,
    "wickets": st.session_state.wickets,
    "overs": f"{st.session_state.overs}.{st.session_state.balls}",
    "extras": st.session_state.extras,
    "fours": st.session_state.fours,
    "sixes": st.session_state.sixes,
    "crr": crr
}

# Main Header Stats
st.subheader(f"📍 Innings {st.session_state.inning}: {batting_team} (Batting) vs {bowling_team} (Bowling)")

if st.session_state.inning == 2:
    runs_needed = st.session_state.target - st.session_state.runs
    total_legal_balls = (match_overs * 6) - (st.session_state.overs * 6 + st.session_state.balls)
    if runs_needed <= 0:
        st.success(f"🎉 **{batting_team} Won the Match!**")
    elif total_legal_balls <= 0:
        st.error(f"🏁 **Match Ended! {bowling_team} Won the Match!**")
    else:
        st.warning(f"🎯 **Target:** {st.session_state.target} | **Need {runs_needed} runs** in {total_legal_balls} balls")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Score", f"{st.session_state.runs}/{st.session_state.wickets}")
col2.metric("Overs", f"{st.session_state.overs}.{st.session_state.balls}")
col3.metric("CRR", crr)
col4.metric("Extras", st.session_state.extras)
col5.metric("4s", st.session_state.fours)
col6.metric("6s", st.session_state.sixes)

st.markdown("---")

# Scoring Controls
st.subheader("🎮 Live Scoring Controls")

def add_ball_logic(is_legal=True):
    if is_legal:
        st.session_state.balls += 1
        if st.session_state.balls == 6:
            st.session_state.overs += 1
            st.session_state.balls = 0

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    if st.button("0 Run (Dot)"):
        save_state_to_history()
        add_ball_logic(True)
        st.rerun()
with c2:
    if st.button("+1 Run"):
        save_state_to_history()
        st.session_state.runs += 1
        add_ball_logic(True)
        st.rerun()
with c3:
    if st.button("+2 Runs"):
        save_state_to_history()
        st.session_state.runs += 2
        add_ball_logic(True)
        st.rerun()
with c4:
    if st.button("+3 Runs"):
        save_state_to_history()
        st.session_state.runs += 3
        add_ball_logic(True)
        st.rerun()
with c5:
    if st.button("🔥 4 Runs"):
        save_state_to_history()
        st.session_state.runs += 4
        st.session_state.fours += 1
        add_ball_logic(True)
        st.rerun()
with c6:
    if st.button("🚀 6 Runs"):
        save_state_to_history()
        st.session_state.runs += 6
        st.session_state.sixes += 1
        add_ball_logic(True)
        st.rerun()
with c7:
    if st.button("↩️ Undo"):
        if st.session_state.history:
            last_state = st.session_state.history.pop()
            st.session_state.runs = last_state['runs']
            st.session_state.wickets = last_state['wickets']
            st.session_state.balls = last_state['balls']
            st.session_state.overs = last_state['overs']
            st.session_state.extras = last_state['extras']
            st.session_state.fours = last_state['fours']
            st.session_state.sixes = last_state['sixes']
            st.success("Last action undone!")
            st.rerun()
        else:
            st.warning("Nothing to undo!")

st.markdown("### Extras & Wickets")
e1, e2, e3 = st.columns(3)

with e1:
    if st.button("Wide (+1 Extra)"):
        save_state_to_history()
        st.session_state.runs += 1
        st.session_state.extras += 1
        st.rerun()
with e2:
    if st.button("No Ball (+1 Extra)"):
        save_state_to_history()
        st.session_state.runs += 1
        st.session_state.extras += 1
        st.rerun()
with e3:
    if st.button("❌ Wicket"):
        save_state_to_history()
        if st.session_state.wickets < 10:
            st.session_state.wickets += 1
            add_ball_logic(True)
        st.rerun()

# Innings Switch / End Button
st.markdown("---")
if st.session_state.inning == 1:
    if st.button("🏁 End 1st Innings & Start 2nd Innings"):
        st.session_state.target = st.session_state.runs + 1
        st.session_state.inning = 2
        st.session_state.runs = 0
        st.session_state.wickets = 0
        st.session_state.balls = 0
        st.session_state.overs = 0
        st.session_state.extras = 0
        st.session_state.fours = 0
        st.session_state.sixes = 0
        st.session_state.history = []
        st.rerun()

# Match Summary Table Section
st.markdown("---")
st.subheader("📋 Match Summary & Scorecards")

summary_data = [
    {
        "Innings": "1st Innings",
        "Batting Team": st.session_state.match_records["Inning 1"]["batting"],
        "Bowling Team": st.session_state.match_records["Inning 1"]["bowling"],
        "Score": f"{st.session_state.match_records['Inning 1']['runs']}/{st.session_state.match_records['Inning 1']['wickets']}",
        "Overs": st.session_state.match_records["Inning 1"]["overs"],
        "Extras": st.session_state.match_records["Inning 1"]["extras"],
        "4s / 6s": f"{st.session_state.match_records['Inning 1']['fours']} / {st.session_state.match_records['Inning 1']['sixes']}",
        "CRR": st.session_state.match_records["Inning 1"]["crr"]
    },
    {
        "Innings": "2nd Innings",
        "Batting Team": st.session_state.match_records["Inning 2"]["batting"],
        "Bowling Team": st.session_state.match_records["Inning 2"]["bowling"],
        "Score": f"{st.session_state.match_records['Inning 2']['runs']}/{st.session_state.match_records['Inning 2']['wickets']}",
        "Overs": st.session_state.match_records["Inning 2"]["overs"],
        "Extras": st.session_state.match_records["Inning 2"]["extras"],
        "4s / 6s": f"{st.session_state.match_records['Inning 2']['fours']} / {st.session_state.match_records['Inning 2']['sixes']}",
        "CRR": st.session_state.match_records["Inning 2"]["crr"]
    }
]

df_summary = pd.DataFrame(summary_data)
st.table(df_summary)

# Download CSV
csv = df_summary.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Complete Match Summary (CSV)",
    data=csv,
    file_name='cricket_match_complete_summary.csv',
    mime='text/csv',
)
