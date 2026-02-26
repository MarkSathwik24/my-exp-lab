import streamlit as st
import plotly.express as px
import pandas as pd
import io

st.set_page_config(page_title="Aero-GNSS Lab", layout="wide")

st.title("🚀 Personal Aerospace Analysis Lab")
st.markdown("Upload your Python analysis scripts or data files to generate interactive visualizations.")

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Center")
    uploaded_file = st.file_uploader("Choose a Python script (.py) or Data (.csv)", type=['py', 'csv'])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.py'):
        st.subheader(f"Executing: {uploaded_file.name}")
        code = uploaded_file.getvalue().decode("utf-8")
        st.code(code, language='python')
        try:
            exec(code)
            st.success("Script executed successfully!")
        except Exception as e:
            st.error(f"Error in script: {e}")

    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        st.subheader("Interactive Visualization")
        columns = df.columns.tolist()
        x_axis = st.selectbox("Select X-axis", columns)
        y_axis = st.selectbox("Select Y-axis", columns)
        
        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Waiting for a file... You can upload your GNSS or propulsion scripts here.")
