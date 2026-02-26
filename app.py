import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. BROWSER INITIALIZATION ---
st.set_page_config(page_title="Chrome | MARK SPACE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["live_sim.py"]}
    st.session_state.file_contents = {"live_sim.py": "# Live Mode On\nimport matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\nplt.plot(x, y)\nplt.show()"}
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "live_sim.py"}]

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
        
        /* Live Mode Active Pulse */
        .live-indicator {{ color: #39ff14; font-size: 0.8rem; font-weight: bold; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
    </style>
    """, unsafe_allow_html=True)

apply_chrome_ui()

# --- 3. BROWSER SIDEBAR ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    st.divider()
    if st.button("＋ NEW BROWSER TAB", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": "live_sim.py"})
        st.rerun()

    st.divider()
    st.markdown("### 📤 Upload Script")
    uploaded_file = st.file_uploader("Drop .py file", type=["py"], label_visibility="collapsed")
    if uploaded_file:
        fname = uploaded_file.name
        st.session_state.file_contents[fname] = uploaded_file.getvalue().decode("utf-8")
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        st.session_state.notebooks.append({"id": new_id, "file": fname})
        st.rerun()

# --- 4. THE CHROME WORKSPACE ---
if not st.session_state.notebooks:
    st.info("Browser is empty.")
else:
    tab_labels = [f"Tab {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id, fname = nb["id"], nb["file"]
            
            # TAB TOOLBAR
            header_col1, header_col2 = st.columns([15, 1])
            header_col1.caption(f"Address: chrome://live-engine/tab-{t_id}/{fname}")
            if header_col2.button("✕", key=f"close_btn_{t_id}"):
                st.session_state.notebooks.pop(i); st.rerun()

            # LIVE MODE CONTROLS
            c1, c2 = st.columns([1, 1])
            run_manual = c1.button("▶️ RUN MANUALLY", key=f"run_m_{t_id}", use_container_width=True)
            live_active = c2.toggle("⚡ LIVE INTERACTING MODE", key=f"live_{t_id}")
            
            if live_active:
                st.markdown("<span class='live-indicator'>● LIVE ENGINE ACTIVE</span>", unsafe_allow_html=True)

            # EDITOR
            code = st.text_area("Source", value=st.session_state.file_contents.get(fname, ""), height=300, key=f"ed_{t_id}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            # CONSOLE INPUT
            st.write("⌨️ **BROWSER CONSOLE**")
            stdin_val = st.text_area("Inputs", key=f"in_{t_id}", height=70, label_visibility="collapsed")
            
            # EXECUTION LOGIC
            if run_manual or live_active:
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
                    if not live_active: st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = sys.__stdin__
                    plt.close('all')
