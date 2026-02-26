import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
import contextlib
import os
import time
from datetime import datetime

# --- 1. SYSTEM CONFIG & AUTO-CLEANUP ---
st.set_page_config(page_title="Jarvis Analysis Hub", layout="wide", initial_sidebar_state="expanded")

# Create a hidden folder on the server to store your weekly data
ARCHIVE_DIR = "weekly_archive"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

# AUTO-REFRESH LOGIC: Delete files older than 7 days
current_time = time.time()
for filename in os.listdir(ARCHIVE_DIR):
    file_path = os.path.join(ARCHIVE_DIR, filename)
    if os.path.isfile(file_path):
        file_age_seconds = current_time - os.path.getmtime(file_path)
        if file_age_seconds > 604800: # 7 days in seconds
            os.remove(file_path)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1e1e26; color: #00d4ff; border: 1px solid #00d4ff; }
    .stButton>button:hover { background-color: #00d4ff; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🛰️ Jarvis System")
    mode = st.radio("Select Module", ["Live Analysis Hub", "Weekly Data Archive"])
    st.divider()
    
    # Show active storage count
    file_count = len(os.listdir(ARCHIVE_DIR))
    st.metric("Files in 7-Day Storage", file_count)

# --- MODULE 1: LIVE ANALYSIS HUB ---
if mode == "Live Analysis Hub":
    st.title("📥 Universal Code & Data Hub")
    st.write("Upload your Python scripts or CSV data. You can save them to your weekly archive after uploading.")

    uploaded_file = st.file_uploader("Drop a .py or .csv file here", type=['py', 'csv'])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_bytes = uploaded_file.getvalue()
        
        # Save to Archive Button
        if st.button(f"💾 Save '{file_name}' to Weekly Archive"):
            save_path = os.path.join(ARCHIVE_DIR, file_name)
            with open(save_path, "wb") as f:
                f.write(file_bytes)
            st.success(f"Saved! This file will be available for 7 days.")

        st.divider()
        
        # --- IF PYTHON SCRIPT ---
        if file_name.endswith('.py'):
            st.subheader("Executing Script...")
            code = file_bytes.decode("utf-8")
            output_buffer = io.StringIO()
            sandbox_namespace = {}
            
            try:
                with contextlib.redirect_stdout(output_buffer):
                    exec(code, globals(), sandbox_namespace)
                
                terminal_output = output_buffer.getvalue()
                if terminal_output:
                    st.text_area("Terminal Output", terminal_output, height=150)
                    
                # Intercept Matplotlib
                fig_nums = plt.get_fignums()
                for i in fig_nums:
                    st.pyplot(plt.figure(i))
                    plt.close(plt.figure(i))
                    
                # Intercept Plotly
                for var_name, var_value in sandbox_namespace.items():
                    if isinstance(var_value, (go.Figure)):
                        st.plotly_chart(var_value, use_container_width=True)
                        
            except Exception as e:
                st.error(f"Execution Error: {e}")
                
        # --- IF CSV DATA ---
        elif file_name.endswith('.csv'):
            st.subheader("Data Preview")
            df = pd.read_csv(io.BytesIO(file_bytes))
            st.dataframe(df.head())

# --- MODULE 2: WEEKLY DATA ARCHIVE ---
elif mode == "Weekly Data Archive":
    st.title("🗄️ 7-Day Rolling Archive")
    st.write("Files saved here automatically delete 1 week after they are uploaded.")
    
    saved_files = os.listdir(ARCHIVE_DIR)
    
    if len(saved_files) == 0:
        st.info("Your archive is currently empty. Upload and save a file in the Live Analysis Hub.")
    else:
        for f_name in saved_files:
            file_path = os.path.join(ARCHIVE_DIR, f_name)
            # Get file age
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            days_old = (current_time - os.path.getmtime(file_path)) / 86400
            
            # Display file card
            with st.expander(f"📄 {f_name} (Uploaded: {file_time.strftime('%b %d')} - Expires in {7 - int(days_old)} days)"):
                col1, col2 = st.columns(2)
                with col1:
                    # Let user download the file back to their phone
                    with open(file_path, "rb") as file:
                        st.download_button(label="📥 Download File", data=file, file_name=f_name)
                with col2:
                    # Let user force-delete early
                    if st.button("🗑️ Delete Now", key=f"del_{f_name}"):
                        os.remove(file_path)
                        st.rerun() # Refresh the page immediately
