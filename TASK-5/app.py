import streamlit as st

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Text Processor", page_icon="📝", layout="wide")

# --- 2. INITIALIZE SESSION STATE (For the Clear Button) ---
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def reset_uploader():
    # Incrementing the key forces Streamlit to create a "fresh" uploader widget
    st.session_state.uploader_key += 1

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2b1055 0%, #050505 60%);
        color: #ffffff;
    }
    .main .block-container {
        max-width: 900px;
        padding-top: 8rem; 
    }
    .instruction-text {
        text-align: center;
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    [data-testid="stFileUploader"] {
        background-color: #0c0c0c;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 40px;
    }
    [data-testid="stFileUploader"]:hover {
        border: 1px solid #7d2ae8;
        box-shadow: 0px 0px 20px rgba(125, 42, 232, 0.1);
    }
    div.stButton > button:first-child {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
    }
    .stTextArea textarea {
        background-color: #080808 !important;
        color: #ffffff !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 8px;
    }
    hr {
        border-top: 1px solid #1f1f1f;
        margin: 3rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. UI CONTENT ---

st.markdown("<p class='instruction-text'>SELECT A DOCUMENT TO BEGIN PROCESSING</p>", unsafe_allow_html=True)

# Create the uploader with a dynamic key
uploaded_file = st.file_uploader(
    "Document Upload", 
    type="txt", 
    label_visibility="collapsed", 
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file is not None:
    try:
        # Read file
        content = uploaded_file.getvalue().decode("utf-8")
        st.markdown("<br>", unsafe_allow_html=True)

        # Content box
        st.text_area(label="Viewer", value=content, height=450, label_visibility="collapsed")
        
        # Action button to Clear
        if st.button("CLEAR"):
            reset_uploader() # Update the key
            st.rerun()      # Refresh the page to show empty uploader

    except Exception as e:
        st.error(f"System Error: {e}")

else:
    # Minimalist Footer
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True) 
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<p style='color:#333; font-size:12px;'>ENCRYPTED PORTAL</p>", unsafe_allow_html=True)
    with f2: st.markdown("<p style='color:#333; font-size:12px; text-align:center;'>STATUS: READY</p>", unsafe_allow_html=True)
    with f3: st.markdown("<p style='color:#333; font-size:12px; text-align:right;'>V.2.1.0</p>", unsafe_allow_html=True)