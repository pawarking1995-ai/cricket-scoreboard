import streamlit as st

st.title("🏏 Cricket Scoreboard Manager Pro")

# Team names input
team1 = st.text_input("Team A Name", "AUS")
team2 = st.text_input("Team B Name", "PAK")

st.subheader(f"{team1} vs {team2}")

# Score tracking session state
if 'runs' not in st.session_state:
    st.session_state.runs = 0
if 'wickets' not in st.session_state:
    st.session_state.wickets = 0

st.metric(label="Live Score", value=f"{st.session_state.runs}/{st.session_state.wickets}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("+1 Run"):
        st.session_state.runs += 1
        st.rerun()
with col2:
    if st.button("+4 Runs"):
        st.session_state.runs += 4
        st.rerun()
with col3:
    if st.button("Wicket"):
        st.session_state.wickets += 1
        st.rerun()