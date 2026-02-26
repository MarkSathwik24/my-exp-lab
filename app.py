import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import contextlib
import traceback
import os

# --- 1. INITIALIZE VIRTUAL FILE SYSTEM ---
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["welcome.py"]}
    st.session_state.file_contents = {"welcome.py": "# Welcome to Jarvis IDE\nprint('System Online.')"}
    st.session_state.notebooks = {"Tab 1": "welcome.py"}
    st.session_state.theme = 'dark'

# --- 2. THEME ENGINE & UI REFINEMENT ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Color Logic for High Contrast
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent, text_faint = "#0e1117", "#c9d1d9", "#161b22", "#58a6ff", "#8b949e"
    btn_bg, btn_fg = "#21262d", "#c9d1d9"
else:
    bg, fg, editor_bg, accent, text_faint = "#ffffff", "#24292f", "#f6f8fa", "#0969da", "#57606a"
    btn_bg, btn_fg = "#f3f4f6", "#24292f"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {fg}; }}
    
    /* Buttons & Inputs Contrast Fix */
    .stButton>button {{ background-color: {btn_bg} !important; color: {btn_fg} !important; border: 1px solid {text_faint}44 !important; border-radius: 6px; }}
    .stButton>button:hover {{ border-color: {accent} !important; color: {accent} !important; }}
    
    /* Toggle & Checkbox Text Contrast */
    .stCheckbox, .stToggle {{ color: {fg} !important; }}
    
    /* Editor Contrast */
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; }}
    
    /* Tabs Contrast */
    button[role="tab"] {{ background-color: {editor_bg} !important; color: {text_faint} !important; }}
    button[role="tab"][aria-selected="true"] {{ color: {accent} !important; border-top: 2px solid {accent} !important; }}

    /* Custom Icon Styles */
    .thin-icon {{ font-weight: 100 !important; font-size: 1.2rem; }}
    .close-btn {{ color: {text_faint} !important; border: none !important; background: transparent !important; }}
    .close-btn:hover {{ color: #ff4b4b !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DIALOG: CREATE NEW FILE ---
@st.dialog("Create New File")
def create_file_pop():
    st.write("Enter the name for your new Python script:")
    name = st.text_input("Filename", placeholder="e.g. simulation.py", label_visibility="collapsed")
    c1, c2 = st.columns(2)
    if c1.button("OK", use_container_width=True):
        if name:
            name = name if name.endswith(".py") else f"{name}.py"
            if name not in st.session_state.vfs["root"]:
                st.session_state.vfs["root"].append(name)
                st.session_state.file_contents[name] = f"# {name}\n"
                st.rerun()
    if c2.button("Cancel", use_container_width=True):
        st.rerun()

# --- 4. SIDEBAR: WORKSPACE & THEME ---
with st.sidebar:
    # Round Theme Toggle placed right of Title
    col_t1, col_t2 = st.columns([3, 1])
    col_t1.title("🛰️ Jarvis")
    if col_t2.button("☀️" if st.session_state.theme == 'dark' else "🌙", help="Toggle Theme"):
        toggle_theme()
        st.rerun()
    
    st.divider()
    mode = st.radio("Navigation", ["📁 Explorer", "📥 Upload"])
    
    if mode == "📁 Explorer":
        # Create File Button (Thinner Icon)
        if st.button("＋ New File", use_container_width=True):
            create_file_pop()

        st.divider()
        for f in st.session_state.vfs["root"]:
            c1, c2 = st.columns([5, 1])
            if c1.button(f"📄 {f}", key=f"open_{f}", use_container_width=True):
                idx = 1
                while f"Tab {idx}" in st.session_state.notebooks: idx += 1
                st.session_state.notebooks[f"Tab {idx}"] = f
                st.rerun()
            if c2.button("×", key=f"del_{f}", help="Delete File"):
                st.session_state.vfs["root"].remove(f)
                st.rerun()
    else:
        up_file = st.file_uploader("Drop .py scripts", type=['py'])
        if up_file:
            st.session_state.vfs["root"].append(up_file.name)
            st.session_state.file_contents[up_file.name] = up_file.getvalue().decode("utf-8")
            st.success("Uploaded to Explorer")

# --- 5. MAIN INTERFACE ---
tab_names = list(st.session_state.notebooks.keys())

if not tab_names:
    st.info("Open a file from the Explorer to start coding.")
else:
    ui_tabs = st.tabs(tab_names)
    for i, t_label in enumerate(tab_names):
        with ui_tabs[i]:
            fname = st.session_state.notebooks[t_label]
            
            # Tab Header with Thin Cross
            h1, h2 = st.columns([10, 1])
            h1.write(f"**{fname}**")
            if h2.button("✕", key=f"cls_{t_label}", help="Close Tab"):
                del st.session_state.notebooks[t_label]
                st.rerun()

            # Editor & Logic
            code = st.text_area("Editor", value=st.session_state.file_contents[fname], height=300, key=f"ed_{t_label}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            c_run, c_live = st.columns([1, 1])
            run_it = c_run.button("▶️ Run", type="primary", key=f"run_{t_label}", use_container_width=True)
            live = c_live.toggle("⚡ Live Engine", key=f"lv_{t_label}")

            if run_it or live:
                output_buffer = io.StringIO()
                figs = []
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(code, {'np': np, 'plt': plt, 'pd': pd, 'st': st}, {})
                    out = output_buffer.getvalue()
                    for fn in plt.get_fignums():
                        fig = plt.figure(fn)
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight", facecolor='white')
                        buf.seek(0); figs.append(buf.getvalue())
                    if out: st.markdown(f"<div class='output-block'>{out}</div>", unsafe_allow_html=True)
                    for fb in figs: st.image(fb)
                except Exception: st.error(traceback.format_exc(limit=0))
                finally: plt.close('all')
