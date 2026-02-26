import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import os
import traceback

# --- 1. SYSTEM CONFIG & PYTHONIC STYLING ---
st.set_page_config(page_title="Jarvis | Python IDE", layout="wide", initial_sidebar_state="collapsed")

# Jarvis Dark Terminal Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #161b22 !important; color: #58d68d !important; border: 1px solid #30363d !important; }
    .stButton>button { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; }
    .stButton>button:hover { background-color: #30363d; border-color: #8b949e; }
    .terminal-output { background-color: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 10px; }
    .terminal-source { color: #58a6ff; font-weight: bold; margin-bottom: 5px; }
    .terminal-error { color: #f85149; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PERSISTENT PYTHON NAMESPACE & MEMORY ---
# This dictionary is the "Memory" of your Python environment
if 'namespace' not in st.session_state:
    st.session_state.namespace = {'np': np, 'plt': plt, 'pd': pd}

# This stores the execution history (text and plots) for Tab 1
if 'terminal_history' not in st.session_state:
    st.session_state.terminal_history = []

if 'editor_content' not in st.session_state:
    st.session_state.editor_content = "# Welcome to the Jarvis Python IDE\\n# Write or upload your aerospace scripts here."

# Directory for Tab 3
ARCHIVE_DIR = "jarvis_scripts"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

# --- 3. THE PYTHON EXECUTION ENGINE ---
def execute_python(code_str, source_name="Terminal"):
    output_buffer = io.StringIO()
    run_record = {"source": source_name, "text": "", "figs": [], "error": False}
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            # Attempt to evaluate as a single expression first (e.g., typing a variable name)
            try:
                result = eval(code_str, globals(), st.session_state.namespace)
                if result is not None:
                    print(result)
            except SyntaxError:
                # If it's a block of code, execute it normally
                exec(code_str, globals(), st.session_state.namespace)
                
        run_record["text"] = output_buffer.getvalue()
        
        # Capture any Matplotlib plots generated during execution
        fig_nums = plt.get_fignums()
        for i in fig_nums:
            fig = plt.figure(i)
            run_record["figs"].append(fig)
            
    except Exception as e:
        run_record["text"] = traceback.format_exc(limit=0)
        run_record["error"] = True
        
    finally:
        st.session_state.terminal_history.append(run_record)
        # Clear plots from memory so they don't duplicate on the next run
        plt.close('all') 

# --- 4. MAIN INTERFACE TABS ---
st.title("🛰️ Jarvis Python IDE")
tab_term, tab_edit, tab_files = st.tabs(["💻 Terminal", "📝 Editor", "🗄️ Saved Files"])

# --- TAB 1: TERMINAL & OUTPUT ---
with tab_term:
    st.markdown("### Execution Terminal")
    
    # Render History
    for entry in st.session_state.terminal_history:
        st.markdown(f"<div class='terminal-source'>&gt;&gt;&gt; Executed: {entry['source']}</div>", unsafe_allow_html=True)
        
        if entry["text"]:
            if entry["error"]:
                st.markdown(f"<div class='terminal-output terminal-error'>{entry['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='terminal-output'>{entry['text']}</div>", unsafe_allow_html=True)
                
        if entry["figs"]:
            for fig in entry["figs"]:
                st.pyplot(fig)
        st.divider()

    # REPL Input (Read-Eval-Print Loop)
    st.write("Live Python Prompt:")
    repl_input = st.chat_input("Enter Python command...")
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
        # Upload code straight into the editor
        uploaded_file = st.file_uploader("Upload a .py file to Editor", type=['py'])
        if uploaded_file is not None:
            # Read file and put it in the text area
            st.session_state.editor_content = uploaded_file.getvalue().decode("utf-8")
            st.success("File loaded into Editor!")

    # The actual code editor
    current_code = st.text_area("Python Script", value=st.session_state.editor_content, height=400)
    
    with col_save:
        save_name = st.text_input("Save as:", value="script.py")
        if st.button("💾 Save to Files (Tab 3)", use_container_width=True):
            with open(os.path.join(ARCHIVE_DIR, save_name), "w") as f:
                f.write(current_code)
            st.success(f"Saved {save_name} to Saved Files.")

    if st.button("▶️ Run Editor Code", type="primary", use_container_width=True):
        st.session_state.editor_content = current_code # keep the typed code
        execute_python(current_code, source_name="Editor Script")
        st.success("Executed! Switch to the 💻 Terminal tab to see the output.")

# --- TAB 3: SAVED FILES ---
with tab_files:
    st.markdown("### Saved Scripts")
    st.write("Run your saved scripts directly. Outputs will route to the Terminal.")
    
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
                        st.success("Executed! Check the 💻 Terminal tab.")
                        
                with c2:
                    # Let the user push the saved file back into the Editor to modify it
                    if st.button("📝 Edit", key=f"edit_{f_name}"):
                        with open(file_path, "r") as f:
                            st.session_state.editor_content = f.read()
                        st.success("Loaded into Editor! Switch to Tab 2 to modify.")
                        
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{f_name}"):
                        os.remove(file_path)
                        st.rerun()
