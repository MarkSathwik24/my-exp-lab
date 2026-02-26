import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import sys
import contextlib
import traceback

# --- 1. INITIALIZE MARK SPACE SYSTEM ---
if 'vfs' not in st.session_state:
    st.session_state.vfs = {"root": ["calculator.py"]}
    st.session_state.file_contents = {"calculator.py": "# Basic Calculator\nx = int(input('Enter first number: '))\ny = int(input('Enter second number: '))\nprint(f'Sum: {x + y}')"}
    st.session_state.notebooks = {"Tab 1": "calculator.py"}
    st.session_state.theme = 'dark'

# --- 2. UNIFIED THEME ENGINE (SIDEBAR & MAIN) ---
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Color Logic for Full-System Contrast
if st.session_state.theme == 'dark':
    bg, fg, editor_bg, accent = "#0e1117", "#c9d1d9", "#161b22", "#58a6ff"
    sidebar_bg, sidebar_fg = "#0e1117", "#c9d1d9"
    btn_bg, btn_fg = "#21262d", "#c9d1d9"
else:
    bg, fg, editor_bg, accent = "#ffffff", "#24292f", "#f6f8fa", "#0969da"
    sidebar_bg, sidebar_fg = "#f6f8fa", "#24292f"
    btn_bg, btn_fg = "#f3f4f6", "#24292f"

st.markdown(f"""
<style>
    /* Full App & Sidebar Theme */
    .stApp {{ background-color: {bg}; color: {fg}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; color: {sidebar_fg} !important; border-right: 1px solid {accent}44; }}
    [data-testid="stSidebar"] .stMarkdown p {{ color: {sidebar_fg} !important; }}
    
    /* Input & Toggle Contrast Fix */
    .stCheckbox, .stToggle, .stMarkdown, label {{ color: {fg} !important; }}
    
    /* Circular Theme Toggle Alignment */
    .theme-btn-container {{ display: flex; align-items: center; justify-content: space-between; }}
    .round-toggle {{ border-radius: 50% !important; width: 40px !important; height: 40px !important; padding: 0 !important; display: flex; align-items: center; justify-content: center; border: 1px solid {accent}44 !important; background: {btn_bg} !important; }}

    /* Editor & Terminal Output */
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; background-color: {editor_bg} !important; color: {fg} !important; border: 1px solid {accent}44 !important; }}
    .output-block {{ background-color: {editor_bg}; color: {fg}; padding: 15px; border-left: 4px solid {accent}; font-family: monospace; border-radius: 4px; margin-top: 10px; white-space: pre-wrap; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DIALOG: CREATE NEW FILE ---
@st.dialog("New File")
def create_file_pop():
    name = st.text_input("Filename", placeholder="script.py")
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

# --- 4. SIDEBAR: MARK SPACE CONTROLS ---
with st.sidebar:
    # Circular toggle in-line with Mark Space title
    col_t1, col_t2 = st.columns([3, 1])
    col_t1.markdown(f"<h2 style='margin:0; padding:0; line-height:40px;'>Mark Space</h2>", unsafe_allow_html=True)
    if col_t2.button("☀️" if st.session_state.theme == 'dark' else "🌙", key="theme_toggle", help="Toggle Theme"):
        toggle_theme()
        st.rerun()
    
    st.divider()
    mode = st.radio("Navigation", ["📁 Explorer", "📥 Upload"])
    
    if mode == "📁 Explorer":
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
            if c2.button("✕", key=f"del_{f}"):
                st.session_state.vfs["root"].remove(f)
                st.rerun()
    else:
        up_file = st.file_uploader("Drop .py scripts", type=['py'])
        if up_file:
            st.session_state.vfs["root"].append(up_file.name)
            st.session_state.file_contents[up_file.name] = up_file.getvalue().decode("utf-8")
            st.success("Uploaded to Explorer")

# --- 5. MAIN INTERFACE & EXECUTION ENGINE ---
tab_names = list(st.session_state.notebooks.keys())

if not tab_names:
    st.info("Open a file from the Explorer to start.")
else:
    ui_tabs = st.tabs(tab_names)
    for i, t_label in enumerate(tab_names):
        with ui_tabs[i]:
            fname = st.session_state.notebooks[t_label]
            
            h1, h2 = st.columns([10, 1])
            h1.write(f"**Editing: {fname}**")
            if h2.button("✕", key=f"cls_{t_label}"):
                del st.session_state.notebooks[t_label]
                st.rerun()

            # Editor
            code = st.text_area("Source", value=st.session_state.file_contents[fname], height=250, key=f"ed_{t_label}", label_visibility="collapsed")
            st.session_state.file_contents[fname] = code
            
            # Interactive Terminal Inputs
            user_input_val = st.text_area("Terminal Input (one per line)", placeholder="Enter values for input() here...", key=f"in_{t_label}", height=80)
            
            c_run, c_live = st.columns([1, 1])
            run_it = c_run.button("▶️ Run Code", type="primary", key=f"run_{t_label}", use_container_width=True)
            live = c_live.toggle("⚡ Live Engine Mode", key=f"lv_{t_label}")

            if run_it or live:
                output_buffer = io.StringIO()
                # Simulate stdin using the input text area
                input_stream = io.StringIO(user_input_val + "\n" * 10)
                original_stdin = sys.stdin
                sys.stdin = input_stream
                
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
                    
                    if out or figs:
                        st.markdown("---")
                        if out: st.markdown(f"<div class='output-block'>{out}</div>", unsafe_allow_html=True)
                        for fb in figs: st.image(fb)
                except Exception:
                    st.error(traceback.format_exc(limit=0))
                finally:
                    sys.stdin = original_stdin
                    plt.close('all')
