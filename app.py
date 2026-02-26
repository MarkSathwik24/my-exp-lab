import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import traceback

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Jarvis | Colab Browser", layout="wide", initial_sidebar_state="expanded")

# --- 2. THEME ENGINE ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Chrome-style Tabs & Colab Cells CSS
if st.session_state.theme == 'dark':
    css = """
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    /* Chrome-like Tabs */
    button[role="tab"] { background-color: #161b22 !important; border-radius: 8px 8px 0 0 !important; border: 1px solid #30363d !important; border-bottom: none !important; padding: 8px 20px !important; margin-right: 2px !important; color: #8b949e !important; }
    button[role="tab"][aria-selected="true"] { background-color: #0e1117 !important; color: #58a6ff !important; border-top: 3px solid #58a6ff !important; font-weight: bold !important; }
    /* Colab Editor */
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #161b22 !important; color: #58d68d !important; border: 1px solid #30363d !important; border-radius: 8px; }
    /* Output Block */
    .output-block { background-color: #0d1117; color: #c9d1d9; padding: 15px; border-left: 3px solid #58a6ff; font-family: monospace; white-space: pre-wrap; margin-top: 10px; border-radius: 4px; }
    .error-block { border-left: 3px solid #f85149; color: #f85149; }
    </style>
    """
else:
    css = """
    <style>
    .main { background-color: #ffffff; color: #24292f; }
    /* Chrome-like Tabs */
    button[role="tab"] { background-color: #e1e4e8 !important; border-radius: 8px 8px 0 0 !important; border: 1px solid #d0d7de !important; border-bottom: none !important; padding: 8px 20px !important; margin-right: 2px !important; color: #57606a !important; }
    button[role="tab"][aria-selected="true"] { background-color: #ffffff !important; color: #0969da !important; border-top: 3px solid #0969da !important; font-weight: bold !important; }
    /* Colab Editor */
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; background-color: #f6f8fa !important; color: #0969da !important; border: 1px solid #d0d7de !important; border-radius: 8px; }
    /* Output Block */
    .output-block { background-color: #f6f8fa; color: #24292f; padding: 15px; border-left: 3px solid #0969da; font-family: monospace; white-space: pre-wrap; margin-top: 10px; border-radius: 4px; }
    .error-block { border-left: 3px solid #cf222e; color: #cf222e; }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

# --- 3. MULTI-INSTANCE MEMORY ---
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {
        "Tab 1": {
            "code": "# Jarvis Colab Environment\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nprint('System Online.')",
            "namespace": {'np': np, 'plt': plt, 'pd': pd},
            "output_text": "",
            "output_error": False,
            "figs_matplotlib": []
        }
    }
if 'tab_counter' not in st.session_state:
    st.session_state.tab_counter = 1

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛰️ Jarvis Controls")
    
    # Sun/Moon Toggle
    btn_icon = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    if st.button(btn_icon, use_container_width=True):
        toggle_theme()
        st.rerun()
        
    st.divider()
    
    # Chrome-style New Tab
    if st.button("➕ Open New Tab", use_container_width=True):
        st.session_state.tab_counter += 1
        new_tab_name = f"Tab {st.session_state.tab_counter}"
        st.session_state.notebooks[new_tab_name] = {
            "code": f"# {new_tab_name}\n",
            "namespace": {'np': np, 'plt': plt, 'pd': pd},
            "output_text": "",
            "output_error": False,
            "figs_matplotlib": []
        }
        st.rerun()
        
    st.markdown("**Active Tabs:**")
    for nb_name in list(st.session_state.notebooks.keys()):
        c1, c2 = st.columns([4, 1])
        c1.write(f"📄 {nb_name}")
        if len(st.session_state.notebooks) > 1:
            if c2.button("❌", key=f"del_{nb_name}"):
                del st.session_state.notebooks[nb_name]
                st.rerun()

# --- 5. BROWSER TABS & COLAB EXECUTION ---
st.title("Jarvis Colab Engine")
tab_names = list(st.session_state.notebooks.keys())
tabs = st.tabs(tab_names)

for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        nb = st.session_state.notebooks[tab_name]
        
        # Code Editor
        current_code = st.text_area(f"Code for {tab_name}", value=nb["code"], height=250, key=f"code_{tab_name}", label_visibility="collapsed")
        nb["code"] = current_code 
        
        col_run, col_up = st.columns([1, 4])
        
        with col_up:
            # File injection
            uploaded_file = st.file_uploader(f"Upload .py to {tab_name}", type=['py'], key=f"up_{tab_name}", label_visibility="collapsed")
            if uploaded_file is not None:
                file_content = uploaded_file.getvalue().decode("utf-8")
                if nb["code"] != file_content:
                    nb["code"] = file_content
                    st.rerun()

        with col_run:
            st.write("") # Spacing
            if st.button(f"▶️ Run Code", type="primary", key=f"run_{tab_name}", use_container_width=True):
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
                    
                    # Capture Matplotlib Figures as Images
                    fig_nums = plt.get_fignums()
                    for f_num in fig_nums:
                        fig = plt.figure(f_num)
                        buf = io.BytesIO()
                        # Dynamic background based on theme
                        face_c = 'white' if st.session_state.theme == 'dark' else '#f6f8fa'
                        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=face_c)
                        buf.seek(0)
                        nb["figs_matplotlib"].append(buf.getvalue())
                        
                except Exception as e:
                    nb["output_text"] = traceback.format_exc(limit=0)
                    nb["output_error"] = True
                    
                finally:
                    plt.close('all') 
                    st.rerun() 

        # Output Section
        if nb["output_text"] or nb["figs_matplotlib"]:
            st.markdown("---")
            if nb["output_text"]:
                if nb["output_error"]:
                    st.markdown(f"<div class='output-block error-block'>{nb['output_text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='output-block'>{nb['output_text']}</div>", unsafe_allow_html=True)
            
            for fig_bytes in nb["figs_matplotlib"]:
                st.image(fig_bytes)
