import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# 1. Setup & Data Persistence (Local CSV)
DB_FILE = "study_log.csv"
if "db" not in st.session_state:
    try:
        st.session_state.db = pd.read_csv(DB_FILE)
    except FileNotFoundError:
        st.session_state.db = pd.DataFrame(columns=["Date", "Subject", "Minutes"])

st.set_page_config(page_title="Academic Flow", layout="centered")

# 2. Sidebar: The Timer (Pomodoro)
st.sidebar.title("⏳ Focus Timer")
minutes = st.sidebar.number_input("Session Length (min):", 1, 120, 25)
subject = st.sidebar.selectbox("Subject:", ["Thesis", "Optimal Control", "GNSS", "Aerodynamics", "Other"])

if st.sidebar.button("Start Session"):
    with st.empty():
        for i in range(minutes * 60, 0, -1):
            mins, secs = divmod(i, 60)
            st.sidebar.metric("Remaining", f"{mins:02d}:{secs:02d}")
            time.sleep(1)
        st.sidebar.success("Session Complete!")
        
        # Log data
        new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Subject": subject, "Minutes": minutes}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.db.to_csv(DB_FILE, index=False)

# 3. Main UI: Visualization
st.title("🚀 Academic Performance Tracker")

if not st.session_state.db.empty:
    # Interactive Plot: Study Distribution
    st.subheader("Your Study Distribution")
    fig = px.pie(st.session_state.db, values='Minutes', names='Subject', 
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Plot: Productivity over Time
    st.subheader("Daily Momentum")
    daily_stats = st.session_state.db.groupby("Date")["Minutes"].sum().reset_index()
    fig2 = px.bar(daily_stats, x="Date", y="Minutes", 
                  title="Total Minutes per Day", color_discrete_sequence=['#00CC96'])
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Complete your first session in the sidebar to generate your productivity plots!")

# 4. Quick Notes Section
st.divider()
st.subheader("📝 Quick Research Notes")
quick_note = st.text_area("Jot down a quick thought or a formula (LaTeX supported):", placeholder="e.g., $J = \int_{t_0}^{t_f} L(x, u, t) dt$")
if st.button("Save Note"):
    with open("quick_notes.txt", "a") as f:
        f.write(f"\n[{datetime.now()}] {quick_note}")
    st.toast("Note captured!")
