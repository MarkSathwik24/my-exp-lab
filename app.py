import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. SYSTEM INITIALIZATION ---
# We use st.session_state to ensure data persists during reruns.
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["main.py"]}
    st.session_state.file_contents = {"main.py": "# MARK SPACE START\nprint('Hello Space')"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "main.py"}]
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# --- 2. THEME & UI LOGIC ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# High-contrast color mapping
bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
fg = "#ffffff" if st.session_state.theme == 'dark' else "#000000"
accent = "#58a6ff" if st.session_state.theme == 'dark' else "#0969da"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid {accent}33; }}
    /* Circle Toggle Styling */
    .stButton>button[key="theme_toggle"] {{ border-radius: 50% !important; width: 45px; height: 45px; }}
    /* Tab Visibility */
    button[role="tab"] {{ color: {fg} !important; opacity: 0.6; }}
    button[role="tab"][aria-selected="true"] {{ opacity: 1; border-top: 2px solid {accent} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR BRANDING & SMART TABS ---
with st.sidebar:
    col_t1, col_t2 = st.columns([3, 1])
    col_t1.markdown(f"## 🛰️ **MARK SPACE**")
    if col_t2.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme()
        st.rerun()

    st.divider()
    
    # SMART TAB ADDITION: Scans for lowest available ID
    if st.button("➕ NEW TAB", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "main.py"})
        st.rerun()

# --- 4. WORKSPACE & EXECUTION ---
if st.session_state.notebooks:
    tab_labels = [f"Tab {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id = nb["id"]
            fname = nb["file"]
            
            # Editor
            code = st.text_area("Code", value=st.session_state.file_contents[fname], height=300, key=f"ed_{t_id}")
            st.session_state.file_contents[fname] = code
            
            # Terminal Input (Prevents float conversion error)
            st.write("⌨️ **TERMINAL INPUT**")
            stdin_raw = st.text_area("Inputs", key=f"in_{t_id}", height=70)
            
            if st.button("▶️ RUN", key=f"run_{t_id}", use_container_width=True):
                # Standard input override for calculator functions
                sys.stdin = io.StringIO(stdin_raw + "\n" * 100)
                out_buf = io.StringIO()
                
                try:
                    with contextlib.redirect_stdout(out_buf):
                        # Execute in a clean namespace
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    st.code(out_buf.getvalue()) # Console output
                    for fig_num in plt.get_fignums():
                        st.pyplot(plt.figure(fig_num)) # Plot rendering
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__ # Reset safety
                    plt.close('all')
