import streamlit as st
import pandas as pd
import json
import datetime
import os

DATA_FILE = "path_data_v2.json"

# --- DATA INITIALIZATION ---
def load_data():
    if not os.path.exists(DATA_FILE):
        # Default template setup
        default_data = {
            "daily_tasks": {
                "Control Systems Study": ["Review LQR code", "Simulate inverted pendulum"],
                "Daily Routine": ["Morning walk", "Read 10 pages"]
            },
            "weekly_tasks": {
                "M.Tech Thesis": ["Draft literature review", "Run aerodynamics simulation"],
                "Project Work": ["GNSS signal testing", "Update Kalman filter"]
            },
            "daily_logs": {},
            "weekly_logs": {}
        }
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f)
            
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
today = str(datetime.date.today())
# Gets current year and week number (e.g., 2026-W10)
current_week = f"{datetime.date.today().year}-W{datetime.date.today().isocalendar()[1]}"

# Safely initialize today's logs
if today not in data["daily_logs"]:
    data["daily_logs"][today] = {}
for task in data["daily_tasks"]:
    if task not in data["daily_logs"][today]:
        data["daily_logs"][today][task] = {}

# Safely initialize this week's logs
if current_week not in data["weekly_logs"]:
    data["weekly_logs"][current_week] = {}
for task in data["weekly_tasks"]:
    if task not in data["weekly_logs"][current_week]:
        data["weekly_logs"][current_week][task] = {}

# --- APP LAYOUT ---
st.set_page_config(page_title="My Path Tracker", layout="centered")
st.title("My Path Tracker")

tab_daily, tab_weekly, tab_settings = st.tabs(["Daily Path", "Weekly Path", "Settings"])

# --- TAB 1: DAILY PATH ---
with tab_daily:
    st.header(f"Daily Log: {today}")
    
    # Calculate Daily Progress
    total_daily_subs = sum(len(subs) for subs in data["daily_tasks"].values())
    completed_daily = 0
    
    if total_daily_subs > 0:
        for task, subs in data["daily_tasks"].items():
            for sub in subs:
                if data["daily_logs"][today][task].get(sub, False):
                    completed_daily += 1
        
        progress_pct = completed_daily / total_daily_subs
        st.progress(progress_pct)
        st.write(f"**Daily Progress:** {int(progress_pct * 100)}% ({completed_daily}/{total_daily_subs} subtasks)")
        st.divider()

        # Display Checkboxes
        for task, subs in data["daily_tasks"].items():
            st.subheader(task)
            for sub in subs:
                current_val = data["daily_logs"][today][task].get(sub, False)
                new_val = st.checkbox(sub, value=current_val, key=f"d_{task}_{sub}")
                
                # Auto-save on click
                if new_val != current_val:
                    data["daily_logs"][today][task][sub] = new_val
                    save_data(data)
                    st.rerun()
    else:
        st.info("No daily tasks set up yet. Go to Settings!")

# --- TAB 2: WEEKLY PATH ---
with tab_weekly:
    st.header(f"Weekly Log: {current_week}")
    
    # Calculate Weekly Progress
    total_weekly_subs = sum(len(subs) for subs in data["weekly_tasks"].values())
    completed_weekly = 0
    
    if total_weekly_subs > 0:
        for task, subs in data["weekly_tasks"].items():
            for sub in subs:
                if data["weekly_logs"][current_week][task].get(sub, False):
                    completed_weekly += 1
        
        progress_pct_w = completed_weekly / total_weekly_subs
        st.progress(progress_pct_w)
        st.write(f"**Weekly Progress:** {int(progress_pct_w * 100)}% ({completed_weekly}/{total_weekly_subs} subtasks)")
        st.divider()

        # Display Checkboxes
        for task, subs in data["weekly_tasks"].items():
            st.subheader(task)
            for sub in subs:
                current_val = data["weekly_logs"][current_week][task].get(sub, False)
                new_val = st.checkbox(sub, value=current_val, key=f"w_{task}_{sub}")
                
                # Auto-save on click
                if new_val != current_val:
                    data["weekly_logs"][current_week][task][sub] = new_val
                    save_data(data)
                    st.rerun()
    else:
        st.info("No weekly tasks set up yet. Go to Settings!")

# --- TAB 3: SETTINGS ---
with tab_settings:
    st.header("Configure Your Path")
    st.write("Separate your subtasks with commas. **Tip: Click the '+' icon at the bottom of the tables to add new rows!**")
    
    # Helper to format dictionaries for the data editor
    def dict_to_df(task_dict):
        return pd.DataFrame([
            {"Task Name": k, "Subtasks (comma separated)": ", ".join(v)} 
            for k, v in task_dict.items()
        ])

    st.subheader("Daily Configuration")
    df_daily = dict_to_df(data["daily_tasks"])
    edited_daily = st.data_editor(df_daily, num_rows="dynamic", use_container_width=True, key="edit_daily")
    
    st.subheader("Weekly Configuration")
    df_weekly = dict_to_df(data["weekly_tasks"])
    edited_weekly = st.data_editor(df_weekly, num_rows="dynamic", use_container_width=True, key="edit_weekly")
    
    if st.button("Save All Settings", type="primary"):
        # Process Daily Table
        new_daily = {}
        for _, row in edited_daily.iterrows():
            name = str(row["Task Name"]).strip()
            subs = [s.strip() for s in str(row["Subtasks (comma separated)"]).split(",") if s.strip()]
            if name and subs and name != "nan":
                new_daily[name] = subs
                
        # Process Weekly Table
        new_weekly = {}
        for _, row in edited_weekly.iterrows():
            name = str(row["Task Name"]).strip()
            subs = [s.strip() for s in str(row["Subtasks (comma separated)"]).split(",") if s.strip()]
            if name and subs and name != "nan":
                new_weekly[name] = subs
                
        # Save updates
        data["daily_tasks"] = new_daily
        data["weekly_tasks"] = new_weekly
        save_data(data)
        st.success("Settings saved! Your paths have been updated.")
        st.rerun()
