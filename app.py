import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import traceback

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Jarvis | Colab Browser", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THEME ENGINE (Full App Contrast) ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Universal Styling for Tabs, Editors, and Outputs
if st.session_state.theme == 'dark':
    bg, fg, accent, border = "#0e1117", "#c9d1d9", "#58a6ff", "#30363d"
    editor_bg, editor_fg = "#161b22", "#58d68d"
else:
    bg, fg, accent, border = "#ffffff", "#24292f", "#0969da", "#d0d7de"
    editor_bg, editor_fg = "#f6f8fa", "#0969da"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stHeader"] {{ background-color: {bg}; }}
    [data-testid="stSidebar"] {{ background-color: {bg}; border-right: 1px solid {border}; }}
    
    /* Chrome-style Tabs */
    button[role="tab"] {{ background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {border} !important; border-bottom: none !important; border-radius: 8px 8px 0 0 !important; }}
    button[role="tab"][aria-selected="true"] {{ background-color: {bg} !important; color: {accent} !important; border-top: 3px solid {accent} !important; }}
    
    /* Editor & Terminal Output */
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {editor_fg} !important; border: 1px solid {border} !important; border-radius: 8px; }}
    .output-block {{ background-color: {editor_bg}; color: {fg}; padding: 15px; border-left: 4px solid {accent}; font-family: monospace; white-space: pre-wrap; border-radius: 4px; margin-top: 10px; }}
    
    /* Buttons */
    .stButton>button {{ width: 100%; background-color: {editor_bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; }}
    .stButton>button:hover {{ border-color: {accent}; color: {accent}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MULTI-INSTANCE MEMORY ---
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {
        "Tab 1": {
            "code": "# Jarvis Colab Environment\nimport numpy as np\nimport matplotlib.pyplot as plt\nprint('System Ready.')",
            "namespace": {'np': np, 'plt': plt, 'pd': pd, 'st': st},
            "output_text": "",
            "figs_matplotlib": []
        }
    }

# --- 4. NAVIGATION & NEW TAB LOGIC ---
col_t, col_btn = st.columns([5, 1])
with col_t:
    st.title("🛰️ Jarvis Colab Browser")
with col_btn:
    st.write("")
    if st.button("➕ New Tab", use_container_width=True):
        idx = 1
        while f"Tab {idx}" in st.session_state.notebooks: idx += 1
        st.session_state.notebooks[f"Tab {idx}"] = {
            "code": f"# Tab {idx}\n", "namespace": {'np': np, 'plt': plt, 'pd': pd, 'st': st},
            "output_text": "", "figs_matplotlib": []
        }
        st.rerun()

# --- 5. EXECUTION ENGINE ---
def run_code(nb_key, code_to_run):
    nb = st.session_state.notebooks[nb_key]
    output_buffer = io.StringIO()
    nb["figs_matplotlib"] = []
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code_to_run, globals(), nb["namespace"])
        nb["output_text"] = output_buffer.getvalue()
        for f_num in plt.get_fignums():
            fig = plt.figure(f_num)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor='white')
            buf.seek(0)
            nb["figs_matplotlib"].append(buf.getvalue())
    except Exception as e:
        nb["output_text"] = traceback.format_exc(limit=0)
    finally:
        plt.close('all')

# --- 6. WORKSPACE INTERFACE ---
tab_names = list(st.session_state.notebooks.keys())
if not tab_names: st.rerun()

tabs = st.tabs(tab_names)
for i, name in enumerate(tab_names):
    with tabs[i]:
        nb = st.session_state.notebooks[name]
        
        # Header & Theme Toggle (Sun/Moon)
        c_title, c_theme, c_close = st.columns([6, 1, 1])
        c_title.write(f"### {name}")
        if c_theme.button("☀️" if st.session_state.theme == 'dark' else "🌙", key=f"t_{name}"):
            toggle_theme(); st.rerun()
        if c_close.button("❌", key=f"c_{name}"):
            del st.session_state.notebooks[name]; st.rerun()

        # Drag & Drop with Run Option
        up_file = st.file_uploader("📂 Drop .py file", type=['py'], key=f"u_{name}")
        
        col_exec1, col_exec2, col_live = st.columns([1, 1, 1])
        
        # New Feature: Execute Dropped File Separately
        if up_file and col_exec1.button("🚀 Run Dropped File", key=f"rf_{name}"):
            run_code(name, up_file.getvalue().decode("utf-8"))
            st.rerun()
        
        if col_exec2.button("▶️ Run Editor Code", type="primary", key=f"re_{name}"):
            run_code(name, nb["code"])
            st.rerun()
            
        is_live = col_live.toggle("⚡ Live Engine", key=f"l_{name}")

        # Code Editor
        nb["code"] = st.text_area("Editor", value=nb["code"], height=250, key=f"ed_{name}", label_visibility="collapsed")
        
        if is_live:
            run_code(name, nb["code"])

        # Output Display
        if nb["output_text"] or nb["figs_matplotlib"]:
            st.markdown("---")
            if nb["output_text"]:
                st.markdown(f"<div class='output-block'>{nb['output_text']}</div>", unsafe_allow_html=True)
            for fig in nb["figs_matplotlib"]:
                st.image(fig)
