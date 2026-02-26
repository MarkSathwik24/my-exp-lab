import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
import contextlib
import os
import time

# --- 1. SYSTEM CONFIG & AUTO-CLEANUP ---
st.set_page_config(page_title="Jarvis Analysis Hub", layout="wide", initial_sidebar_state="expanded")

ARCHIVE_DIR = "weekly_archive"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

current_time = time.time()
for filename in os.listdir(ARCHIVE_DIR):
    file_path = os.path.join(ARCHIVE_DIR, filename)
    if os.path.isfile(file_path):
        if (current_time - os.path.getmtime(file_path)) > 604800: 
            os.remove(file_path)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1e1e26; color: #00d4ff; border: 1px solid #00d4ff; }
    .stButton>button:hover { background-color: #00d4ff; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CORE EXECUTION ENGINE ---
def run_analysis_sandbox(file_name, file_bytes):
    if file_name.endswith('.py'):
        code = file_bytes.decode("utf-8")
        output_buffer = io.StringIO()
        sandbox_namespace = {}
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                exec(code, globals(), sandbox_namespace)
            
            terminal_output = output_buffer.getvalue()
            if terminal_output:
                st.text_area("Terminal Output", terminal_output, height=150)
                
            fig_nums = plt.get_fignums()
            for i in fig_nums:
                st.pyplot(plt.figure(i))
                plt.close(plt.figure(i))
                
            for var_name, var_value in sandbox_namespace.items():
                if isinstance(var_value, go.Figure):
                    st.plotly_chart(var_value, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Execution Error in {file_name}: {e}")
            
    elif file_name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
        st.dataframe(df)
        if len(df.columns) >= 2:
            x_col = st.selectbox("X-Axis", df.columns, key=f"x_{file_name}")
            y_col = st.selectbox("Y-Axis", df.columns, key=f"y_{file_name}")
            import plotly.express as px
            fig = px.line(df, x=x_col, y=y_col, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛰️ Jarvis System")
    mode = st.radio("Select Module", ["Live Analysis Hub", "Weekly Data Archive"])
    st.divider()
    st.metric("Files in 7-Day Storage", len(os.listdir(ARCHIVE_DIR)))

# --- MODULE 1: LIVE ANALYSIS HUB ---
if mode == "Live Analysis Hub":
    st.title("📥 Universal Code & Data Hub")
    uploaded_file = st.file_uploader("Drop a .py or .csv file here", type=['py', 'csv'])

    if uploaded_file is not None:
        f_name = uploaded_file.name
        f_bytes = uploaded_file.getvalue()
        
        if st.button(f"💾 Save '{f_name}' to Weekly Archive"):
            with open(os.path.join(ARCHIVE_DIR, f_name), "wb") as f:
                f.write(f_bytes)
            st.success(f"Saved! You can now run this directly from the Archive tab.")

        st.divider()
        st.subheader(f"⚙️ Active Session: {f_name}")
        run_analysis_sandbox(f_name, f_bytes)

# --- MODULE 2: WEEKLY DATA ARCHIVE ---
elif mode == "Weekly Data Archive":
    st.title("🗄️ 7-Day Rolling Archive")
    saved_files = os.listdir(ARCHIVE_DIR)
    
    if not saved_files:
        st.info("Archive is empty. Upload a file in the Live Analysis Hub to save it here.")
    else:
        for f_name in saved_files:
            file_path = os.path.join(ARCHIVE_DIR, f_name)
            days_old = (current_time - os.path.getmtime(file_path)) / 86400
            
            with st.expander(f"📄 {f_name} (Expires in {7 - int(days_old)} days)"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🚀 Run in Lab", key=f"run_{f_name}"):
                        # Save to persistent memory
                        st.session_state['run_file'] = file_path
                        st.session_state['run_name'] = f_name
                with col2:
                    with open(file_path, "rb") as file:
                        st.download_button("📥 Download", data=file, file_name=f_name, key=f"dl_{f_name}")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{f_name}"):
                        os.remove(file_path)
                        if st.session_state.get('run_file') == file_path:
                            del st.session_state['run_file']
                        st.rerun()
                        
        # Check if a file is loaded in memory
        if 'run_file' in st.session_state and os.path.exists(st.session_state['run_file']):
            st.divider()
            
            # Create a header with a Close button to stop the session
            head_col1, head_col2 = st.columns([4, 1])
            head_col1.subheader(f"🟢 Active Session: {st.session_state['run_name']}")
            if head_col2.button("❌ Close Session"):
                del st.session_state['run_file']
                del st.session_state['run_name']
                st.rerun()
                
            # If the session wasn't just closed, run the file
            if 'run_file' in st.session_state:
                with open(st.session_state['run_file'], "rb") as file:
                    run_analysis_sandbox(st.session_state['run_name'], file.read())
