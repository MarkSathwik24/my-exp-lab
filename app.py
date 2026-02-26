import streamlit as st
import os
import plotly.express as px
import pandas as pd

# 1. Configuration
NOTES_DIR = "notes_vault"
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

st.set_page_config(page_title="Python Note App", layout="wide")

# 2. Sidebar: Folder and File Navigation
st.sidebar.title("📁 Notes Vault")

# List directories and files
def get_files(path):
    items = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".md") or f.endswith(".txt"):
                items.append(os.path.relpath(os.path.join(root, f), path))
    return items

all_notes = get_files(NOTES_DIR)
selected_note = st.sidebar.selectbox("Select a Note", ["+ New Note"] + sorted(all_notes))

# 3. Logic for Creating/Loading Notes
if selected_note == "+ New Note":
    new_name = st.text_input("Note Name (e.g., folder/note.md)")
    content = ""
    file_path = os.path.join(NOTES_DIR, new_name)
else:
    file_path = os.path.join(NOTES_DIR, selected_note)
    with open(file_path, "r") as f:
        content = f.read()

# 4. Main Area: The Editor
st.title(f"Editing: {selected_note}")
text_input = st.text_area("Write your Markdown here...", value=content, height=400)

if st.button("Save Note"):
    # Ensure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(text_input)
    st.success("Saved!")

# 5. The "Magic": Interactive Plots
st.divider()
st.subheader("📊 Interactive Data Preview")
if st.checkbox("Show Interactive Plot Demo"):
    # Example: Creating a plot from simple data
    df = pd.DataFrame({"x": range(10), "y": [x**2 for x in range(10)]})
    fig = px.line(df, x="x", y="y", title="Interactive Note Plot")
    st.plotly_chart(fig, use_container_width=True)
