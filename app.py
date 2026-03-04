import streamlit as st
import datetime

st.title("Daily Path Tracker")

# Get today's date
today = datetime.date.today().strftime("%B %d, %Y")
st.subheader(f"Progress for {today}")

# Create 6 checkboxes
tasks = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"]
completed = 0

for task in tasks:
    if st.checkbox(task):
        completed += 1

# Progress Bar
progress = completed / 6
st.progress(progress)
st.write(f"You are {int(progress*100)}% along the path today!")
