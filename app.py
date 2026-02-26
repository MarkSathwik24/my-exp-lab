import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import os
import traceback

# --- 1. SYSTEM CONFIG & THEME STATE ---
st.set_page_config(page_title="Jarvis | Python IDE", layout="wide", initial_sidebar_state="expanded")

# Initialize Theme State
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark' # Default Jarvis theme

def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

# Dynamic CSS Injection based on Theme
if st.session_state.theme == 'dark':
    css = """
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #161b22 !important; color: #58d68d !important; border: 1px solid #30363d !important; }
    .stButton>button { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #30363d; border-color: #8b949e; color: #ffffff; }
    .terminal-output { background-color: #0d1117; color: #c9d1d9; padding: 15px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 10px; white-space: pre-wrap; }
    .terminal-source { color: #58a6ff; font-weight: bold; margin-bottom: 5px; }
    .terminal-error { color: #f85149; }
    </style>
    """
else:
    css = """
    <style>
    .main { background-color: #ffffff; color: #24292f; font-family: 'Courier New', Courier, monospace; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #f6f8fa !important; color: #0969da !important; border: 1px solid #d0d7de !important; }
    .stButton>button { background-color: #f3f4f6; color: #24292f; border: 1px solid #d0d7de; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #e5e7eb; border-color: #8c959f; color: #000000; }
    .terminal-output { background-color: #f6f8fa; color: #24292f; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de; margin-bottom: 10px; white-space: pre-wrap; }
    .terminal-source { color: #0969da; font-weight: bold; margin-bottom: 5px; }
    .terminal-error { color: #cf222e; }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

# --- 2. PERSISTENT PYTHON NAMESPACE & MEMORY ---
if 'namespace' not in st.session_state:
    st.session_state.namespace = {'np': np, 'plt': plt, 'pd': pd}

if 'terminal_history' not in st.session_state:
    st.session_state.terminal_history = [{
        "source": "System", 
        "text": "Jarvis Python Engine Initialized.\nReady for aerospace analysis.", 
        "figs": [], 
        "error": False
    }]

if 'editor_content' not in st.session_state:
    st.session_state.editor_content = "# Welcome to the Jarvis Python IDE\n# Write or upload your scripts here."

ARCHIVE_DIR = "jarvis_scripts"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

# --- 3. THE PYTHON EXECUTION ENGINE (PLOT FIX APPLIED) ---
def execute_python(code_str, source_name="Terminal"):
    output_buffer = io.StringIO()
    run_record = {"source": source_name, "text": "", "figs": [], "error": False}
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            try:
                result = eval(code_str, globals(), st.session_state.namespace)
                if result is not None:
                    print(result)
            except SyntaxError:
                exec(code_str, globals(), st.session_state.namespace)
                
        run_record["text"] = output_buffer.getvalue()
        
        # FIX: Capture plots as permanent image bytes, not fragile matplotlib objects
        fig_nums = plt.get_fignums()
        for i in fig_nums:
            fig = plt.figure(i)
            buf = io.BytesIO()
            # Force a white facecolor so plots are always readable in Dark Mode
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor='white')
            buf.seek(0)
            run_record["figs"].append(buf.getvalue())
            
    except Exception as e:
        run_record["text"] = traceback.format_exc(limit=0)
        run_record["error"] = True
        
    finally:
        st.session_state.terminal_history.append(run_record)
        plt.close('all') # Clear the plot memory safely

# --- 4. SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚙️ System Settings")
    if st.button("🌓 Toggle Light / Dark Mode"):
        toggle_theme()
        st.rerun()
    st.divider()
    st.metric("Scripts Saved", len(os.listdir(ARCHIVE_DIR)))

# --- 5. MAIN INTERFACE TABS ---
st.title("🛰️ Jarvis Python IDE")
tab_term, tab_edit, tab_files = st.tabs(["💻 Terminal", "📝 Editor", "🗄️ Saved Files"])

# --- TAB 1: TERMINAL & OUTPUT ---
with tab_term:
    st.markdown("### Execution Terminal")
    
    for entry in st.session_state.terminal_history:
        st.markdown(f"<div class='terminal-source'>&gt;&gt;&gt; Executed: {entry['source']}</div>", unsafe_allow_html=True)
        
        if entry["text"]:
            if entry["error"]:
                st.markdown(f"<div class='terminal-output terminal-error'>{entry['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='terminal-output'>{entry['text']}</div>", unsafe_allow_html=True)
                
        # Render the perfectly saved images
        if entry["figs"]:
            for fig_bytes in entry["figs"]:
                st.image(fig_bytes)
        st.divider()

    st.write("Live Python Prompt:")
    repl_input = st.chat_input("Enter Python command (e.g., print(np.pi))...")
    if repl_input:
        execute_python(repl_input, source_name="Command Line")
        st.rerun()
        
    if st.button("🧹 Clear Terminal History"):
        st.session_state.terminal_history = []
        st.rerun()

# --- TAB 2: EDITOR & UPLOADS ---
with tab_edit:
    col_upload, col_save = st.columns(2)
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload a .py file to Editor", type=['py'])
        if uploaded_file is not None:
            st.session_state.editor_content = uploaded_file.getvalue().decode("utf-8")
            st.success("File loaded into Editor!")

    current_code = st.text_area("Python Script", value=st.session_state.editor_content, height=400, label_visibility="collapsed")
    
    with col_save:
        save_name = st.text_input("Save as:", value="script.py")
        if st.button("💾 Save to Files (Tab 3)"):
            with open(os.path.join(ARCHIVE_DIR, save_name), "w") as f:
                f.write(current_code)
            st.success(f"Saved {save_name} to Saved Files.")

    if st.button("▶️ Run Editor Code", type="primary"):
        st.session_state.editor_content = current_code 
        execute_python(current_code, source_name="Editor Script")
        # Force a rerun so the terminal logs the output immediately
        st.rerun()

# --- TAB 3: SAVED FILES ---
with tab_files:
    st.markdown("### Saved Scripts")
    saved_files = os.listdir(ARCHIVE_DIR)
    
    if not saved_files:
        st.info("No files saved yet. Create one in the Editor tab.")
    else:
        for f_name in saved_files:
            file_path = os.path.join(ARCHIVE_DIR, f_name)
            
            with st.expander(f"🐍 {f_name}"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    if st.button("▶️ Run", key=f"run_{f_name}"):
                        with open(file_path, "r") as f:
                            script_code = f.read()
                        execute_python(script_code, source_name=f_name)
                        st.rerun()
                        
                with c2:
                    if st.button("📝 Edit", key=f"edit_{f_name}"):
                        with open(file_path, "r") as f:
                            st.session_state.editor_content = f.read()
                        st.success("Loaded into Editor! Switch to Tab 2.")
                        
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{f_name}"):
                        os.remove(file_path)
                        st.rerun()
