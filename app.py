import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cricket Scoreboard Manager Pro", layout="wide")

st.title("🏏 Cricket Scoreboard Manager Pro (Web Version)")

# Initialize Session State
if 'runs' not in st.session_state: st.session_state.runs = 0
if 'wickets' not in st.session_state: st.session_state.wickets = 0
if 'balls' not in st.session_state: st.session_state.balls = 0
if 'overs' not in st.session_state: st.session_state.overs = 0
if 'extras' not in st.session_state: st.session_state.extras = 0
if 'fours' not in st.session_state: st.session_state.fours = 0
if 'sixes' not in st.session_state: st.session_state.sixes = 0

# Sidebar for Team & Match Setup
st.sidebar.header("⚙ Match Setup")
team1 = st.sidebar.text_input("Team A Name", "AUS")
team2 = st.sidebar.text_input("Team B Name", "PAK")
match_overs = st.sidebar.number_input("Total Match Overs", min_value=1, max_value=50, value=5)

batting_team = st.sidebar.selectbox("Batting Team", [team1, team2])
bowling_team = team2 if batting_team == team1 else team1

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Match Score"):
    st.session_state.runs = 0
    st.session_state.wickets = 0
    st.session_state.balls = 0
    st.session_state.overs = 0
    st.session_state.extras = 0
    st.session_state.fours = 0
    st.session_state.sixes = 0
    st.rerun()

# Main Header Stats
st.subheader(f"📍 {batting_team} vs {bowling_team}")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Score", f"{st.session_state.runs}/{st.session_state.wickets}")
total_ov_float = st.session_state.overs + (st.session_state.balls / 6.0)
crr = f"{st.session_state.runs / total_ov_float:.2f}" if total_ov_float > 0 else "0.00"
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

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    if st.button("0 Run (Dot)"):
        add_ball_logic(True)
        st.rerun()
with c2:
    if st.button("+1 Run"):
        st.session_state.runs += 1
        add_ball_logic(True)
        st.rerun()
with c3:
    if st.button("+2 Runs"):
        st.session_state.runs += 2
        add_ball_logic(True)
        st.rerun()
with c4:
    if st.button("+3 Runs"):
        st.session_state.runs += 3
        add_ball_logic(True)
        st.rerun()
with c5:
    if st.button("🔥 4 Runs"):
        st.session_state.runs += 4
        st.session_state.fours += 1
        add_ball_logic(True)
        st.rerun()
with c6:
    if st.button("🚀 6 Runs"):
        st.session_state.runs += 6
        st.session_state.sixes += 1
        add_ball_logic(True)
        st.rerun()

st.markdown("### Extras & Wickets")
e1, e2, e3 = st.columns(3)

with e1:
    if st.button("Wide (+1 Extra)"):
        st.session_state.runs += 1
        st.session_state.extras += 1
        st.rerun()
with e2:
    if st.button("No Ball (+1 Extra)"):
        st.session_state.runs += 1
        st.session_state.extras += 1
        st.rerun()
with e3:
    if st.button("❌ Wicket"):
        if st.session_state.wickets < 10:
            st.session_state.wickets += 1
            add_ball_logic(True)
        st.rerun()

st.markdown("---")
st.info("💡 Tip: Streamlit app var code update kelyanantar, tumchi live website automatic update hoil ani sagle scoring buttons disu lagtil!")
