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
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["Research_Log_01.txt"]}
    st.session_state.file_contents = {"Research_Log_01.txt": "## 🛰️ Project Notes\nStart logging aerospace data here..."}
    st.session_state.media_vault = {} # Store images as base64
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = [{"id": 1, "file": "Research_Log_01.txt", "type": "Notes"}]

# --- 2. CHROME-RESEARCH UI ---
def apply_research_ui():
    bg = "#0d1117" if st.session_state.theme == 'dark' else "#ffffff"
    fg = "#ffffff" if st.session_state.theme == 'dark' else "#202124"
    accent = "#58a6ff" if st.session_state.theme == 'dark' else "#1a73e8"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg}; color: {fg}; }}
        [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid #3c4043; }}
        .stMarkdown, label, .stHeader, .stCaption {{ color: {fg} !important; font-weight: bold; }}
        
        /* Chrome Tab Styling */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; padding-top: 8px; }}
        button[role="tab"] {{ color: {fg} !important; opacity: 0.6; }}
        button[role="tab"][aria-selected="true"] {{ opacity: 1; border-top: 2px solid {accent} !important; }}
        
        /* Note Editor High Contrast */
        .stTextArea textarea {{ background-color: {bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; border-radius: 8px; }}
    </style>
    """, unsafe_allow_html=True)

apply_research_ui()

# --- 3. SIDEBAR: RESEARCH CONTROLS ---
with st.sidebar:
    h_col, t_col = st.columns([3, 1])
    h_col.markdown(f"<h2 style='margin:0;'>🛰️ **MARK SPACE**</h2>", unsafe_allow_html=True)
    if t_col.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    st.divider()
    # ADD NEW TAB LOGIC
    tab_type = st.radio("New Tab Type", ["📝 Notes", "💻 Compiler"])
    if st.button("＋ OPEN NEW TAB", use_container_width=True):
        ids = [nb["id"] for nb in st.session_state.notebooks]
        new_id = 1
        while new_id in ids: new_id += 1
        default_file = f"Untitled_{new_id}.txt" if tab_type == "📝 Notes" else f"Script_{new_id}.py"
        st.session_state.notebooks.append({"id": new_id, "file": default_file, "type": tab_type})
        st.session_state.file_contents[default_file] = ""
        st.rerun()

    st.divider()
    st.markdown("### 🖼️ Image Clipboard")
    img_upload = st.file_uploader("Upload Images to Notes", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if img_upload:
        # Save image to vault for reference
        img_bytes = img_upload.getvalue()
        encoded = base64.b64encode(img_bytes).decode()
        st.session_state.media_vault[img_upload.name] = encoded
        st.success(f"Saved: {img_upload.name}")

# --- 4. THE MULTI-TAB RESEARCH WORKSPACE ---
if not st.session_state.notebooks:
    st.info("Start a new tab from the sidebar.")
else:
    tab_labels = [f"{nb['type']} {nb['id']}" for nb in st.session_state.notebooks]
    ui_tabs = st.tabs(tab_labels)
    
    for i, nb in enumerate(st.session_state.notebooks):
        with ui_tabs[i]:
            t_id, fname, t_type = nb["id"], nb["file"], nb["type"]
            
            # --- TAB TOOLBAR ---
            header_col1, header_col2, header_col3 = st.columns([12, 3, 1])
            header_col1.write(f"**FILE:** `{fname}`")
            if header_col2.button("💾 SAVE", key=f"save_{t_id}", use_container_width=True):
                st.toast(f"Saved {fname} to memory.")
            if header_col3.button("✕", key=f"close_{t_id}"):
                st.session_state.notebooks.pop(i); st.rerun()

            # --- MODE 1: NOTE TAKING WITH IMAGES ---
            if t_type == "📝 Notes":
                note_name = st.text_input("Note Name", value=fname, key=f"name_{t_id}")
                nb["file"] = note_name
                
                # Image Gallery for Copy-Paste Reference
                if st.session_state.media_vault:
                    with st.expander("🖼️ View Saved Images"):
                        for name, data in st.session_state.media_vault.items():
                            st.image(f"data:image/png;base64,{data}", caption=name, width=200)
                
                content = st.text_area("Write Notes (Markdown Supported)", 
                                       value=st.session_state.file_contents.get(fname, ""), 
                                       height=400, key=f"note_ed_{t_id}")
                st.session_state.file_contents[note_name] = content
                st.markdown("---")
                st.markdown(content) # Preview notes

            # --- MODE 2: INTERACTIVE PYTHON COMPILER ---
            else:
                code_name = st.text_input("Script Name", value=fname, key=f"name_{t_id}")
                nb["file"] = code_name
                
                c1, c2 = st.columns([1, 1])
                run_btn = c1.button("▶️ RUN COMPILER", key=f"run_{t_id}", use_container_width=True, type="primary")
                live_mode = c2.toggle("⚡ LIVE GRAPHING", key=f"live_{t_id}")
                
                code = st.text_area("Python Editor", value=st.session_state.file_contents.get(fname, ""), 
                                    height=300, key=f"code_ed_{t_id}", label_visibility="collapsed")
                st.session_state.file_contents[code_name] = code
                
                if run_btn or live_mode:
                    sys.stdin = io.StringIO("\n" * 100) # Prevents input error
                    out_buf = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(out_buf):
                            exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                        st.markdown("---")
                        output = out_buf.getvalue()
                        if output: st.code(output)
                        for fig_n in plt.get_fignums():
                            st.pyplot(plt.figure(fig_n)) # Renders graphs instantly
                    except Exception:
                        if not live_mode: st.error(traceback.format_exc(limit=0))
                    finally:
                        sys.stdin = sys.__stdin__
                        plt.close('all')
