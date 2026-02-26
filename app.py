import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. CHROME BROWSER CONFIG ---
st.set_page_config(page_title="Chrome | MARK SPACE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["index.py"]}
    st.session_state.file_contents = {"index.py": "print('Browser Ready.')"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "index.py"}]

# --- 2. CHROME UI ENGINE ---
def apply_chrome_ui():
    bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
    fg = "#ffffff" if st.session_state.theme == 'dark' else "#202124"
    accent = "#58a6ff" if st.session_state.theme == 'dark' else "#1a73e8"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg}; color: {fg}; }}
        [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid #3c4043; }}
        .stMarkdown, label, .stHeader, .stCaption {{ color: {fg} !important; font-weight: bold; }}
        
        /* Chrome Tab List Styling */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; padding-top: 8px; }}
        button[role="tab"] {{ color: {fg} !important; opacity: 0.6; }}
        button[role="tab"][aria-selected="true"] {{ opacity: 1; border-top: 2px solid {accent} !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_chrome_ui()

# --- 3. BROWSER SIDEBAR (CONTROLS & UPLOAD) ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    st.divider()
    
    # ➕ NEW TAB LOGIC
    if st.button("＋ NEW BROWSER TAB", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "index.py"})
        st.rerun()

    st.divider()
    
    # 📤 UPLOAD ENGINE
    st.markdown("### 📤 Upload Script")
    uploaded_file = st.file_uploader("Drop .py file here", type=["py"], label_visibility="collapsed")
    if uploaded_file:
        fname = uploaded_file.name
        content = uploaded_file.getvalue().decode("utf-8")
        
        # Add to Virtual File System
        if fname not in st.session_state.vfs["root"]:
            st.session_state.vfs["root"].append(fname)
            st.session_state.file_contents[fname] = content
            
            # Smart Tab logic: Open uploaded file in new tab
            ids = [nb["id"] for nb in st.session_state.notebooks]
            new_id = 1
            while new_id in ids: new_id += 1
            st.session_state.notebooks.append({"id": new_id, "file": fname})
            st.success(f"Opened {fname}")
            st.rerun()

# --- 4. THE CHROME WORKSPACE ---
if not st.session_state.notebooks:
    st.info("No active tabs. Open one or upload a file from the sidebar.")
else:
    tab_labels = [f"Tab {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id, fname = nb["id"], nb["file"]
            
            # TAB TOOLBAR
            header_col1, header_col2 = st.columns([15, 1])
            header_col1.caption(f"Address: chrome://workspace/tab-{t_id}/{fname}")
            if header_col2.button("✕", key=f"close_btn_{t_id}", help="Close Tab"):
                st.session_state.notebooks.pop(i)
                st.rerun()

            # EDITOR
            code = st.text_area("Source", value=st.session_state.file_contents.get(fname, ""), height=300, key=f"ed_{t_id}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            # CONSOLE INPUT
            st.write("⌨️ **BROWSER CONSOLE**")
            stdin_val = st.text_area("Inputs", key=f"in_{t_id}", height=70, label_visibility="collapsed")
            
            if st.button("▶️ RUN SCRIPT", key=f"run_{t_id}", use_container_width=True, type="primary"):
                # Padding stdin to fix float conversion error
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
