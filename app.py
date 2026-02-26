import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

# Set page to wide mode and dark theme
st.set_page_config(page_title="Aero-Lab Mission Control", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; }
    .stButton>button:hover { border: 1px solid #4CAF50; }
    </style>
    """, unsafe_allow_state_usage=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛰️ Mission Control")
    page = st.radio("Select Module", ["Dashboard", "Code Library", "Live Upload", "GNSS Tools"])
    st.divider()
    st.info("Current Project: Thesis Research")

# --- MODULE 1: DASHBOARD ---
if page == "Dashboard":
    st.title("Welcome back, Jarvis.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Scripts", "4", "+1")
    col2.metric("Last GNSS Sync", "2h ago")
    col3.metric("System Status", "Optimal", delta_color="normal")
    
    st.subheader("Recent Activity")
    st.write("Your most recent plots will appear here once you run a script.")

# --- MODULE 2: CODE LIBRARY (Pre-loaded for easy testing) ---
elif page == "Code Library":
    st.title("📚 Research Library")
    st.write("Select a pre-saved script to run instantly.")
    
    lib_choice = st.selectbox("Choose Script", ["Eigenvalue Visualizer", "Inverted Pendulum Sim", "PW2000 Thrust Curve"])
    
    if st.button("Execute Script"):
        if lib_choice == "Eigenvalue Visualizer":
            # --- EIGENVALUE CODE START ---
            A = np.array([[2, 1], [1, 2]])
            vals, vecs = np.linalg.eig(A)
            st.success(f"Calculated Eigenvalues: {vals}")
            fig = px.scatter(x=[0, vecs[0,0]], y=[0, vecs[1,0]], title="Eigenvector Direction")
            st.plotly_chart(fig)
            # --- EIGENVALUE CODE END ---

# --- MODULE 3: LIVE UPLOAD (For new files from phone) ---
elif page == "Live Upload":
    st.title("📥 Mobile Upload")
    uploaded_file = st.file_uploader("Drop a .py or .csv file here", type=['py', 'csv'])
    if uploaded_file:
        st.write("Processing file...")
        # (Rest of your upload logic here)

# --- MODULE 4: GNSS TOOLS ---
elif page == "GNSS Tools":
    st.title("📡 GNSS Analysis")
    st.warning("Connect your Google Drive or upload a log file to begin.")
