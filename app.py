import streamlit as st
import pandas as pd
import datetime
import os

# --- CONFIGURATION & STORAGE ---
DATA_FILE = "progress_log.csv"
DEFAULT_TASKS = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"]

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date"] + DEFAULT_TASKS)
    df.to_csv(DATA_FILE, index=False)

# Load data
df_log = pd.read_csv(DATA_FILE)
today = str(datetime.date.today())

# --- APP LAYOUT ---
st.set_page_config(page_title="Daily Path Tracker", layout="wide")
tab1, tab2, tab3 = st.tabs(["Today's Path", "Weekly Progress", "Settings"])

# --- TAB 3: SETTINGS (Change Task Names) ---
with tab3:
    st.header("Customize Your Tasks")
    new_tasks = []
    for i in range(6):
        # Use existing column names as default values
        current_name = df_log.columns[i+1] if len(df_log.columns) > i+1 else DEFAULT_TASKS[i]
        name = st.text_input(f"Task {i+1} Name", value=current_name, key=f"t{i}")
        new_tasks.append(name)
    
    if st.button("Update Task Names"):
        # Rename columns in the dataframe and save
        df_log.columns = ["Date"] + new_tasks
        df_log.to_csv(DATA_FILE, index=False)
        st.success("Task names updated!")
        st.rerun()

# --- TAB 1: TODAY'S CHECKBOXES ---
with tab1:
    st.header(f"Log for {today}")
    
    # Check if we already have an entry for today
    if today not in df_log["Date"].values:
        new_row = {col: (today if col == "Date" else False) for col in df_log.columns}
        df_log = pd.concat([df_log, pd.DataFrame([new_row])], ignore_index=True)
        df_log.to_csv(DATA_FILE, index=False)

    # Get today's index
    idx = df_log[df_log["Date"] == today].index[0]
    
    # Display 6 checkboxes
    current_status = []
    for task in df_log.columns[1:]:
        is_checked = df_log.at[idx, task]
        # Streamlit checkboxes return True/False
        val = st.checkbox(task, value=bool(is_checked), key=f"check_{task}")
        df_log.at[idx, task] = val
        current_status.append(val)
    
    # Save changes instantly
    if st.button("Save Daily Progress"):
        df_log.to_csv(DATA_FILE, index=False)
        st.balloons()
        st.success("Progress Saved!")

# --- TAB 2: WEEKLY PROGRESS ---
with tab2:
    st.header("Last 7 Days Analysis")
    
    # Convert Date column to datetime for filtering
    df_log['Date'] = pd.to_datetime(df_log['Date'])
    last_7_days = df_log[df_log['Date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
    
    if not last_7_days.empty:
        for task in df_log.columns[1:]:
            # Calculate percentage of 'True' values
            completed_count = last_7_days[task].sum()
            progress_pct = completed_count / 7
            
            col1, col2 = st.columns([1, 3])
            col1.write(f"**{task}**")
            col2.progress(min(progress_pct, 1.0))
            st.caption(f"Completed {int(completed_count)} out of the last 7 days")
    else:
        st.info("No data logged in the last 7 days yet.")
