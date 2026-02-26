import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import traceback

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Jarvis | Colab Browser", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THEME ENGINE ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    css = """
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    button[role="tab"] { background-color: #161b22 !important; border-radius: 8px 8px 0 0 !important; border: 1px solid #30363d !important; border-bottom: none !important; padding: 8px 20px !important; margin-right: 2px !important; color: #8b949e !important; }
    button[role="tab"][aria-selected="true"] { background-color: #0e1117 !important; color: #58a6ff !important; border-top: 3px solid #58a6ff !important; font-weight: bold !important; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #161b22 !important; color: #58d68d !important; border: 1px solid #30363d !important; border-radius: 8px; }
    .output-block { background-color: #0d1117; color: #c9d1d9; padding: 15px; border-left: 3px solid #58a6ff; font-family: monospace; white-space: pre-wrap; margin-top: 10px; border-radius: 4px; }
    .error-block { border-left: 3px solid #f85149; color: #f85149; }
    [data-testid="stFileUploadDropzone"] { border: 1px dashed #58a6ff !important; background-color: rgba(88, 166, 255, 0.05) !important; min-height: 100px !important; }
    </style>
    """
else:
    css = """
    <style>
    .main { background-color: #ffffff; color: #24292f; }
    button[role="tab"] { background-color: #e1e4e8 !important; border-radius: 8px 8px 0 0 !important; border: 1px solid #d0d7de !important; border-bottom: none !important; padding: 8px 20px !important; margin-right: 2px !important; color: #57606a !important; }
    button[role="tab"][aria-selected="true"] { background-color: #ffffff !important; color: #0969da !important; border-top: 3px solid #0969da !important; font-weight: bold !important; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #f6f8fa !important; color: #0969da !important; border: 1px solid #d0d7de !important; border-radius: 8px; }
    .output-block { background-color: #f6f8fa; color: #24292f; padding: 15px; border-left: 3px solid #0969da; font-family: monospace; white-space: pre-wrap; margin-top: 10px; border-radius: 4px; }
    .error-block { border-left: 3px solid #cf222e; color: #cf222e; }
    [data-testid="stFileUploadDropzone"] { border: 1px dashed #0969da !important; background-color: rgba(9, 105, 218, 0.05) !important; min-height: 100px !important; }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

# --- 3. MULTI-INSTANCE MEMORY ---
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {
        "Tab 1": {
            "code": "# Jarvis Colab Environment\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nprint('System Online.')",
            "namespace": {'np': np, 'plt': plt, 'pd': pd, 'st': st},
            "output_text": "",
            "output_error": False,
            "figs_matplotlib": []
        }
    }

# --- 4. SIDEBAR (Only for Theme Toggle Now) ---
with st.sidebar:
    btn_icon = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    if st.button(btn_icon, use_container_width=True):
        toggle_theme()
        st.rerun()
    st.info("Sidebar collapsed. All controls are now in the main interface.")

# --- 5. MAIN HEADER & NEW TAB CONTROL ---
col_title, col_newtab = st.columns([4, 1])
with col_title:
    st.title("Jarvis Colab Engine")
with col_newtab:
    st.write("") # Spacing alignment
    if st.button("➕ Open New Tab", use_container_width=True):
        # SMART TAB NUMBERING: Find the lowest available number
        idx = 1
        while f"Tab {idx}" in st.session_state.notebooks:
            idx += 1
        
        new_tab_name = f"Tab {idx}"
        st.session_state.notebooks[new_tab_name] = {
            "code": f"# {new_tab_name}\n",
            "namespace": {'np': np, 'plt': plt, 'pd': pd, 'st': st},
            "output_text": "",
            "output_error": False,
            "figs_matplotlib": []
        }
        st.rerun()

# --- 6. BROWSER TABS & COLAB EXECUTION ---
tab_names = list(st.session_state.notebooks.keys())

# Failsafe: If user closes all tabs, generate a fresh Tab 1
if not tab_names:
    st.session_state.notebooks["Tab 1"] = {
        "code": "# Welcome back.\n",
        "namespace": {'np': np, 'plt': plt, 'pd': pd, 'st': st},
        "output_text": "",
        "output_error": False,
        "figs_matplotlib": []
    }
    st.rerun()

tabs = st.tabs(tab_names)

for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        nb = st.session_state.notebooks[tab_name]
        
        # IN-TAB HEADER: Title and Close Button
        c_head, c_close = st.columns([5, 1])
        c_head.subheader(f"Workspace: {tab_name}")
        if c_close.button("❌ Close Tab", key=f"close_{tab_name}", use_container_width=True):
            del st.session_state.notebooks[tab_name]
            st.rerun()
            
        # DEDICATED DRAG & DROP ZONE
        uploaded_file = st.file_uploader(f"📂 Drag and drop a .py script to load into {tab_name}", type=['py'], key=f"up_{tab_name}")
        if uploaded_file is not None:
            file_content = uploaded_file.getvalue().decode("utf-8")
            if nb["code"] != file_content:
                nb["code"] = file_content
                st.rerun()
                
        # CODE EDITOR
        current_code = st.text_area("Code", value=nb["code"], height=250, key=f"code_{tab_name}", label_visibility="collapsed")
        nb["code"] = current_code 
        
        # EXECUTION CONTROLS
        col_run, col_live = st.columns([1, 1])
        with col_run:
            run_clicked = st.button(f"▶️ Run Code", type="primary", key=f"run_{tab_name}", use_container_width=True)
        with col_live:
            is_interactive = st.toggle("⚡ Live Engine Mode", key=f"live_{tab_name}")

        # EXECUTION LOGIC
        if run_clicked or is_interactive:
            output_buffer = io.StringIO()
            nb["figs_matplotlib"] = []
            nb["output_error"] = False
            
            try:
                with contextlib.redirect_stdout(output_buffer):
                    try:
                        result = eval(current_code, globals(), nb["namespace"])
                        if result is not None: print(result)
                    except SyntaxError:
                        exec(current_code, globals(), nb["namespace"])
                        
                nb["output_text"] = output_buffer.getvalue()
                
                fig_nums = plt.get_fignums()
                for f_num in fig_nums:
                    fig = plt.figure(f_num)
                    buf = io.BytesIO()
                    face_c = 'white' if st.session_state.theme == 'dark' else '#f6f8fa'
                    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=face_c)
                    buf.seek(0)
                    nb["figs_matplotlib"].append(buf.getvalue())
                    
            except Exception as e:
                nb["output_text"] = traceback.format_exc(limit=0)
                nb["output_error"] = True
                
            finally:
                plt.close('all') 
                if run_clicked and not is_interactive:
                    st.rerun() 

        # OUTPUT RENDERING
        if nb["output_text"] or nb["figs_matplotlib"]:
            st.markdown("---")
            if nb["output_text"]:
                if nb["output_error"]:
                    st.markdown(f"<div class='output-block error-block'>{nb['output_text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='output-block'>{nb['output_text']}</div>", unsafe_allow_html=True)
            
            for fig_bytes in nb["figs_matplotlib"]:
                st.image(fig_bytes)
