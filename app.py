import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import traceback
import os

# --- 1. INITIALIZE VIRTUAL FILE SYSTEM ---
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["welcome.py"]} # List of files
    st.session_state.file_contents = {"welcome.py": "# Welcome to Jarvis IDE\nprint('System Online.')"}
    st.session_state.notebooks = {"Tab 1": "welcome.py"} # Active Tabs
    st.session_state.theme = 'dark'

# --- 2. THEME ENGINE (SIDEBAR CONTROLLED) ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Dynamic CSS Injection
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent = "#0e1117", "#c9d1d9", "#161b22", "#58a6ff"
else:
    bg, fg, editor_bg, accent = "#ffffff", "#24292f", "#f6f8fa", "#0969da"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {accent} !important; border: 1px solid {accent}44 !important; }}
    button[role="tab"] {{ background-color: {editor_bg} !important; color: {fg} !important; border-radius: 8px 8px 0 0 !important; }}
    button[role="tab"][aria-selected="true"] {{ border-top: 3px solid {accent} !important; font-weight: bold !important; }}
    .output-block {{ background-color: {editor_bg}; padding: 15px; border-left: 4px solid {accent}; font-family: monospace; border-radius: 4px; margin-top: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: WORKSPACE MANAGER ---
with st.sidebar:
    st.title("🛰️ Jarvis Workspace")
    
    # Theme Toggle
    theme_icon = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    if st.button(theme_icon, use_container_width=True):
        toggle_theme()
        st.rerun()
    
    st.divider()
    
    # Module Selection
    mode = st.radio("Mode", ["📁 Explorer", "📥 Drag & Drop Upload"])
    
    if mode == "📁 Explorer":
        st.subheader("Files")
        # Create New File
        new_file_name = st.text_input("New Filename (e.g. test.py)", key="new_f")
        if st.button("➕ Create File", use_container_width=True):
            if new_file_name and new_file_name not in st.session_state.vfs["root"]:
                st.session_state.vfs["root"].append(new_file_name)
                st.session_state.file_contents[new_file_name] = f"# {new_file_name}\n"
                st.rerun()

        st.divider()
        # File List
        for f in st.session_state.vfs["root"]:
            c1, c2 = st.columns([4, 1])
            if c1.button(f"📄 {f}", key=f"open_{f}", use_container_width=True):
                # Open in a new numbered tab
                idx = len(st.session_state.notebooks) + 1
                st.session_state.notebooks[f"Tab {idx}"] = f
                st.rerun()
            if c2.button("🗑️", key=f"del_{f}"):
                st.session_state.vfs["root"].remove(f)
                st.rerun()

    else:
        st.subheader("Upload to Workspace")
        up_file = st.file_uploader("Drop .py scripts here", type=['py'])
        if up_file:
            f_name = up_file.name
            if f_name not in st.session_state.vfs["root"]:
                st.session_state.vfs["root"].append(f_name)
            st.session_state.file_contents[f_name] = up_file.getvalue().decode("utf-8")
            st.success(f"Stored {f_name} in Explorer")

# --- 4. MAIN INTERFACE: TABS & EDITOR ---
st.title("Jarvis Multi-Tab IDE")
tab_names = list(st.session_state.notebooks.keys())

if not tab_names:
    st.info("Select a file from the 📁 Explorer in the sidebar to begin.")
else:
    ui_tabs = st.tabs(tab_names)
    
    for i, tab_label in enumerate(tab_names):
        with ui_tabs[i]:
            target_file = st.session_state.notebooks[tab_label]
            
            # Tab Header
            h1, h2 = st.columns([5, 1])
            h1.subheader(f"Editing: {target_file}")
            if h2.button("❌ Close", key=f"close_{tab_label}"):
                del st.session_state.notebooks[tab_label]
                st.rerun()

            # Editor
            code = st.text_area("Source Code", value=st.session_state.file_contents[target_file], height=300, key=f"ed_{tab_label}")
            st.session_state.file_contents[target_file] = code # Sync changes
            
            # Controls
            c_run, c_live = st.columns([1, 1])
            run_trigger = c_run.button("▶️ Run Code", type="primary", key=f"run_{tab_label}", use_container_width=True)
            live_mode = c_live.toggle("⚡ Live Engine", key=f"live_{tab_label}")

            # Execution Logic
            if run_trigger or live_mode:
                output_buffer = io.StringIO()
                figs = []
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    out_text = output_buffer.getvalue()
                    
                    for f_num in plt.get_fignums():
                        fig = plt.figure(f_num)
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight", facecolor='white')
                        buf.seek(0)
                        figs.append(buf.getvalue())
                        
                    st.markdown("---")
                    if out_text:
                        st.markdown(f"<div class='output-block'>{out_text}</div>", unsafe_allow_html=True)
                    for f_bytes in figs:
                        st.image(f_bytes)
                except Exception as e:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    plt.close('all')
