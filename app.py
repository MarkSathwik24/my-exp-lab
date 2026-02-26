import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. SYSTEM CONFIG & THEME ---
st.set_page_config(page_title="MARK SPACE | IDE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["main.py"]}
    st.session_state.file_contents = {"main.py": "x = float(input('Num 1: '))\ny = float(input('Num 2: '))\nprint(f'Sum: {x + y}')"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {"Tab 1": "main.py"}

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# UI Styling
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent = "#0d1117", "#e6edf3", "#161b22", "#58a6ff"
    term_bg, term_fg = "#000000", "#39ff14"
else:
    bg, fg, editor_bg, accent = "#ffffff", "#24292f", "#f6f8fa", "#0969da"
    term_bg, term_fg = "#f6f8fa", "#1a1a1b"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid {accent}33; }}
    .stButton>button[key="theme_toggle"] {{ 
        border-radius: 50% !important; width: 42px !important; height: 42px !important; 
        background: {editor_bg} !important; border: 1px solid {accent}44 !important;
    }}
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; }}
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
            if name not in st.session_state.vfs["root"]:
                st.session_state.vfs["root"].append(name)
                st.session_state.file_contents[name] = f"# {name}\n"
            new_tab = f"Tab {len(st.session_state.notebooks) + 1}"
            st.session_state.notebooks[new_tab] = name
            st.rerun()
    if c2.button("CANCEL", use_container_width=True): st.rerun()

# --- 3. SIDEBAR: WORKSPACE CONTROLS ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='color:{fg}; margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme(); st.rerun()
    
    st.divider()
    workspace_mode = st.radio("WORKSPACE MODE", ["📊 Plotter Mode", "💻 Terminal Compiler"])
    
    # Sub-mode for Plotter
    plotter_submode = "Explorer"
    if workspace_mode == "📊 Plotter Mode":
        plotter_submode = st.radio("PLOTTER SOURCE", ["📁 Explorer", "📥 Upload"])
    
    st.divider()
    if st.button("➕ NEW TAB / FILE", use_container_width=True): create_file_pop()
    
    st.markdown("### 📁 EXPLORER")
    for f in st.session_state.vfs["root"]:
        c1, c2 = st.columns([5, 1])
        if c1.button(f"📄 {f}", key=f"sb_{f}", use_container_width=True):
            new_tab = f"Tab {len(st.session_state.notebooks) + 1}"
            st.session_state.notebooks[new_tab] = f; st.rerun()
        if c2.button("✕", key=f"del_{f}"):
            st.session_state.vfs["root"].remove(f); st.rerun()

# --- 4. MAIN INTERFACE ---
tab_keys = list(st.session_state.notebooks.keys())
if not tab_keys:
    st.info("Select a file from the explorer to begin.")
else:
    ui_tabs = st.tabs(tab_keys)
    for i, t_key in enumerate(tab_keys):
        with ui_tabs[i]:
            fname = st.session_state.notebooks[t_key]
            
            # Tab Header
            th1, th2 = st.columns([10, 1])
            th1.markdown(f"**FILE:** `{fname}` | **MODE:** `{workspace_mode}`")
            if th2.button("✕", key=f"cls_{t_key}"):
                del st.session_state.notebooks[t_key]; st.rerun()

            # Plotter Upload Logic
            if workspace_mode == "📊 Plotter Mode" and plotter_submode == "📥 Upload":
                up_file = st.file_uploader(f"Upload .py for {t_key}", type=['py'], key=f"up_{t_key}")
                if up_file:
                    content = up_file.getvalue().decode("utf-8")
                    st.session_state.file_contents[fname] = content
            
            # Editor
            code = st.text_area("EDITOR", value=st.session_state.file_contents.get(fname, ""), height=300, key=f"ed_{t_key}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code

            # Input Handling for Compiler
            stdin_data = ""
            if workspace_mode == "💻 Terminal Compiler":
                st.write("⌨️ **STDIN / INPUT STREAM**")
                stdin_data = st.text_area("Inputs (one per line)", key=f"in_{t_key}", height=80, label_visibility="collapsed")
            
            if st.button("▶️ RUN EXECUTION", type="primary", use_container_width=True, key=f"run_{t_key}"):
                output_buffer = io.StringIO()
                # FIX: Pre-pad stdin with extra newlines to prevent 'float conversion' errors on empty inputs
                sys.stdin = io.StringIO(stdin_data + "\n" * 100)
                
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    res = output_buffer.getvalue()
                    
                    if workspace_mode == "💻 Terminal Compiler":
                        st.markdown(f"<div class='terminal-window' style='color:{term_fg};'>$ python {fname}\n{res}</div>", unsafe_allow_html=True)
                    else:
                        if res: st.markdown(f"<div class='terminal-window'>{res}</div>", unsafe_allow_html=True)
                        for fn in plt.get_fignums():
                            st.pyplot(plt.figure(fn))
                            plt.close(plt.figure(fn))
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
