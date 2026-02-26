import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Setup for 'App' Feel
st.set_page_config(page_title="Aero-Lab Mission Control", layout="wide")

# Custom CSS for the 'Jarvis' Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1e1e26; color: #00d4ff; border: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Navigation
with st.sidebar:
    st.title("🛰️ Jarvis Aero-Lab")
    mode = st.radio("Select Mode", ["Live Analysis Hub", "Research Library"])
    st.divider()
    st.info("Upload any .py or .csv from your phone to begin.")

# --- MODE 1: LIVE ANALYSIS HUB ---
if mode == "Live Analysis Hub":
    st.title("📥 Instant Upload & Plot")
    uploaded_file = st.file_uploader("Upload a Python script or Data file", type=['py', 'csv'])
    
    if uploaded_file is not None:
        # Display file info for tracking
        st.json({"FileName": uploaded_file.name, "FileType": uploaded_file.type})

        # Logic for Python Scripts
        if uploaded_file.name.endswith('.py'):
            st.subheader("Executing Script...")
            code = uploaded_file.getvalue().decode("utf-8")
            try:
                # Executing the uploaded code in the app context
                exec(code) 
                st.success("Execution Successful")
            except Exception as e:
                st.error(f"Execution Error: {e}")

        # Logic for Data Files
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.subheader("Data Visualization")
            x_axis = st.selectbox("X Axis", df.columns)
            y_axis = st.selectbox("Y Axis", df.columns)
            fig = px.line(df, x=x_axis, y=y_axis, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# --- MODE 2: RESEARCH LIBRARY ---
else:
    st.title("📚 Permanent Lab")
    st.write("Your saved thesis modules will appear here.")
