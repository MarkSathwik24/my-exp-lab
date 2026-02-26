import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

# 1. Set page config
st.set_page_config(page_title="Aero-Lab Mission Control", layout="wide", initial_sidebar_state="expanded")

# 2. Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; }
    .stButton>button:hover { border: 1px solid #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Navigation
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
    st.write("System is ready for aerospace analysis.")

# --- MODULE 2: CODE LIBRARY (Optimized for Real-Time Changes) ---
elif page == "Code Library":
    st.title("📚 Research Library")
    
    lib_choice = st.selectbox("Choose Script", ["Interactive Eigenvalue Viz", "PW2000 Thrust Tracker"])
    
    if lib_choice == "Interactive Eigenvalue Viz":
        st.sidebar.markdown("### 🎛️ Matrix Controls")
        # Placing sliders in the sidebar allows the plot on the right to update live
        a11 = st.sidebar.slider("a11 (Top Left)", -5.0, 5.0, 2.0)
        a12 = st.sidebar.slider("a12 (Top Right)", -5.0, 5.0, 1.0)
        a21 = st.sidebar.slider("a21 (Bottom Left)", -5.0, 5.0, 1.0)
        a22 = st.sidebar.slider("a22 (Bottom Right)", -5.0, 5.0, 2.0)

        # Calculation
        A = np.array([[a11, a12], [a21, a22]])
        vals, vecs = np.linalg.eig(A)

        # Layout for results
        col1, col2 = st.columns(2)
        with col1:
            st.latex(f"A = \\begin{{bmatrix}} {a11} & {a12} \\\\ {a21} & {a22} \\end{{bmatrix}}")
        with col2:
            st.write(f"**λ₁:** {vals[0]:.2f} | **λ₂:** {vals[1]:.2f}")

        # Live Plotly Chart
        fig = px.scatter(
            x=[0, vecs[0,0] * vals[0], 0, vecs[0,1] * vals[1]], 
            y=[0, vecs[1,0] * vals[0], 0, vecs[1,1] * vals[1]],
            title="Principal Directions (Eigenvectors)",
            labels={'x': 'X-Axis', 'y': 'Y-Axis'},
            template="plotly_dark"
        )
        # Adding lines to the vectors
        fig.add_trace(px.line(x=[0, vecs[0,0]*vals[0]], y=[0, vecs[1,0]*vals[0]]).data[0])
        fig.add_trace(px.line(x=[0, vecs[0,1]*vals[1]], y=[0, vecs[1,1]*vals[1]]).data[0])
        
        st.plotly_chart(fig, use_container_width=True)

# --- MODULE 3: LIVE UPLOAD (FIXED LOGIC) ---
elif page == "Live Upload":
    st.title("📥 Mobile Upload")
    uploaded_file = st.file_uploader("Drop a .py or .csv file here", type=['py', 'csv'])
    
    if uploaded_file:
        # Check if it's a Python file
        if uploaded_file.name.endswith('.py'):
            st.success(f"Running {uploaded_file.name}...")
            code = uploaded_file.getvalue().decode("utf-8")
            try:
                exec(code) # This actually runs your code!
            except Exception as e:
                st.error(f"Error in script: {e}")
        
        # Check if it's a CSV file
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("### Data Preview", df.head())
            x_col = st.selectbox("X-Axis", df.columns)
            y_col = st.selectbox("Y-Axis", df.columns)
            fig = px.line(df, x=x_col, y=y_col, template="plotly_dark")
            st.plotly_chart(fig)

# --- MODULE 4: GNSS TOOLS ---
elif page == "GNSS Tools":
    st.title("📡 GNSS Analysis")
    st.warning("Module under development. Link your IITKGP research data here.")
