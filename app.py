import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. SYSTEM CONFIG & SMART THEME ---
st.set_page_config(page_title="MARK SPACE | IDE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# --- 2. THEME ENGINE (TOTAL SYSTEM SYNC) ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Color Logic for Sidebar & Main Workspace
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent, text_faint = "#0d1117", "#ffffff", "#161b22", "#58a6ff", "#8b949e"
    sidebar_bg, btn_bg = "#0d1117", "#21262d"
else:
    bg, fg, editor_bg, accent, text_faint = "#ffffff", "#000000", "#f6f8fa", "#0969da", "#57606a"
    sidebar_bg, btn_bg = "#f6f8fa", "#f3f4f6"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {accent}33; }}
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{ color: {fg} !important; font-weight: bold; }}
    
    /* Chrome Tabs Visibility */
    button[role="tab"] {{ color: {text_faint} !important; background-color: {editor_bg} !important; }}
    button[role="tab"][aria-selected="true"] {{ color: {accent} !important; border-top: 2px solid {accent} !important; font-weight: bold !important; }}

    /* Circular Theme Toggle */
    .stButton>button[key="theme_toggle"] {{ 
        border-radius: 50% !important; width: 42px !important; height: 42px !important; 
        background: {btn_bg} !important; border: 1px solid {accent}44 !important;
        display: flex; align-items: center; justify-content: center;
    }}
    
    /* Editor & Terminal Window */
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; }}
    .terminal-window {{ background-color: #000000; color: #39ff14; padding: 15px; border-radius: 8px; border: 1px solid {accent}44; font-family: monospace; white-space: pre-wrap; }}
    
    /* Toggle & Labels */
    .stToggle, .stCheckbox, label {{ color: {fg} !important; font-weight: bold !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["main.py"]}
    st.session_state.file_contents = {"main.py": "x = float(input('Enter Num: '))\nprint(f'Double: {x*2}')"}

if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "main.py"}]

# --- 4. DIALOG: NEW FILE ---
@st.dialog("Create New File")
def create_file_pop():
    name = st.text_input("Filename", placeholder="aerospace_sim.py")
    c1, c2 = st.columns(2)
    if c1.button("CREATE", use_container_width=True):
        if name:
            name = name if name.endswith(".py") else f"{name}.py"
            if name not in st.session_state.vfs["root"]:
                st.session_state.vfs["root"].append(name)
                st.session_state.file_contents[name] = f"# {name}\n"
            
            # Smart Logic: Open in new Chrome-style Tab
            existing_ids = [nb["id"] for nb in st.session_state.notebooks if isinstance(nb, dict)]
            new_id = 1
            while new_id in existing_ids: new_id += 1
            st.session_state.notebooks.append({"id": new_id, "file": name})
            st.rerun()
    if c2.button("CANCEL", use_container_width=True): st.rerun()

# --- 5. SIDEBAR: WORKSPACE MANAGER ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='color:{fg}; margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme(); st.rerun()
    
    st.divider()
    workspace_mode = st.radio("WORKSPACE MODE", ["📊 Plotter Mode", "💻 Terminal Compiler"])
    
    st.divider()
    # SMART TAB ADDITION
    if st.button("➕ NEW TAB", use_container_width=True):
        existing_ids = [nb["id"] for nb in st.session_state.notebooks if isinstance(nb, dict)]
        new_id = 1
        while new_id in existing_ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "scratchpad.py"})
        if "scratchpad.py" not in st.session_state.file_contents:
            st.session_state.file_contents["scratchpad.py"] = "# Scratchpad\n"
        st.rerun()

    if st.button("📄 NEW FILE", use_container_width=True): create_file_pop()
    
    st.divider()
    st.markdown("### 📁 EXPLORER")
    for f in st.session_state.vfs["root"]:
        c1, c2 = st.columns([5, 1])
        if c1.button(f"📄 {f}", key=f"sb_{f}", use_container_width=True):
            existing_ids = [nb["id"] for nb in st.session_state.notebooks if isinstance(nb, dict)]
            new_id = 1
            while new_id in existing_ids: new_id += 1
            st.session_state.notebooks.append({"id": new_id, "file": f})
            st.rerun()
        if c2.button("✕", key=f"del_{f}"):
            st.session_state.vfs["root"].remove(f); st.rerun()

# --- 6. MAIN INTERFACE ---
if not st.session_state.notebooks:
    st.info("Click '➕ NEW TAB' to begin.")
else:
    # Safely handle tab names for Chrome-style numbering
    tab_labels = [f"Tab {nb['id']}" if isinstance(nb, dict) else f"Tab {i+1}" for i, nb in enumerate(st.session_state.notebooks)]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        if not isinstance(nb, dict): continue
        with ui_tabs[i]:
            fname = nb["file"]
            t_id = nb["id"]
            
            # Tab Header
            th1, th2 = st.columns([10, 1])
            th1.markdown(f"**WORKSPACE:** `Tab {t_id}` | **FILE:** `{fname}`")
            if th2.button("✕", key=f"cls_{t_id}"):
                st.session_state.notebooks.pop(i)
                st.rerun()

            # Editor
            code = st.text_area("EDITOR", value=st.session_state.file_contents.get(fname, ""), height=250, key=f"ed_{t_id}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code

            # Input Handling (Fix for String to Float Error)
            stdin_data = ""
            if workspace_mode == "💻 Terminal Compiler":
                st.write("⌨️ **TERMINAL INPUT**")
                stdin_data = st.text_area("Type inputs here...", key=f"in_{t_id}", height=80, label_visibility="collapsed")
            
            if st.button("▶️ RUN EXECUTION", type="primary", use_container_width=True, key=f"run_{t_id}"):
                output_buffer = io.StringIO()
                # Pre-pad with 100 newlines to ensure float() never hits an empty string
                sys.stdin = io.StringIO(stdin_data + "\n" * 100)
                
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    res = output_buffer.getvalue()
                    
                    if workspace_mode == "💻 Terminal Compiler":
                        st.markdown(f"<div class='terminal-window'>$ python {fname}\n{res}</div>", unsafe_allow_html=True)
                    else:
                        if res: st.markdown(f"<div class='terminal-window' style='background:#161b22; color:white;'>{res}</div>", unsafe_allow_html=True)
                        for fn in plt.get_fignums():
                            st.pyplot(plt.figure(fn))
                            plt.close(plt.figure(fn))
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
