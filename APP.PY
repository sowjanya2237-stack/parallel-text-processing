import streamlit as st
import pandas as pd
import sqlite3
import re
import time
from datetime import datetime
import os

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="Text System Pro", page_icon="🟣", layout="wide")

# Database Name from your config
DB_NAME = "performance_test.db"

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'uploaded_content' not in st.session_state:
    st.session_state.uploaded_content = None

# --- 2. SCORING RULES & LOGIC (From your provided code) ---
positive_words = ["good", "great", "excellent", "amazing", "love", "awesome", "fantastic", "perfect", "nice", "satisfied", "delicious", "fresh", "happy"]
negative_words = ["bad", "worst", "poor", "terrible", "hate", "awful", "disappointed", "broken", "damaged", "stale", "mushy", "expensive"]

regex_patterns = {
    r"never\s+buy\s+again": -3, r"won'?t\s+buy\s+again": -3, r"no\s+flavor": -2, r"no\s+taste": -2,
    r"arrived\s+.*melted": -3, r"solid\s+mass\s+of\s+melted": -3, r"stale": -3, r"diarrhea": -3,
    r"itching\s+increased": -3, r"too\s+expensive": -2, r"not\s+as\s+advertised": -3, r"would\s+not\s+buy\s+again": -3,
    r"highly\s+recommend": 3, r"definitely\s+recommend": 3, r"love\s+this": 2, r"very\s+satisfied": 2,
    r"great\s+taste": 2, r"delicious": 2, r"arrived\s+on\s+time": 2, r"works\s+wonders": 3,
    r"great\s+deal": 2, r"fresh\s+and\s+delicious": 2,
}

def calculate_sentiment(text):
    score = 0
    text = text.lower()
    words = text.split()
    for i, word in enumerate(words):
        if word in positive_words:
            score += -1 if (i > 0 and words[i-1] == "not") else 1
        if word in negative_words:
            score += 1 if (i > 0 and words[i-1] == "not") else -1
    for pattern, weight in regex_patterns.items():
        if re.search(pattern, text):
            score += weight
    return score

def assign_label(score):
    if score >= 1: return "Positive"
    elif score <= -1: return "Negative"
    else: return "Neutral"

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 50% -20%, #2b1055 0%, #050505 60%); color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #1f1f1f; }
    .main .block-container { max-width: 1000px; padding-top: 5rem; }
    .instruction-text { text-align: center; color: #888888; font-size: 1.1rem; margin-bottom: 2rem; letter-spacing: 1px; }
    [data-testid="stFileUploader"] { background-color: #0c0c0c; border: 1px solid #1f1f1f; border-radius: 12px; padding: 40px; }
    div.stButton > button:first-child { background-color: #ffffff !important; color: #000000 !important; border-radius: 6px !important; padding: 0.5rem 2rem !important; font-weight: 600 !important; width: 100%; }
    .stTextArea textarea { background-color: #080808 !important; color: #ffffff !important; border: 1px solid #1f1f1f !important; border-radius: 8px; }
    [data-testid="stMetric"] { background-color: #0c0c0c; border: 1px solid #1f1f1f; padding: 15px; border-radius: 10px; }
    /* Table Styling */
    [data-testid="stDataFrame"] { background-color: #0c0c0c; border-radius: 10px; border: 1px solid #1f1f1f; }
    hr { border-top: 1px solid #1f1f1f; margin: 2rem 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>CORE MENU</h2>", unsafe_allow_html=True)
    page = st.radio("Navigate", ["Upload Portal", "Scoring Engine", "Archive Vault"])
    st.markdown("---")
    st.markdown("<p style='color:#444; font-size:10px;'>DATABASE: ONLINE</p>", unsafe_allow_html=True)

# --- 5. PAGE 1: UPLOAD PORTAL ---
if page == "Upload Portal":
    st.markdown("<p class='instruction-text'>SELECT A DOCUMENT TO BEGIN PROCESSING</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Document Upload", type="txt", label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")

    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        st.session_state.uploaded_content = content
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area(label="Viewer", value=content, height=400, label_visibility="collapsed")
        if st.button("CLEAR"):
            st.session_state.uploader_key += 1
            st.session_state.uploaded_content = None
            st.rerun()
    else:
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        f1, f2, f3 = st.columns(3)
        with f1: st.markdown("<p style='color:#333; font-size:12px;'>ENCRYPTED PORTAL</p>", unsafe_allow_html=True)
        with f2: st.markdown("<p style='color:#333; font-size:12px; text-align:center;'>STATUS: READY</p>", unsafe_allow_html=True)
        with f3: st.markdown("<p style='color:#333; font-size:12px; text-align:right;'>V.2.1.0</p>", unsafe_allow_html=True)

# --- 6. PAGE 2: SCORING ENGINE ---
elif page == "Scoring Engine":
    st.markdown("<p class='instruction-text'>ANALYSIS COMMAND CENTER</p>", unsafe_allow_html=True)
    if st.session_state.uploaded_content:
        lines = [line.strip() for line in st.session_state.uploaded_content.split('\n') if line.strip()]
        st.info(f"Loaded {len(lines)} text entries for processing.")
        
        if st.button("INITIALIZE RUN"):
            results = []
            progress_bar = st.progress(0)
            start_time = time.time()
            
            for i, text in enumerate(lines):
                score = calculate_sentiment(text)
                sentiment = assign_label(score)
                results.append({
                    "text": text,
                    "score": score,
                    "sentiment": sentiment,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                progress_bar.progress((i + 1) / len(lines))
            
            end_time = time.time()
            df = pd.DataFrame(results)
            
            # Save to performance_test.db
            conn = sqlite3.connect(DB_NAME)
            df.to_sql("results", conn, if_exists="append", index=False)
            conn.close()

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("PROCESSED", len(lines))
            with c2: st.metric("TIME", f"{end_time - start_time:.4f}s")
            with c3: st.metric("STATUS", "SAVED TO DB")
            
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df['sentiment'].value_counts())
    else:
        st.warning("No data detected. Please upload a file in the 'Upload Portal' first.")

# --- 7. PAGE 3: ARCHIVE VAULT (The Database Page) ---
elif page == "Archive Vault":
    st.markdown("<p class='instruction-text'>HISTORICAL DATABASE RECORDS</p>", unsafe_allow_html=True)

    if os.path.exists(DB_NAME):
        try:
            conn = sqlite3.connect(DB_NAME)
            # Query the database
            query = "SELECT * FROM results ORDER BY timestamp DESC"
            db_df = pd.read_sql_query(query, conn)
            conn.close()

            if not db_df.empty:
                # Dashboard stats for the DB
                m1, m2, m3 = st.columns(3)
                with m1: st.metric("DB RECORDS", len(db_df))
                with m2: st.metric("POS %", f"{(len(db_df[db_df['sentiment']=='Positive'])/len(db_df)*100):.1f}%")
                with m3: st.metric("NEG %", f"{(len(db_df[db_df['sentiment']=='Negative'])/len(db_df)*100):.1f}%")

                st.markdown("### Persistent Data Table")
                # Using st.dataframe for a professional look
                st.dataframe(
                    db_df, 
                    use_container_width=True, 
                    height=500,
                    column_config={
                        "text": st.column_config.TextColumn("Content", width="large"),
                        "score": st.column_config.NumberColumn("Score"),
                        "sentiment": st.column_config.TextColumn("Label"),
                        "timestamp": st.column_config.TextColumn("Date/Time")
                    }
                )
                
                if st.button("DOWNLOAD FULL ARCHIVE"):
                    st.download_button("Export as CSV", db_df.to_csv(index=False), "archive_export.csv", "text/csv")

            else:
                st.info("Database table is empty. Run scoring to populate records.")
        except Exception as e:
            st.error(f"Database Read Error: {e}")
    else:
        st.error("Database file not found. Please run the Scoring Engine first to create 'performance_test.db'.")