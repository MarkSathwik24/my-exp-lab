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

# --- MODULE 2: CODE LIBRARY (Single-Page Layout) ---
elif page == "Code Library":
    st.title("📚 Interactive Eigen-Analysis")
    st.markdown("Adjust the matrix $A$ to see how eigenvectors (directions) and eigenvalues (scale) change.")

    # Create two columns for the 'App' layout
    # On mobile, these will stack: Controls on top, Plot on bottom
    control_col, plot_col = st.columns([1, 2])

    with control_col:
        st.subheader("🎛️ Matrix Controls")
        # Real-time sliders that trigger an instant plot update
        a11 = st.slider("a11 (Top Left)", -5.0, 5.0, 2.0, help="Change the horizontal stretch")
        a12 = st.slider("a12 (Top Right)", -5.0, 5.0, 1.0, help="Change the shear")
        a21 = st.slider("a21 (Bottom Left)", -5.0, 5.0, 1.0)
        a22 = st.slider("a22 (Bottom Right)", -5.0, 5.0, 2.0)

        # Mathematical Engine
        A = np.array([[a11, a12], [a21, a22]])
        try:
            vals, vecs = np.linalg.eig(A)
            
            st.info(f"**λ₁:** {vals[0].real:.2f} | **λ₂:** {vals[1].real:.2f}")
            if np.iscomplex(vals).any():
                st.warning("Complex Eigenvalues: Rotation detected!")
        except np.linalg.LinAlgError:
            st.error("Matrix is singular or computation failed.")

    with plot_col:
        import plotly.graph_objects as go
        
        fig = go.Figure()

        # Add a static grid for reference
        for i in range(-10, 11, 2):
            fig.add_shape(type="line", x0=i, y0=-10, x1=i, y1=10, line=dict(color="rgba(255,255,255,0.1)", width=1))
            fig.add_shape(type="line", x0=-10, y0=i, x1=10, y1=i, line=dict(color="rgba(255,255,255,0.1)", width=1))

        # Plot the Eigenvectors
        colors = ['#00d4ff', '#ff007f'] # Neon Blue and Pink for Jarvis theme
        for i in range(len(vals)):
            # Scale vector by its eigenvalue for visualization
            v = vecs[:, i].real * vals[i].real 
            
            fig.add_trace(go.Scatter(
                x=[0, v[0]], y=[0, v[1]],
                mode='lines+markers+text',
                name=f'v{i+1} (λ={vals[i].real:.2f})',
                text=["", f"v{i+1}"],
                textposition="top right",
                line=dict(color=colors[i], width=5),
                marker=dict(size=10, symbol="arrow-bar-up")
            ))

        # Final Plot Styling
        fig.update_layout(
            template="plotly_dark",
            height=500,
            xaxis=dict(range=[-10, 10], zeroline=True, showgrid=False),
            yaxis=dict(range=[-10, 10], zeroline=True, showgrid=False),
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=True
        )
        
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
