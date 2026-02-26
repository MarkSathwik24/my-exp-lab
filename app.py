import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. CHROME BROWSER CONFIGURATION ---
st.set_page_config(page_title="Chrome | MARK SPACE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["index.py"]}
    st.session_state.file_contents = {"index.py": "print('Browser Ready.')"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "index.py"}]

# --- 2. CHROME UI ENGINE (CUSTOM CSS) ---
def apply_chrome_ui():
    bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
    fg = "#ffffff" if st.session_state.theme == 'dark' else "#202124"
    tab_bg = "#1e1e1e" if st.session_state.theme == 'dark' else "#dee1e6"
    active_tab = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
    accent = "#58a6ff" if st.session_state.theme == 'dark' else "#1a73e8"

    st.markdown(f"""
    <style>
        /* Main Browser Window */
        .stApp {{ background-color: {bg}; color: {fg}; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        
        /* Sidebar Styling (Address Bar & Settings) */
        [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid #3c4043; }}
        [data-testid="stSidebar"] .stMarkdown p {{ color: {fg} !important; font-weight: 500; font-size: 0.9rem; }}

        /* Chrome Tab Logic Styling */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; background-color: {tab_bg}; padding: 8px 12px 0 12px; border-radius: 8px 8px 0 0; }}
        .stTabs [data-baseweb="tab"] {{ 
            height: 38px; padding: 0 16px; 
            background-color: transparent !important; color: {fg} !important; 
            border-radius: 8px 8px 0 0 !important; border: none !important;
            font-size: 13px; font-weight: 400; opacity: 0.7;
        }}
        .stTabs [aria-selected="true"] {{ 
            background-color: {active_tab} !important; opacity: 1 !important; 
            box-shadow: 0 -2px 0 {accent} inset;
        }}

        /* Code Editor & Console */
        .stTextArea textarea {{ border-radius: 0 0 8px 8px !important; border: 1px solid #3c4043 !important; background: {active_tab} !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_chrome_ui()

# --- 3. BROWSER CONTROLS (SIDEBAR) ---
with st.sidebar:
    # Branding with Satellite Icon
    header_col, toggle_col = st.columns([4, 1])
    header_col.markdown(f"<h3 style='margin:0;'>🛰️ **MARK SPACE**</h3>", unsafe_allow_html=True)
    if toggle_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    st.divider()
    
    # Chrome Tab Addition
    if st.button("＋ New Browser Tab", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "index.py"})
        st.rerun()

    st.markdown("### 📁 Bookmarks / Files")
    for f in st.session_state.vfs["root"]:
        if st.button(f"📄 {f}", key=f"sb_{f}", use_container_width=True):
            ids = [nb["id"] for nb in st.session_state.notebooks]
            new_id = 1
            while new_id in ids: new_id += 1
            st.session_state.notebooks.append({"id": new_id, "file": f})
            st.rerun()

# --- 4. THE BROWSER WORKSPACE ---
if not st.session_state.notebooks:
    st.info("Browser is empty. Click '＋ New Browser Tab' to search.")
else:
    # Render Chrome-numbered Tabs
    tab_labels = [f"Tab {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id, fname = nb["id"], nb["file"]
            
            # Tab Toolbar (Chrome Toolbar Style)
            tb1, tb2 = st.columns([12, 1])
            tb1.caption(f"Address: mark-space://workspace/tab-{t_id}/{fname}")
            if tb2.button("✕", key=f"cls_{t_id}", help="Close Tab"):
                st.session_state.notebooks.pop(i); st.rerun()

            # Editor (Website Source)
            code = st.text_area("Source Code", value=st.session_state.file_contents[fname], height=300, key=f"ed_{t_id}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            # Input-Safe Compiler Console
            st.write("⌨️ **TERMINAL / CONSOLE**")
            stdin_val = st.text_area("Console Input", key=f"in_{t_id}", height=70, label_visibility="collapsed")
            
            if st.button("▶️ EXECUTE SCRIPT", key=f"run_{t_id}", use_container_width=True, type="primary"):
                # Padding stdin with 100 newlines to prevent conversion errors
                sys.stdin = io.StringIO(stdin_val + "\n" * 100)
                out_buf = io.StringIO()
                
                try:
                    with contextlib.redirect_stdout(out_buf):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    
                    st.markdown("---")
                    res = out_buf.getvalue()
                    if res: st.code(res)
                    for fig_n in plt.get_fignums():
                        st.pyplot(plt.figure(fig_n))
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
                    plt.close('all')
