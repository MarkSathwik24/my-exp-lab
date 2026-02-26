import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg as la
import pandas as pd
import io
import contextlib
import sys
import traceback

# --- 1. SYSTEM CONFIG & MATLAB UI STYLING ---
st.set_page_config(page_title="Jarvis | MATLAB Desktop", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* MATLAB Desktop Colors & Fonts */
    .main { background-color: #ffffff; color: #000000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Command Window */
    .cmd-window { background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace; 
                  padding: 10px; border: 1px solid #cccccc; height: 400px; overflow-y: auto; font-size: 14px;}
    .cmd-prompt { color: #000000; font-weight: bold; }
    .cmd-error { color: #d9534f; font-weight: bold; }
    
    /* Editor */
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace !important; font-size: 14px !important; border: 1px solid #cccccc !important; }
    
    /* Sidebar (Workspace) */
    [data-testid="stSidebar"] { background-color: #f3f3f3; border-right: 1px solid #cccccc; }
    
    /* Buttons */
    .stButton>button { background-color: #f0f0f0; color: #000; border: 1px solid #cccccc; border-radius: 2px; }
    .stButton>button:hover { background-color: #e5f1fb; border-color: #0078d7; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PERSISTENT WORKSPACE MEMORY ---
# This is the "Base Workspace". Variables live here forever until cleared.
if 'workspace' not in st.session_state:
    st.session_state.workspace = {'np': np, 'plt': plt, 'la': la, 'pd': pd}

# This stores the unified output history for the Command Window
if 'cmd_history' not in st.session_state:
    st.session_state.cmd_history = [
        "MATLAB [Jarvis Edition]\nReady for aerospace control analysis.\n"
    ]

# Virtual Current Folder
if 'saved_scripts' not in st.session_state:
    st.session_state.saved_scripts = {}

# --- 3. EXECUTION ENGINE ---
def execute_code(code_str, source_name="Command Line"):
    output_buffer = io.StringIO()
    
    try:
        # Redirect prints to our buffer
        with contextlib.redirect_stdout(output_buffer):
            # If it's a single line, try to eval it first (like typing 'A' to see the matrix)
            try:
                result = eval(code_str, globals(), st.session_state.workspace)
                if result is not None:
                    print(result)
            except SyntaxError:
                # If eval fails (because it's a full script or assignment), use exec
                exec(code_str, globals(), st.session_state.workspace)
        
        # Capture text output
        out_text = output_buffer.getvalue()
        if out_text:
            st.session_state.cmd_history.append(out_text)
            
        # Capture and log any plots generated
        fig_nums = plt.get_fignums()
        if fig_nums:
            st.session_state.cmd_history.append("[Figure Window Updated]")
            # Display plots immediately so user sees them
            for i in fig_nums:
                st.pyplot(plt.figure(i))
                plt.close(plt.figure(i))
                
    except Exception as e:
        error_msg = f"<span class='cmd-error'>Error in {source_name}:\n{traceback.format_exc(limit=0)}</span>"
        st.session_state.cmd_history.append(error_msg)

# --- 4. SIDEBAR: WORKSPACE & CURRENT FOLDER ---
with st.sidebar:
    st.markdown("### Workspace")
    workspace_data = []
    # Show active variables (ignoring imported modules/functions to keep it clean)
    for k, v in st.session_state.workspace.items():
        if not k.startswith('_') and type(v).__name__ not in ['module', 'function', 'builtin_function_or_method']:
            # Try to get matrix sizes like MATLAB does
            if isinstance(v, np.ndarray):
                val_desc = f"{v.shape} double"
            elif isinstance(v, list):
                val_desc = f"1x{len(v)} cell"
            else:
                val_desc = str(type(v).__name__)
            workspace_data.append({"Name": k, "Value/Size": val_desc})
            
    if workspace_data:
        st.dataframe(pd.DataFrame(workspace_data), hide_index=True)
    else:
        st.write("Workspace is empty.")
        
    if st.button("Clear Workspace"):
        st.session_state.workspace = {'np': np, 'plt': plt, 'la': la, 'pd': pd}
        st.session_state.cmd_history.append("<span class='cmd-error'>Workspace cleared.</span>")
        st.rerun()

    st.markdown("### Current Folder")
    for script_name in st.session_state.saved_scripts.keys():
        st.write(f"📄 {script_name}")

# --- 5. MAIN DESKTOP TABS ---
st.title("Jarvis Desktop Environment")
tab_cmd, tab_editor = st.tabs(["💻 Command Window", "📝 Editor"])

# TAB 1: COMMAND WINDOW
with tab_cmd:
    # Render the history log
    history_html = "<div class='cmd-window'>"
    for item in st.session_state.cmd_history:
        # Check if it's a raw command prompt input
        if item.startswith(">>"):
            history_html += f"<span class='cmd-prompt'>{item}</span><br>"
        else:
            # Replace newlines with breaks for HTML rendering
            history_html += f"{item.replace(chr(10), '<br>')}<br>"
    history_html += "</div>"
    
    st.markdown(history_html, unsafe_allow_html=True)
    
    # Command Line Input
    cmd_input = st.chat_input("Enter command... (e.g., A = np.array([[0, 1], [-2, -3]]))")
    if cmd_input:
        st.session_state.cmd_history.append(f">> {cmd_input}")
        execute_code(cmd_input)
        st.rerun() # Refresh to show new history

# TAB 2: EDITOR
with tab_editor:
    col_file, col_btns = st.columns([3, 1])
    with col_file:
        file_name = st.text_input("File Name:", value="optimal_control_LQR.py")
        
    default_code = """# Continuous-Time LQR Design
# x_dot = A*x + B*u

A = np.array([[0, 1], 
              [-2, -3]])
              
B = np.array([[0], 
              [1]])
              
Q = np.eye(2) # State penalty
R = np.array([[1]]) # Control penalty

# Solve Continuous Riccati Equation
P = la.solve_continuous_are(A, B, Q, R)

# Calculate optimal feedback gain K
K = la.inv(R) @ B.T @ P

print("Optimal Gain Matrix (K):")
print(K)

# Check closed-loop eigenvalues
Ac = A - B @ K
eigenvalues, _ = la.eig(Ac)
print("\\nClosed-Loop Poles:")
print(eigenvalues)"""

    # Load from virtual folder if it exists, otherwise use default
    current_code = st.session_state.saved_scripts.get(file_name, default_code)
    
    editor_code = st.text_area("Code", value=current_code, height=400, label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save to Current Folder", use_container_width=True):
            st.session_state.saved_scripts[file_name] = editor_code
            st.success(f"Saved {file_name}")
            
    with c2:
        if st.button("▶ Run Script", type="primary", use_container_width=True):
            # Log the execution in the command window
            st.session_state.cmd_history.append(f">> run {file_name}")
            # Execute the code
            execute_code(editor_code, source_name=file_name)
            st.success("Executed! Check the Command Window tab for outputs.")
