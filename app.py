import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

# 1. Page Configuration for 'App' Feel
st.set_page_config(page_title="Aero-Lab Mission Control", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1e1e26; color: #00d4ff; border: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar for Navigation
with st.sidebar:
    st.title("🛰️ Jarvis Aero-Lab")
    mode = st.radio("Select Mode", ["Live Analysis Hub", "Pre-loaded Lab"])
    st.divider()
    st.info("Upload any .py or .csv from your phone to start.")

# --- MODE 1: LIVE ANALYSIS HUB (The 'Just Upload' Mode) ---
if mode == "Live Analysis Hub":
    st.title("📥 Instant Upload & Plot")
    st.write("Upload your Python scripts or Data files to visualize them instantly.")
    
    uploaded_file = st.file_uploader("Choose a file from your phone", type=['py', 'csv'])
    
    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
        st.write(file_details)

        # CASE A: It's a Python Script (like your Eigenvalue or Stiffness code)
        if uploaded_file.name.endswith('.py'):
            st.subheader("Executing Script...")
            code = uploaded_file.getvalue().decode("utf-8")
            
            # This creates a "sandbox" to run your code
            try:
                # We use exec() to run the code you uploaded
                # To see plots, ensure your script uses st.pyplot() or st.plotly_chart()
                exec(code) 
                st.success("Analysis Complete")
            except Exception as e:
                st.error(f"Execution Error: {e}")

        # CASE B: It's a Data File (CSV)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.subheader("Data Visualization")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                x_axis = st.selectbox("X Axis", df.columns)
                y_axis = st.selectbox("Y Axis", df.columns)
                plot_type = st.radio("Type", ["Line", "Scatter", "Bar"])
            
            with col2:
                if plot_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, template="plotly_dark")
                elif plot_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis, template="plotly_dark")
                else:
                    fig = px.bar(df, x=x_axis, y=y_axis, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

# --- MODE 2: PRE-LOADED LAB (For your regular experiments) ---
else:
    st.title("📚 Permanent Lab Modules")
    st.write("These stay here forever so you don't have to upload them.")
    # (You can paste your Eigenvalue/Stiffness code here as permanent features)
    st.info("Check back here for your saved thesis modules.")
