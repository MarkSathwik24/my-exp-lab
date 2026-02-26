import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# 1. Page Config
st.set_page_config(page_title="Research Time-Lap", layout="wide")
st.title("⏱️ Research Timeline Lab")

# 2. Initialize Session State
if "laps" not in st.session_state:
    st.session_state.laps = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# 3. Sidebar Controls
st.sidebar.header("Stopwatch")
if not st.session_state.start_time:
    if st.sidebar.button("🚀 Start Timer", use_container_width=True):
        st.session_state.start_time = datetime.now()
        st.rerun()
else:
    elapsed = datetime.now() - st.session_state.start_time
    st.sidebar.metric("Total Elapsed", f"{str(elapsed).split('.')[0]}")
    
    if st.sidebar.button("🚩 Lap / Capture Time", use_container_width=True):
        new_lap = {
            "ID": len(st.session_state.laps) + 1,
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Duration_Seconds": elapsed.total_seconds(),
            "Note": ""
        }
        st.session_state.laps.append(new_lap)
    
    if st.sidebar.button("🛑 Reset", type="primary", use_container_width=True):
        st.session_state.laps = []
        st.session_state.start_time = None
        st.rerun()

# 4. Interactive Note Entry
st.subheader("📝 Lapped Observations")
if st.session_state.laps:
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(st.session_state.laps)
    
    # Create an editable data editor for the notes
    edited_df = st.data_editor(
        df,
        column_config={
            "ID": st.column_config.NumberColumn(disabled=True),
            "Timestamp": st.column_config.TextColumn(disabled=True),
            "Duration_Seconds": st.column_config.NumberColumn("Elapsed (s)", disabled=True),
            "Note": st.column_config.TextColumn("Observation / Note", width="large", placeholder="Type what happened here...")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Sync edits back to session state
    st.session_state.laps = edited_df.to_dict('records')

    # 5. Interactive Timeline Plot
    st.divider()
    st.subheader("📊 Session Timeline")
    if len(st.session_state.laps) > 0:
        fig = px.scatter(
            edited_df, 
            x="Timestamp", 
            y="Duration_Seconds", 
            text="Note",
            size="Duration_Seconds",
            color="Duration_Seconds",
            title="Observations Over Time",
            labels={"Duration_Seconds": "Seconds since start"},
            template="plotly_dark"
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
        
    # Export Option
    if st.button("💾 Export to CSV"):
        edited_df.to_csv(f"session_log_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", index=False)
        st.success("Log saved locally!")
else:
    st.info("Start the timer and hit 'Lap' to record a timestamped note.")

# 6. Auto-Refresh (UI hack to keep timer visually updating)
if st.session_state.start_time:
    time.sleep(1)
    st.rerun()
