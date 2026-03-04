import streamlit as st
import json
import datetime
import os

DATA_FILE = "path_data.json"

# --- DATA INITIALIZATION ---
# We use JSON because it handles nested subtasks much better than CSV
def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "task_names": {f"t{i}": f"Task {i}" for i in range(1, 7)},
            "daily_subs": {f"t{i}": [] for i in range(1, 7)},
            "weekly_subs": {f"t{i}": [] for i in range(1, 7)},
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
# This gets the current year and week number (e.g., 2026-W10)
current_week = f"{datetime.date.today().year}-W{datetime.date.today().isocalendar()[1]}"

# Ensure today and this week exist in logs
if today not in data["daily_logs"]:
    data["daily_logs"][today] = {t_key: {} for t_key in data["task_names"]}
if current_week not in data["weekly_logs"]:
    data["weekly_logs"][current_week] = {t_key: {} for t_key in data["task_names"]}

# --- APP LAYOUT ---
st.set_page_config(page_title="Path Tracker", layout="centered")
st.title("My Path Tracker")

tab_daily, tab_weekly, tab_settings = st.tabs(["Daily Path", "Weekly Path", "Settings"])

# --- TAB 1: DAILY PATH ---
with tab_daily:
    st.header(f"Daily Log: {today}")
    
    # Calculate Daily Progress %
    total_daily_subs = sum(len(subs) for subs in data["daily_subs"].values())
    completed_daily = 0
    
    if total_daily_subs > 0:
        for t_key in data["task_names"]:
            for sub in data["daily_subs"][t_key]:
                if data["daily_logs"][today][t_key].get(sub, False):
                    completed_daily += 1
        
        progress_pct = completed_daily / total_daily_subs
        st.progress(progress_pct)
        st.write(f"**Daily Progress:** {int(progress_pct * 100)}% ({completed_daily}/{total_daily_subs} subtasks)")
    else:
        st.info("No daily subtasks set up yet. Go to Settings!")

    st.divider()

    # Display Daily Checkboxes
    for t_key, t_name in data["task_names"].items():
        if data["daily_subs"][t_key]: # Only show task if it has subtasks
            st.subheader(t_name)
            for sub in data["daily_subs"][t_key]:
                # Initialize state if newly created
                if sub not in data["daily_logs"][today][t_key]:
                    data["daily_logs"][today][t_key][sub] = False
                
                current_val = data["daily_logs"][today][t_key][sub]
                # Auto-save logic
                new_val = st.checkbox(sub, value=current_val, key=f"d_{t_key}_{sub}")
                if new_val != current_val:
                    data["daily_logs"][today][t_key][sub] = new_val
                    save_data(data)
                    st.rerun()

# --- TAB 2: WEEKLY PATH ---
with tab_weekly:
    st.header(f"Weekly Log: {current_week}")
    
    # Calculate Weekly Progress %
    total_weekly_subs = sum(len(subs) for subs in data["weekly_subs"].values())
    completed_weekly = 0
    
    if total_weekly_subs > 0:
        for t_key in data["task_names"]:
            for sub in data["weekly_subs"][t_key]:
                if data["weekly_logs"][current_week][t_key].get(sub, False):
                    completed_weekly += 1
        
        progress_pct_w = completed_weekly / total_weekly_subs
        st.progress(progress_pct_w)
        st.write(f"**Weekly Progress:** {int(progress_pct_w * 100)}% ({completed_weekly}/{total_weekly_subs} subtasks)")
    else:
        st.info("No weekly subtasks set up yet. Go to Settings!")

    st.divider()

    # Display Weekly Checkboxes
    for t_key, t_name in data["task_names"].items():
        if data["weekly_subs"][t_key]: 
            st.subheader(t_name)
            for sub in data["weekly_subs"][t_key]:
                if sub not in data["weekly_logs"][current_week][t_key]:
                    data["weekly_logs"][current_week][t_key][sub] = False
                
                current_val = data["weekly_logs"][current_week][t_key][sub]
                new_val = st.checkbox(sub, value=current_val, key=f"w_{t_key}_{sub}")
                if new_val != current_val:
                    data["weekly_logs"][current_week][t_key][sub] = new_val
                    save_data(data)
                    st.rerun()

# --- TAB 3: SETTINGS ---
with tab_settings:
    st.header("Configure Your Path")
    st.write("Separate subtasks with commas (e.g., Read chapter, Write notes).")
    
    with st.form("settings_form"):
        for t_key, t_name in data["task_names"].items():
            st.subheader(f"Configure {t_name}")
            new_name = st.text_input("Task Name", value=t_name, key=f"name_{t_key}")
            
            daily_str = ", ".join(data["daily_subs"][t_key])
            new_daily = st.text_input("Daily Subtasks", value=daily_str, key=f"d_sub_{t_key}")
            
            weekly_str = ", ".join(data["weekly_subs"][t_key])
            new_weekly = st.text_input("Weekly Subtasks", value=weekly_str, key=f"w_sub_{t_key}")
            st.divider()
            
        if st.form_submit_button("Save All Settings"):
            for t_key in data["task_names"]:
                # Update Names
                data["task_names"][t_key] = st.session_state[f"name_{t_key}"]
                
                # Update Subtasks (split by comma, clean up spaces, remove empty strings)
                d_subs = [s.strip() for s in st.session_state[f"d_sub_{t_key}"].split(",") if s.strip()]
                w_subs = [s.strip() for s in st.session_state[f"w_sub_{t_key}"].split(",") if s.strip()]
                
                data["daily_subs"][t_key] = d_subs
                data["weekly_subs"][t_key] = w_subs
                
            save_data(data)
            st.success("Settings saved successfully!")
            st.rerun()
