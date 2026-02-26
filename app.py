import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. SYSTEM INITIALIZATION ---
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["main.py"]}
    st.session_state.file_contents = {"main.py": "# MARK SPACE START\nprint('Hello Space')"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "main.py"}]
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# --- 2. THEME LOGIC ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
fg = "#ffffff" if st.session_state.theme == 'dark' else "#000000"
accent = "#58a6ff" if st.session_state.theme == 'dark' else "#0969da"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid {accent}33; }}
    /* High-contrast labels */
    .stMarkdown, label, .stToggle {{ color: {fg} !important; font-weight: bold; }}
    /* Tab Close Button Styling */
    .close-tab-btn {{ color: #ff4b4b !important; border: none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR BRANDING & TAB MANAGEMENT ---
with st.sidebar:
    col_t1, col_t2 = st.columns([3, 1])
    col_t1.markdown(f"## 🛰️ **MARK SPACE**")
    if col_t2.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme(); st.rerun()

    st.divider()
    
    # SMART TAB ADDITION
    if st.button("➕ NEW TAB", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "main.py"})
        st.rerun()

# --- 4. MAIN WORKSPACE ---
if not st.session_state.notebooks:
    st.info("No active tabs. Click '➕ NEW TAB' in the sidebar to begin.")
else:
    tab_labels = [f"Tab {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id = nb["id"]
            fname = nb["file"]
            
            # --- TAB HEADER WITH CLOSE OPTION ---
            h_col1, h_col2 = st.columns([10, 1])
            h_col1.write(f"**WORKSPACE:** `Tab {t_id}`")
            # The Close Button: Removes the entry at current index 'i'
            if h_col2.button("✕", key=f"cls_{t_id}", help="Close this tab"):
                st.session_state.notebooks.pop(i)
                st.rerun()

            # Editor and Input Handling
            code = st.text_area("Editor", value=st.session_state.file_contents[fname], height=300, key=f"ed_{t_id}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            st.write("⌨️ **TERMINAL INPUT**")
            stdin_raw = st.text_area("Input Stream", key=f"in_{t_id}", height=70, label_visibility="collapsed")
            
            if st.button("▶️ RUN EXECUTION", key=f"run_{t_id}", use_container_width=True):
                # Safe input override to prevent numeric conversion errors
                sys.stdin = io.StringIO(stdin_raw + "\n" * 100)
                out_buf = io.StringIO()
                
                try:
                    with contextlib.redirect_stdout(out_buf):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    output = out_buf.getvalue()
                    if output: st.code(output)
                    for fig_num in plt.get_fignums():
                        st.pyplot(plt.figure(fig_num))
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
                    plt.close('all')

# Capture Plotly Figures directly from the execution namespace
for var_name, var_value in local_scope.items():
    if "plotly.graph_objs._figure.Figure" in str(type(var_value)):
        st.plotly_chart(var_value, use_container_width=True) # Render interactive chart
