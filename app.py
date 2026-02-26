import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback
import base64

# --- 1. RESEARCH HUB INITIALIZATION ---
st.set_page_config(page_title="Notes | MARK SPACE", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# --- 2. THEME ENGINE & UI ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Logic for Absolute Contrast
bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
fg = "#ffffff" if st.session_state.theme == 'dark' else "#202124"
accent = "#58a6ff" if st.session_state.theme == 'dark' else "#1a73e8"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid #3c4043; }}
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{ color: {fg} !important; font-weight: bold; }}
    
    /* Chrome Tab Styling */
    button[role="tab"] {{ color: {fg} !important; opacity: 0.6; background: transparent !important; }}
    button[role="tab"][aria-selected="true"] {{ opacity: 1; border-top: 3px solid {accent} !important; font-weight: bold !important; }}

    /* Editor Styling */
    .stTextArea textarea {{ background-color: {bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. PERSISTENT STATE INITIALIZATION ---
# Safe structures to prevent the KeyError and TypeError seen in your logs
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["Research_Log.txt"]}
    st.session_state.file_contents = {"Research_Log.txt": "## 🛰️ Research Entry\nStart logging aerospace notes..."}
    st.session_state.media_vault = {} 

if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "Research_Log.txt", "type": "Notes"}]

# --- 4. SIDEBAR: RESEARCH CONTROLS ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        toggle_theme(); st.rerun()
    
    st.divider()
    tab_type = st.radio("Add Workstation", ["📝 Notes", "💻 Compiler"])
    if st.button("＋ OPEN NEW TAB", use_container_width=True):
        # Smart Tab logic: recycling lowest available ID
        ids = [nb["id"] for nb in st.session_state.notebooks if isinstance(nb, dict)]
        new_id = 1
        while new_id in ids: new_id += 1
        default_file = f"Log_{new_id}.txt" if tab_type == "📝 Notes" else f"Script_{new_id}.py"
        st.session_state.notebooks.append({"id": new_id, "file": default_file, "type": tab_type})
        st.rerun()

    st.divider()
    st.markdown("### 🖼️ Media Clipboard")
    img_up = st.file_uploader("Upload reference images", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if img_up:
        encoded = base64.b64encode(img_up.getvalue()).decode()
        st.session_state.media_vault[img_up.name] = encoded
        st.toast(f"Attached {img_up.name}")

# --- 5. MAIN RESEARCH WORKSPACE ---
if not st.session_state.notebooks:
    st.info("No active workstations. Use the sidebar to open a tab.")
else:
    # Safely generate tab labels
    tab_labels = [f"{nb.get('type', 'Tab')} {nb.get('id', i)}" for i, nb in enumerate(st.session_state.notebooks)]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id, fname, t_type = nb["id"], nb["file"], nb["type"]
            
            # Toolbar
            th1, th2 = st.columns([10, 1])
            th1.write(f"**FILE:** `{fname}`")
            if th2.button("✕", key=f"cls_{t_id}", help="Close Tab"):
                st.session_state.notebooks.pop(i); st.rerun()

            # --- MODE 1: NOTES & IMAGES ---
            if t_type == "📝 Notes":
                if st.session_state.media_vault:
                    with st.expander("🖼️ Attached Media Vault"):
                        for m_name, m_data in st.session_state.media_vault.items():
                            st.image(f"data:image/png;base64,{m_data}", caption=m_name, width=300)
                
                content = st.text_area("Research Notes", value=st.session_state.file_contents.get(fname, ""), 
                                       height=350, key=f"note_{t_id}", label_visibility="collapsed")
                st.session_state.file_contents[fname] = content
                st.markdown("---")
                st.markdown(content) # Note preview

            # --- MODE 2: INTERACTIVE COMPILER ---
            else:
                c1, c2 = st.columns([1, 1])
                run_btn = c1.button("▶️ RUN COMPILER", key=f"run_{t_id}", use_container_width=True, type="primary")
                live_mode = c2.toggle("⚡ LIVE MODE", key=f"live_{t_id}")
                
                code = st.text_area("Code Editor", value=st.session_state.file_contents.get(fname, ""), 
                                    height=250, key=f"code_{t_id}", label_visibility="collapsed")
                st.session_state.file_contents[fname] = code
                
                st.write("⌨️ **TERMINAL INPUT**")
                stdin_val = st.text_area("Inputs", key=f"in_{t_id}", height=70, label_visibility="collapsed")
                
                if run_btn or live_mode:
                    # FIX: Pre-padding stdin with 100 newlines to stop the ValueError
                    sys.stdin = io.StringIO(stdin_val + "\n" * 100)
                    out_buf = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(out_buf):
                            exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                        st.markdown("---")
                        res = out_buf.getvalue()
                        if res: st.code(res)
                        for f_n in plt.get_fignums():
                            st.pyplot(plt.figure(f_n)) # Show interactive graphs
                    except Exception:
                        if not live_mode: st.error(traceback.format_exc(limit=0))
                    finally:
                        sys.stdin = sys.__stdin__
                        plt.close('all')
