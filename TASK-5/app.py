import streamlit as st
import pandas as pd
import sqlite3
import time
import os
import io
import csv
import plotly.express as px 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from workers import analyze_chunk

# --- 1. CONFIGURATION ---
DB_NAME = "CORE_VAULT.db"
SENDER_EMAIL = "sowjanya2237@gmail.com"
SENDER_PASSWORD = "fyis cnux ctxn fflq"

def run_app():
    st.set_page_config(page_title="Parallel System Pro", page_icon="⚡", layout="wide")

    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0
    if 'uploaded_data_list' not in st.session_state:
        st.session_state.uploaded_data_list = None

    # --- 2. CUSTOM UI CSS ---
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle at 50% -20%, #2b1055 0%, #050505 60%); color: #ffffff; }
        [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #1f1f1f; }
        .main .block-container { max-width: 1000px; padding-top: 5rem; }
        .instruction-text { text-align: center; color: #888888; font-size: 1.1rem; margin-bottom: 2rem; letter-spacing: 1px; }
        [data-testid="stFileUploader"] { background-color: #0c0c0c; border: 1px solid #1f1f1f; border-radius: 12px; padding: 40px; }
        div.stButton > button:first-child, div.stDownloadButton > button:first-child { 
            background: linear-gradient(180deg, #ffffff 0%, #e0e0e0 100%) !important; 
            color: #000000 !important; border: none !important; border-radius: 6px !important; 
            padding: 0.8rem !important; font-weight: 800 !important; width: 100%;
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
        }
        div.stButton > button:first-child:hover { background: #ffffff !important; }
        [data-testid="stMetric"] { background-color: #0c0c0c; border: 1px solid #1f1f1f; padding: 20px; border-radius: 10px; }
        [data-testid="stDataFrame"] { background-color: #0c0c0c; border-radius: 10px; border: 1px solid #1f1f1f; }
        hr { border-top: 1px solid #333333; margin: 2rem 0; }
        </style>
        """, unsafe_allow_html=True)

    # --- 3. NAVIGATION ---
    with st.sidebar:
        st.markdown("<h2 style='color:white; letter-spacing:2px;'>CORE SYSTEM</h2>", unsafe_allow_html=True)
        page = st.radio("Navigate", ["File Portal", "Process Engine", "Registry Vault", "Report Distribution"])
        st.markdown("---")
        st.markdown(f"<p style='color:#00ffcc; font-family:monospace; font-size:14px; font-weight:bold;'>DATABASE: {DB_NAME}</p>", unsafe_allow_html=True)

    # --- PAGE 1: FILE PORTAL ---
    if page == "File Portal":
        st.markdown("<p class='instruction-text'>SELECT A DOCUMENT TO BEGIN PROCESSING</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload", type=["txt", "csv"], label_visibility="collapsed", key=f"u_{st.session_state.uploader_key}")

        if uploaded_file is not None:
            if st.session_state.uploaded_data_list is None:
                with st.spinner("Analyzing dataset structure..."):
                    try:
                        df = pd.read_csv(uploaded_file, sep=",")
                        st.markdown("### Data Preview")
                        st.dataframe(df.head(5), width="stretch")

                        target_col = st.selectbox("Select Text Column to Analyze", df.columns.tolist(), index=0)
                        sample = df[target_col].dropna().head(100).astype(str)

                        if pd.api.types.is_numeric_dtype(df[target_col]) or sample.str.len().mean() < 15:
                            st.error(f"🛑 INVALID SELECTION: '{target_col}' is numerical or too short.")
                        else:
                            if st.button("CONFIRM DATASET"):
                                st.session_state.uploaded_data_list = df[target_col].dropna().astype(str).tolist()
                                st.rerun()
                    except Exception as e:
                        st.error(f"Structure Error: {e}")

            if st.session_state.uploaded_data_list:
                if st.button("CLEAR WORKSPACE"):
                    st.session_state.uploaded_data_list = None
                    st.session_state.uploader_key += 1
                    st.rerun()

    # --- PAGE 2: PROCESS ENGINE ---
    elif page == "Process Engine":
        st.markdown("<p class='instruction-text'>INITIALIZE ANALYSIS SEQUENCE</p>", unsafe_allow_html=True)

        if st.session_state.uploaded_data_list:
            data = st.session_state.uploaded_data_list
            st.info(f"Target Workload: {len(data):,} entries.")

            if st.button("RUN"):
                import multiprocessing

                start_time = time.time()

                c_size = 100000

                chunks = [(i, data[i:i + c_size]) for i in range(0, len(data), c_size)]

                with st.status("processing...", expanded=True) as status:
                    conn = sqlite3.connect(DB_NAME)

                    conn.execute("PRAGMA journal_mode = WAL")
                    conn.execute("PRAGMA synchronous = OFF")
                    conn.execute("PRAGMA temp_store = MEMORY")
                    conn.execute("PRAGMA cache_size = 1000000")
                    conn.execute("PRAGMA locking_mode = EXCLUSIVE") 

                    cursor = conn.cursor()
                    cursor.execute("DROP TABLE IF EXISTS results")
                    cursor.execute("CREATE TABLE results (text TEXT, score INTEGER, sentiment TEXT, timestamp TEXT)")

                    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                        for batch_result in executor.map(analyze_chunk, chunks, chunksize=2):
                            payload = [(data[r[0]], r[1], r[2], r[3]) for r in batch_result]
                            cursor.executemany("INSERT INTO results VALUES (?, ?, ?, ?)", payload)

                    conn.commit()
                    conn.close()
                    status.update(label="Completed", state="complete")

                st.success(f" PROCESSED {len(data):,} RECORDS IN {(time.time() - start_time):.2f}s")

        else:
            st.warning("PLEASE UPLOAD A FILE")
    
    # --- PAGE 3: REGISTRY VAULT ---
    elif page == "Registry Vault":
        st.markdown("<p class='instruction-text'>CENTRAL REGISTRY RECORDS</p>", unsafe_allow_html=True)
        if os.path.exists(DB_NAME):
            conn = sqlite3.connect(DB_NAME)
            st.markdown("### 🔍 Registry Filter")
            f_choice = st.selectbox("Select results", ["All Records", "Positive", "Negative", "Neutral", "Spam", "Abusive", "Urgent", "Suggestion"])
            query = "SELECT * FROM results" if f_choice == "All Records" else f"SELECT * FROM results WHERE sentiment='{f_choice}'"
            db_df_preview = pd.read_sql_query(f"{query} ORDER BY rowid DESC LIMIT 500", conn)
            df_sent = pd.read_sql_query("SELECT sentiment FROM results", conn); conn.close()
            
            st.markdown(f"### Registry Matrix ({f_choice})")
            st.dataframe(db_df_preview, use_container_width=True, height=400)
            
            if not df_sent.empty:
                st.markdown("---"); st.markdown("### Sentiment Distribution Analysis")
                col_l, col_chart, col_r = st.columns([1, 2, 1])
                with col_chart:
                    counts = df_sent['sentiment'].value_counts().reset_index(); counts.columns = ['S', 'C']
                    fig = px.pie(counts, values='C', names='S', hole=0.6, color='S', 
                                color_discrete_map={'Positive': '#00ffcc', 'Negative': '#ff0066', 'Neutral': '#888888', 'Spam': '#ffaa00', 'Abusive': '#ff0000', 'Urgent': '#ff4b4b', 'Suggestion': '#636efa'}, height=350)
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=20, b=20, l=0, r=0), legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
                    st.plotly_chart(fig, use_container_width=True)
                    
    # --- PAGE 4: REPORT DISTRIBUTION ---
    elif page == "Report Distribution":
        st.markdown("<p class='instruction-text'>DISPATCH SYSTEM INTELLIGENCE</p>", unsafe_allow_html=True)
        st.markdown("### 📥 Dataset Export")
        if os.path.exists(DB_NAME):
            if st.button("PREPARE ENTIRE VAULT FOR DOWNLOAD"):
                with st.status("PREPARING...", expanded=True) as status:
                    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("SELECT * FROM results")
                    output = io.StringIO(); writer = csv.writer(output); writer.writerow([i[0] for i in cursor.description])
                    while True:
                        rows = cursor.fetchmany(50000); writer.writerows(rows)
                        if not rows: break
                    conn.close(); csv_bytes = output.getvalue().encode('utf-8'); output.close(); status.update(label="Export Ready!", state="complete")
                    st.download_button("📥 DOWNLOAD DATABASE", csv_bytes, "review_database.csv", "text/csv")
        st.markdown("---")
        st.markdown("### 📧 Detailed Intelligence Email")
        receiver_email = st.text_input("Enter Destination Email Address", placeholder="client@example.com")
        
        if st.button("DISPATCH REPORT"):
            if not receiver_email: st.error("Provide email.")
            else:
                with st.status("Compiling Report...", expanded=True) as status:
                    try:
                        conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                        total = cursor.execute("SELECT COUNT(*) FROM results").fetchone()[0]
                        s_data = cursor.execute("SELECT sentiment, COUNT(*) FROM results GROUP BY sentiment").fetchall()
                        c_dict = {row[0]: row[1] for row in s_data}
                        
                        # Fetch highlights for ALL 7 categories in correct order
                        order = ["Positive", "Negative", "Neutral", "Urgent", "Abusive", "Spam", "Suggestion"]
                        samples = {cat: cursor.execute(f"SELECT text FROM results WHERE sentiment='{cat}' LIMIT 3").fetchall() for cat in order}
                        df_sample_att = pd.read_sql_query("SELECT * FROM results ORDER BY rowid DESC LIMIT 1000", conn); conn.close()
                        
                        # Chart Image
                        chart_df = pd.DataFrame([{'S': k, 'C': v} for k, v in c_dict.items()])
                        fig = px.pie(chart_df, values='C', names='S', hole=0.6, color='S', color_discrete_map={'Positive': '#00ffcc', 'Negative': '#ff0066', 'Neutral': '#888888', 'Spam': '#ffaa00', 'Abusive': '#ff0000', 'Urgent': '#ff4b4b', 'Suggestion': '#636efa'})
                        img_bytes = fig.to_image(format="png")
                        
                        msg = MIMEMultipart(); msg['From'] = SENDER_EMAIL; msg['To'] = receiver_email; msg['Subject'] = f"Full System Intelligence Report - {datetime.now().strftime('%Y-%m-%d')}"
                        
                        sections = []
                        for i, cat in enumerate(order, 1):
                            count = c_dict.get(cat, 0)
                            perc = (count/total*100) if total > 0 else 0
                            highlights = "\n".join([f"- {s[0][:150]}..." for s in samples[cat]]) if samples[cat] else "- None detected in this vault."
                            sections.append(f"{i}. {cat.upper()} REVIEWS/ALERTS: {count:,} ({perc:.1f}%)\nSample Highlights:\n{highlights}")
                        
                        email_body = f"""SYSTEM ANALYSIS OVERVIEW:
-------------------------
We have successfully processed the entire dataset stored in the vault.
Here are the findings from the total of {total:,} records:

{chr(10).join(sections)}

CONCLUSION:
A visual distribution chart is attached. A sample CSV database is also attached."""
                        msg.attach(MIMEText(email_body, 'plain'))
                        
                        # Attachments
                        p_img = MIMEBase('application', 'octet-stream'); p_img.set_payload(img_bytes); encoders.encode_base64(p_img); p_img.add_header('Content-Disposition', 'attachment; filename="pie_chart.png"'); msg.attach(p_img)
                        p_csv = MIMEBase('application', 'octet-stream'); p_csv.set_payload(df_sample_att.to_csv(index=False).encode('utf-8')); encoders.encode_base64(p_csv); p_csv.add_header('Content-Disposition', 'attachment; filename="Review_dataset.csv"'); msg.attach(p_csv)
                        
                        srv = smtplib.SMTP('smtp.gmail.com', 587); srv.starttls(); srv.login(SENDER_EMAIL, SENDER_PASSWORD)
                        srv.send_message(msg); srv.quit()
                        status.update(label="Dispatch Successful!", state="complete"); st.success(f"Full intelligence report sent to {receiver_email}")
                    except Exception as e: st.error(f"Error: {e}")

if __name__ == "__main__":
    run_app()