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
st.set_page_config(page_title="Jarvis | MATLAB Environment", layout="wide", initial_sidebar_state="expanded")

ARCHIVE_DIR = "weekly_archive"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

current_time = time.time()
for filename in os.listdir(ARCHIVE_DIR):
    file_path = os.path.join(ARCHIVE_DIR, filename)
    if os.path.isfile(file_path):
        if (current_time - os.path.getmtime(file_path)) > 604800: 
            os.remove(file_path)

# MATLAB Dark Mode + Jarvis Aesthetics
st.markdown("""
    <style>
    .main { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Buttons */
    .stButton>button { width: 100%; border-radius: 4px; background-color: #00539c; color: #ffffff; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #0078d7; color: #ffffff; }
    
    /* Code Editor & Text Areas */
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #252526 !important; color: #ce9178 !important; border: 1px solid #3c3c3c !important; }
    
    /* Dropzone */
    [data-testid="stFileUploadDropzone"] { min-height: 150px !important; border: 2px dashed #0078d7 !important; background-color: #252526 !important; }
    
    /* Command Window Styling */
    .command-window { font-family: 'Courier New', Courier, monospace; background-color: #000000; color: #cccccc; padding: 15px; border-radius: 4px; border: 1px solid #3c3c3c; white-space: pre-wrap; height: 250px; overflow-y: auto; }
    .prompt { color: #f0a30a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CORE EXECUTION ENGINE ---
def run_analysis_sandbox(file_name, file_bytes, user_inputs=""):
    if file_name.endswith('.py'):
        code = file_bytes.decode("utf-8")
        output_buffer = io.StringIO()
        input_buffer = io.StringIO(user_inputs + "\n" * 20) 
        sandbox_namespace = {}
        
        original_stdin = sys.stdin
        sys.stdin = input_buffer
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                exec(code, globals(), sandbox_namespace)
            
            terminal_output = output_buffer.getvalue()
            
            # Display as a MATLAB Command Window
            st.markdown("### Command Window")
            if terminal_output:
                formatted_output = f"<div class='command-window'><span class='prompt'>>> </span>Executing {file_name}...\n\n{terminal_output}</div>"
                st.markdown(formatted_output, unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='command-window'><span class='prompt'>>> </span>Executing {file_name}...\n\n[No printed output]</div>", unsafe_allow_html=True)
                
            fig_nums = plt.get_fignums()
            if fig_nums or any(isinstance(v, go.Figure) for v in sandbox_namespace.values()):
                st.markdown("### Figure Window")
                for i in fig_nums:
                    st.pyplot(plt.figure(i))
                    plt.close(plt.figure(i))
                    
                for var_name, var_value in sandbox_namespace.items():
                    if isinstance(var_value, go.Figure):
                        st.plotly_chart(var_value, use_container_width=True)
                    
        except Exception as e:
            st.markdown(f"<div class='command-window'><span class='prompt'>>> </span><span style='color: #f48771;'>Error: {e}</span></div>", unsafe_allow_html=True)
            
        finally:
            sys.stdin = original_stdin
            
    elif file_name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
        st.markdown("### Workspace Variables (DataFrame)")
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
    mode = st.radio("Environment", ["💻 Editor & Command Window", "📥 File Workspace", "🗄️ Current Folder (Archive)"])
    st.divider()
    st.metric("Files in Current Folder", len(os.listdir(ARCHIVE_DIR)))

# --- MODULE 1: LIVE IDE (MATLAB STYLE) ---
if mode == "💻 Editor & Command Window":
    
    col_editor, col_workspace = st.columns([3, 1])
    
    with col_editor:
        st.markdown("### Editor")
        default_code = "# Equivalent to your .m script\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nx = np.linspace(0, 10, 100)\nplt.plot(x, np.sin(x))\nplt.grid(True)\nplt.title('Sine Wave')\nplt.show()"
        user_code = st.text_area("Script", value=default_code, height=400, label_visibility="collapsed")
        
    with col_workspace:
        st.markdown("### Workspace Inputs")
        st.write("If using `input()`, list variables here.")
        terminal_input = st.text_area("Inputs", placeholder="e.g.,\n10\n[1, 2, 3]", height=315, label_visibility="collapsed")
        
        if st.button("▶ Run Script", use_container_width=True):
            st.session_state['compile_trigger'] = True

    if st.session_state.get('compile_trigger'):
        st.divider()
        code_bytes = user_code.encode("utf-8")
        run_analysis_sandbox("Untitled.py", code_bytes, user_inputs=terminal_input)
        st.session_state['compile_trigger'] = False

# --- MODULE 2: FILE HUB ---
elif mode == "📥 File Workspace":
    st.title("📥 Import Data & Scripts")
    uploaded_file = st.file_uploader("Select files to add to the path", type=['py', 'csv'])

    if uploaded_file is not None:
        f_name = uploaded_file.name
        f_bytes = uploaded_file.getvalue()
        
        if st.button(f"💾 Add '{f_name}' to Current Folder"):
            with open(os.path.join(ARCHIVE_DIR, f_name), "wb") as f:
                f.write(f_bytes)
            st.success(f"Added to path! Available in the Archive tab.")

        st.divider()
        terminal_input = ""
        if f_name.endswith('.py'):
            st.markdown("### Workspace Inputs")
            terminal_input = st.text_area("Inputs", placeholder="Line-by-line inputs")
            
        if st.button("▶ Run File"):
            run_analysis_sandbox(f_name, f_bytes, user_inputs=terminal_input)

# --- MODULE 3: WEEKLY DATA ARCHIVE ---
elif mode == "🗄️ Current Folder (Archive)":
    st.title("🗄️ Current Folder")
    saved_files = os.listdir(ARCHIVE_DIR)
    
    if not saved_files:
        st.info("Folder is empty.")
    else:
        for f_name in saved_files:
            file_path = os.path.join(ARCHIVE_DIR, f_name)
            
            with st.expander(f"📄 {f_name}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("▶ Run", key=f"run_{f_name}"):
                        st.session_state['run_file'] = file_path
                        st.session_state['run_name'] = f_name
                with c2:
                    with open(file_path, "rb") as file:
                        st.download_button("📥 Export", data=file, file_name=f_name, key=f"dl_{f_name}")
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{f_name}"):
                        os.remove(file_path)
                        if st.session_state.get('run_file') == file_path:
                            del st.session_state['run_file']
                        st.rerun()
                        
        if 'run_file' in st.session_state and os.path.exists(st.session_state['run_file']):
            st.divider()
            head_col1, head_col2 = st.columns([4, 1])
            head_col1.markdown(f"**🟢 Active Script:** {st.session_state['run_name']}")
            if head_col2.button("❌ Clear Workspace"):
                del st.session_state['run_file']
                del st.session_state['run_name']
                st.rerun()
                
            if 'run_file' in st.session_state:
                terminal_input = ""
                if st.session_state['run_name'].endswith('.py'):
                    terminal_input = st.text_area("Workspace Inputs", key="archive_input")
                    
                if st.button("▶ Execute", key="archive_exec"):
                    with open(st.session_state['run_file'], "rb") as file:
                        run_analysis_sandbox(st.session_state['run_name'], file.read(), user_inputs=terminal_input)
