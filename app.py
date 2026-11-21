st.subheader(f"1st Innings Scorecard ({i1_bat} vs {i1_bowl})")
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.session_state.i1_batting_df['SR'] = st.session_state.i1_batting_df.apply(lambda r: round((r['Runs'] / r['Balls']) * 100, 2) if r['Balls'] > 0 else 0.0, axis=1)
    st.dataframe(st.session_state.i1_batting_df, use_container_width=True, hide_index=True)
with col_s2:
    st.session_state.i1_bowling_df['Economy'] = st.session_state.i1_bowling_df.apply(lambda r: round(r['Runs'] / (((int(r['Overs']) * 6) + round((r['Overs'] - int(r['Overs'])) * 10)) / 6), 2) if r['Overs'] > 0 else 0.0, axis=1)
    st.dataframe(st.session_state.i1_bowling_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader(f"2nd Innings Scorecard ({i2_bat} vs {i2_bowl})")
col_s3, col_s4 = st.columns(2)
with col_s3:
    st.session_state.i2_batting_df['SR'] = st.session_state.i2_batting_df.apply(lambda r: round((r['Runs'] / r['Balls']) * 100, 2) if r['Balls'] > 0 else 0.0, axis=1)
    st.dataframe(st.session_state.i2_batting_df, use_container_width=True, hide_index=True)
with col_s4:
    st.session_state.i2_bowling_df['Economy'] = st.session_state.i2_bowling_df.apply(lambda r: round(r['Runs'] / (((int(r['Overs']) * 6) + round((r['Overs'] - int(r['Overs'])) * 10)) / 6), 2) if r['Overs'] > 0 else 0.0, axis=1)
    st.dataframe(st.session_state.i2_bowling_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 5: MATCH SUMMARY & TOP PERFORMERS
# ==========================================
st.markdown('<div class="summary-section">', unsafe_allow_html=True)
st.markdown("<h2 style='color: #000000; margin-top:0;'>📋 MATCH SUMMARY & TOP PERFORMERS</h2>", unsafe_allow_html=True)

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
        "CRR": i1_crr
    },
    {
        "Innings": "2nd Innings",
        "Batting Team": st.session_state.i2_batting,
        "Bowling Team": st.session_state.i2_bowling,
        "Score": f"{st.session_state.i2_runs}/{st.session_state.i2_wickets}",
        "Overs": f"{st.session_state.i2_overs}.{st.session_state.i2_balls}",
        "Extras": st.session_state.i2_extras,
        "CRR": i2_crr
    }
]

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🌟 Top 5 Performers (Team A & Team B)")

if i1_bat == team1:
    team_a_bat_df = st.session_state.i1_batting_df
    team_b_bowl_df = st.session_state.i1_bowling_df
    team_b_bat_df = st.session_state.i2_batting_df
    team_a_bowl_df = st.session_state.i2_bowling_df
else:
    team_b_bat_df = st.session_state.i1_batting_df
    team_a_bowl_df = st.session_state.i1_bowling_df
    team_a_bat_df = st.session_state.i2_batting_df
    team_b_bowl_df = st.session_state.i2_bowling_df

col_tp1, col_tp2 = st.columns(2)

with col_tp1:
    st.markdown(f"#### 🛡️ {team1} (Team A)")
    st.markdown("##### 🏏 Top 5 Batting")
    top_a_bat = team_a_bat_df.sort_values(by="Runs", ascending=False).head(5)
    st.dataframe(top_a_bat, hide_index=True, use_container_width=True)

    st.markdown("##### ⚾ Top 5 Bowling")
    top_a_bowl = team_a_bowl_df.sort_values(by="Wickets", ascending=False).head(5)
    st.dataframe(top_a_bowl, hide_index=True, use_container_width=True)

with col_tp2:
    st.markdown(f"#### ⚔️ {team2} (Team B)")
    st.markdown("##### 🏏 Top 5 Batting")
    top_b_bat = team_b_bat_df.sort_values(by="Runs", ascending=False).head(5)
    st.dataframe(top_b_bat, hide_index=True, use_container_width=True)

    st.markdown("##### ⚾ Top 5 Bowling")
    top_b_bowl = team_b_bowl_df.sort_values(by="Wickets", ascending=False).head(5)
    st.dataframe(top_b_bowl, hide_index=True, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
csv = df_summary.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Match Summary as CSV",
    data=csv,
    file_name='cricket_match_summary.csv',
    mime='text/csv',
)
st.markdown('</div>', unsafe_allow_html=True)
