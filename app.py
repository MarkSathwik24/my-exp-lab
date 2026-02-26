import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
import contextlib
import os
import time
import sys

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
    
    /* The Jarvis 'Landing Pad' Upgrade for File Uploads */
    [data-testid="stFileUploadDropzone"] {
        min-height: 200px !important;
        border: 2px dashed #00d4ff !important;
        background-color: rgba(0, 212, 255, 0.05) !important;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease-in-out;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(0, 212, 255, 0.15) !important;
        border: 2px solid #00d4ff !important;
    }
    
    /* IDE Text Area Styling */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace !important;
        background-color: #1e1e26 !important;
        color: #00ffcc !important;
        border: 1px solid #00d4ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CORE EXECUTION ENGINE ---
def run_analysis_sandbox(file_name, file_bytes, user_inputs=""):
    if file_name.endswith('.py'):
        code = file_bytes.decode("utf-8")
        output_buffer = io.StringIO()
        input_buffer = io.StringIO(user_inputs + "\n" * 20) 
        sandbox_namespace = {}
        
        # Override standard input for input() functions
        original_stdin = sys.stdin
        sys.stdin = input_buffer
        
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
            
        finally:
            sys.stdin = original_stdin
            
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
    mode = st.radio("Select Module", ["💻 Live IDE (Compiler)", "📥 File Hub", "🗄️ Weekly Archive"])
    st.divider()
    st.metric("Files in 7-Day Storage", len(os.listdir(ARCHIVE_DIR)))

# --- MODULE 1: LIVE IDE (PSEUDO COMPILER) ---
if mode == "💻 Live IDE (Compiler)":
    st.title("💻 Jarvis In-Browser IDE")
    st.write("Write, edit, and compile Python code directly on the server.")
    
    # Pre-filled with a test script
    default_code = """import numpy as np
import matplotlib.pyplot as plt

print("Jarvis Compiler Online.")
name = input("Enter simulation name: ")
print(f"Running simulation: {name}")

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y, color='cyan')
plt.title(f"{name} Results")
plt.grid(True)
plt.show()"""

    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_code = st.text_area("Code Editor", value=default_code, height=350)
        
    with col2:
        terminal_input = st.text_area("⌨️ Terminal Inputs", placeholder="Enter inputs line by line for input()", height=150)
        st.write("") # Spacing
        if st.button("🚀 Compile & Run", use_container_width=True):
            st.session_state['compile_trigger'] = True

    if st.session_state.get('compile_trigger'):
        st.divider()
        st.subheader("⚙️ Execution Results")
        # Convert the string to bytes to feed into our engine seamlessly
        code_bytes = user_code.encode("utf-8")
        run_analysis_sandbox("ide_session.py", code_bytes, user_inputs=terminal_input)
        st.session_state['compile_trigger'] = False

# --- MODULE 2: FILE HUB ---
elif mode == "📥 File Hub":
    st.title("📥 Upload & Execute")
    uploaded_file = st.file_uploader("Drop a .py or .csv file here", type=['py', 'csv'])

    if uploaded_file is not None:
        f_name = uploaded_file.name
        f_bytes = uploaded_file.getvalue()
        
        if st.button(f"💾 Save '{f_name}' to Weekly Archive"):
            with open(os.path.join(ARCHIVE_DIR, f_name), "wb") as f:
                f.write(f_bytes)
            st.success(f"Saved! You can now run this directly from the Archive tab.")

        st.divider()
        terminal_input = ""
        if f_name.endswith('.py'):
            terminal_input = st.text_area("⌨️ Terminal Inputs (Optional)", placeholder="Provide inputs line by line")
            
        if st.button("🚀 Execute Script"):
            run_analysis_sandbox(f_name, f_bytes, user_inputs=terminal_input)

# --- MODULE 3: WEEKLY DATA ARCHIVE ---
elif mode == "🗄️ Weekly Archive":
    st.title("🗄️ 7-Day Rolling Archive")
    saved_files = os.listdir(ARCHIVE_DIR)
    
    if not saved_files:
        st.info("Archive is empty. Upload a file in the File Hub to save it here.")
    else:
        for f_name in saved_files:
            file_path = os.path.join(ARCHIVE_DIR, f_name)
            days_old = (current_time - os.path.getmtime(file_path)) / 86400
            
            with st.expander(f"📄 {f_name} (Expires in {7 - int(days_old)} days)"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("Load Script", key=f"run_{f_name}"):
                        st.session_state['run_file'] = file_path
                        st.session_state['run_name'] = f_name
                with c2:
                    with open(file_path, "rb") as file:
                        st.download_button("📥 Download", data=file, file_name=f_name, key=f"dl_{f_name}")
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{f_name}"):
                        os.remove(file_path)
                        if st.session_state.get('run_file') == file_path:
                            del st.session_state['run_file']
                        st.rerun()
                        
        if 'run_file' in st.session_state and os.path.exists(st.session_state['run_file']):
            st.divider()
            head_col1, head_col2 = st.columns([4, 1])
            head_col1.subheader(f"🟢 Active Session: {st.session_state['run_name']}")
            if head_col2.button("❌ Close Session"):
                del st.session_state['run_file']
                del st.session_state['run_name']
                st.rerun()
                
            if 'run_file' in st.session_state:
                terminal_input = ""
                if st.session_state['run_name'].endswith('.py'):
                    terminal_input = st.text_area("⌨️ Terminal Inputs (Optional)", key="archive_input")
                    
                if st.button("🚀 Execute Script", key="archive_exec"):
                    with open(st.session_state['run_file'], "rb") as file:
                        run_analysis_sandbox(st.session_state['run_name'], file.read(), user_inputs=terminal_input)
