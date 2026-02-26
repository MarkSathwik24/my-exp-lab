import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. SYSTEM CONFIG & DYNAMIC THEME ---
st.set_page_config(page_title="MARK SPACE | IDE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["main.py"]}
    st.session_state.file_contents = {"main.py": "print('Welcome to MARK SPACE')\n# Start coding here"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {"Tab 1": "main.py"}
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Enhanced Color Palette
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent, sidebar_bg = "#0d1117", "#e6edf3", "#161b22", "#58a6ff", "#010409"
    term_bg, term_fg = "#000000", "#39ff14"
else:
    bg, fg, editor_bg, accent, sidebar_bg = "#ffffff", "#24292f", "#f6f8fa", "#0969da", "#f6f8fa"
    term_bg, term_fg = "#f6f8fa", "#1a1a1b"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {accent}33; }}
    
    /* Circle Theme Toggle */
    .stButton>button[key="theme_toggle"] {{ 
        border-radius: 50% !important; width: 42px !important; height: 42px !important; 
        padding: 0 !important; background: {editor_bg} !important; border: 1px solid {accent}44 !important;
    }}
    
    /* Chrome-style Tabs */
    button[role="tab"] {{ color: {fg} !important; background-color: {editor_bg} !important; border-radius: 8px 8px 0 0 !important; }}
    button[role="tab"][aria-selected="true"] {{ border-top: 3px solid {accent} !important; font-weight: bold !important; color: {accent} !important; }}

    /* Code Editor & Command Window */
    .stTextArea textarea {{ font-family: 'Fira Code', 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; border-radius: 8px; }}
    .terminal-window {{ background-color: {term_bg}; color: {term_fg}; padding: 15px; border-radius: 8px; border: 1px solid {accent}44; font-family: monospace; white-space: pre-wrap; }}
</style>
""", unsafe_allow_html=True)

# --- 2. FILE DIALOG ---
@st.dialog("Create New File")
def create_file_pop():
    name = st.text_input("Filename", placeholder="script.py")
    c1, c2 = st.columns(2)
    if c1.button("CREATE", use_container_width=True):
        if name:
            name = name if name.endswith(".py") else f"{name}.py"
            st.session_state.vfs["root"].append(name)
            st.session_state.file_contents[name] = f"# {name}\n"
            # Auto-open in new tab and switch to it
            new_tab = f"Tab {len(st.session_state.notebooks) + 1}"
            st.session_state.notebooks[new_tab] = name
            st.session_state.active_tab_index = len(st.session_state.notebooks) - 1
            st.rerun()
    if c2.button("CANCEL", use_container_width=True): st.rerun()

# --- 3. SIDEBAR: WORKSPACE CONTROLS ---
with st.sidebar:
    header_col, toggle_col = st.columns([3, 1])
    header_col.markdown(f"<h2 style='color:{fg}; margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if toggle_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme(); st.rerun()
    
    st.divider()
    workspace_mode = st.radio("WORKSPACE MODE", ["📊 Plotter Mode", "💻 Terminal Compiler"])
    st.divider()
    
    if st.button("➕ NEW TAB / FILE", use_container_width=True):
        create_file_pop()
    
    st.markdown("### 📁 EXPLORER")
    for f in st.session_state.vfs["root"]:
        c1, c2 = st.columns([5, 1])
        if c1.button(f"📄 {f}", key=f"sidebar_f_{f}", use_container_width=True):
            # Check if already open
            existing_tab = [k for k, v in st.session_state.notebooks.items() if v == f]
            if existing_tab:
                st.session_state.active_tab_index = list(st.session_state.notebooks.keys()).index(existing_tab[0])
            else:
                new_tab_label = f"Tab {len(st.session_state.notebooks) + 1}"
                st.session_state.notebooks[new_tab_label] = f
                st.session_state.active_tab_index = len(st.session_state.notebooks) - 1
            st.rerun()
        if c2.button("✕", key=f"del_{f}"):
            st.session_state.vfs["root"].remove(f); st.rerun()

# --- 4. MAIN INTERFACE ---
tab_keys = list(st.session_state.notebooks.keys())
if not tab_keys:
    st.info("No active tabs. Open a file from the explorer.")
else:
    # Render Tabs with persistent index
    ui_tabs = st.tabs(tab_keys)
    
    for i, t_key in enumerate(tab_keys):
        with ui_tabs[i]:
            fname = st.session_state.notebooks[t_key]
            
            # Tab Toolbar
            t_col1, t_col2 = st.columns([10, 1])
            t_col1.markdown(f"**FILE:** `{fname}` | **MODE:** `{workspace_mode}`")
            if t_col2.button("✕", key=f"close_{t_key}", help="Close Tab"):
                del st.session_state.notebooks[t_key]; st.rerun()

            # Editor
            code = st.text_area("EDITOR", value=st.session_state.file_contents[fname], height=300, key=f"ed_{t_key}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code

            # Conditional Layout based on Workspace Mode
            if workspace_mode == "💻 Terminal Compiler":
                st.write("⌨️ **STDIN / INPUT STREAM**")
                stdin_data = st.text_area("Type inputs for input() here...", key=f"in_{t_key}", height=80, label_visibility="collapsed")
                
            run_btn = st.button("▶️ RUN EXECUTION", type="primary", use_container_width=True, key=f"run_{t_key}")
            
            if run_btn:
                output_buffer = io.StringIO()
                if workspace_mode == "💻 Terminal Compiler":
                    sys.stdin = io.StringIO(stdin_data + "\n" * 50)
                
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    res_text = output_buffer.getvalue()
                    
                    if workspace_mode == "💻 Terminal Compiler":
                        st.markdown(f"<div class='terminal-window' style='color:{term_fg};'>$ python {fname}\n{res_text}</div>", unsafe_allow_html=True)
                    else:
                        # Plotter Mode Handling
                        if res_text:
                            st.markdown(f"<div class='terminal-window' style='color:{fg};'>{res_text}</div>", unsafe_allow_html=True)
                        for fn in plt.get_fignums():
                            fig = plt.figure(fn)
                            st.pyplot(fig)
                            plt.close(fig)
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
