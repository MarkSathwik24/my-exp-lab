import streamlit as st
import pandas as pd
import json
import datetime
import os
import calendar

DATA_FILE = "path_data_v3.json"

# --- DATA INITIALIZATION ---
def load_data():
    if not os.path.exists(DATA_FILE):
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
current_week = f"{datetime.date.today().year}-W{datetime.date.today().isocalendar()[1]}"

# Strict Sync and Purge
current_daily_log = data["daily_logs"].get(today, {})
data["daily_logs"][today] = {
    task: {sub: current_daily_log.get(task, {}).get(sub, False) for sub in subs}
    for task, subs in data["daily_tasks"].items()
}

current_weekly_log = data["weekly_logs"].get(current_week, {})
data["weekly_logs"][current_week] = {
    task: {sub: current_weekly_log.get(task, {}).get(sub, False) for sub in subs}
    for task, subs in data["weekly_tasks"].items()
}
save_data(data)

# Initialize Session State for Date Selection
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

# --- APP LAYOUT ---
st.set_page_config(page_title="My Path Tracker", layout="centered")
st.title("My Path Tracker")

tab_daily, tab_weekly, tab_history, tab_settings = st.tabs(["Daily Path", "Weekly Path", "Calendar & History", "Settings"])

# --- TAB 1: DAILY PATH ---
with tab_daily:
    st.header(f"Daily Log: {today}")
    
    total_daily_subs = sum(len(subs) for subs in data["daily_tasks"].values())
    completed_daily = sum(
        sum(1 for sub in subs if data["daily_logs"][today].get(task, {}).get(sub, False))
        for task, subs in data["daily_tasks"].items()
    )
    
    if total_daily_subs > 0:
        progress_pct = completed_daily / total_daily_subs
        st.progress(progress_pct)
        st.write(f"**Today's Progress:** {int(progress_pct * 100)}% ({completed_daily}/{total_daily_subs} subtasks)")
        st.divider()

        for task, subs in data["daily_tasks"].items():
            st.subheader(task)
            for sub in subs:
                current_val = data["daily_logs"][today][task].get(sub, False)
                new_val = st.checkbox(sub, value=current_val, key=f"d_{task}_{sub}")
                
                if new_val != current_val:
                    data["daily_logs"][today][task][sub] = new_val
                    save_data(data)
                    st.rerun()
    else:
        st.info("No daily tasks set up yet. Go to Settings!")

# --- TAB 2: WEEKLY PATH ---
with tab_weekly:
    st.header(f"Weekly Log: {current_week}")
    
    total_weekly_subs = sum(len(subs) for subs in data["weekly_tasks"].values())
    completed_weekly = sum(
        sum(1 for sub in subs if data["weekly_logs"][current_week].get(task, {}).get(sub, False))
        for task, subs in data["weekly_tasks"].items()
    )
    
    if total_weekly_subs > 0:
        progress_pct_w = completed_weekly / total_weekly_subs
        st.progress(progress_pct_w)
        st.write(f"**This Week's Progress:** {int(progress_pct_w * 100)}% ({completed_weekly}/{total_weekly_subs} subtasks)")
        st.divider()

        for task, subs in data["weekly_tasks"].items():
            st.subheader(task)
            for sub in subs:
                current_val = data["weekly_logs"][current_week][task].get(sub, False)
                new_val = st.checkbox(sub, value=current_val, key=f"w_{task}_{sub}")
                
                if new_val != current_val:
                    data["weekly_logs"][current_week][task][sub] = new_val
                    save_data(data)
                    st.rerun()
    else:
        st.info("No weekly tasks set up yet. Go to Settings!")

# --- TAB 3: CALENDAR & HISTORY ---
with tab_history:
    st.header("📈 Tracking History")
    
    # 1. Top Section: 30-Day Trend
    st.subheader("Last 30 Days Trend")
    last_30_days = [str(datetime.date.today() - datetime.timedelta(days=i)) for i in range(29, -1, -1)]
    trend_data = {"Date": [], "Progress (%)": []}
    
    for d in last_30_days:
        if d in data["daily_logs"]:
            day_log = data["daily_logs"][d]
            total = sum(len(subs) for subs in day_log.values())
            completed = sum(sum(1 for v in subs.values() if v) for subs in day_log.values())
            pct = (completed / total * 100) if total > 0 else 0
        else:
            pct = 0
            
        trend_data["Date"].append(d)
        trend_data["Progress (%)"].append(pct)
        
    df_trend = pd.DataFrame(trend_data)
    st.bar_chart(df_trend.set_index("Date"))
    st.divider()

    # 2. Middle Section: Specific Date Snapshot
    st.subheader("Inspect a Specific Date")
    
    # Update session state if the date input is changed manually
    selected_date_input = st.date_input("🗓️ View end-of-day snapshot for:", st.session_state.selected_date)
    if selected_date_input != st.session_state.selected_date:
        st.session_state.selected_date = selected_date_input
        st.rerun()
        
    selected_date_str = str(st.session_state.selected_date)
    
    if selected_date_str in data["daily_logs"]:
        day_log = data["daily_logs"][selected_date_str]
        
        hist_total = sum(len(subs) for subs in day_log.values())
        hist_completed = sum(sum(1 for v in subs.values() if v) for subs in day_log.values())
        
        if hist_total > 0:
            hist_pct = hist_completed / hist_total
            st.metric(label=f"Total Progress on {selected_date_str}", value=f"{int(hist_pct*100)}%", delta=f"{hist_completed}/{hist_total} subtasks completed")
            st.progress(hist_pct)
            
            st.write("**Task Breakdown:**")
            for task, subs in day_log.items():
                if subs: 
                    with st.expander(task):
                        for sub, is_done in subs.items():
                            status = "✅" if is_done else "❌"
                            st.write(f"{status} {sub}")
        else:
             st.info(f"No tasks were logged on {selected_date_str}.")
    else:
        st.warning(f"No activity recorded for {selected_date_str}.")

    st.divider()

    # 3. Bottom Section: Normal Visual Calendar
    st.subheader("📅 Monthly Calendar")
    
    sel_year = st.session_state.selected_date.year
    sel_month = st.session_state.selected_date.month
    
    cal = calendar.monthcalendar(sel_year, sel_month)
    month_name = calendar.month_name[sel_month]
    
    st.write(f"### {month_name} {sel_year}")
    
    # Days of week headers
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day_name in enumerate(days_of_week):
        cols[i].write(f"**{day_name}**")
        
    # Calendar Grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day != 0:
                # If a day is clicked, update the selected date and refresh to show the snapshot above
                if cols[i].button(str(day), use_container_width=True, key=f"cal_{sel_year}_{sel_month}_{day}"):
                    st.session_state.selected_date = datetime.date(sel_year, sel_month, day)
                    st.rerun()

# --- TAB 4: SETTINGS ---
with tab_settings:
    st.header("Configure Your Path")
    st.write("Separate your subtasks with commas. **Click the '+' icon to add new tasks.**")
    
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
        new_daily, new_weekly = {}, {}
        
        for _, row in edited_daily.iterrows():
            name = str(row["Task Name"]).strip()
            subs = [s.strip() for s in str(row["Subtasks (comma separated)"]).split(",") if s.strip()]
            if name and subs and name != "nan":
                new_daily[name] = subs
                
        for _, row in edited_weekly.iterrows():
            name = str(row["Task Name"]).strip()
            subs = [s.strip() for s in str(row["Subtasks (comma separated)"]).split(",") if s.strip()]
            if name and subs and name != "nan":
                new_weekly[name] = subs
                
        data["daily_tasks"] = new_daily
        data["weekly_tasks"] = new_weekly
        save_data(data)
        st.success("Settings saved! Your paths have been updated.")
        st.rerun()
