import streamlit as st
import os
import pickle
import re
import pandas as pd
import plotly.express as px
import time
import json
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURATION & AFFILIATE LINKS ---
LINK_ROCKET_MONEY = "https://www.rocketmoney.com/?utm_source=vampire_hunter_tool&utm_medium=referral&utm_campaign=audit_tool" 
LINK_POCKETGUARD = "https://pocketguard.com/?utm_source=vampire_hunter_tool&utm_medium=referral&utm_campaign=audit_tool"
LINK_TRIM = "https://www.asktrim.com/?utm_source=vampire_hunter_tool&utm_medium=referral&utm_campaign=audit_tool"

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

st.set_page_config(page_title="Vampire Subscription Hunter", page_icon="🧛", layout="wide", initial_sidebar_state="expanded")

# --- HELPER: RECURSIVE DICT CONVERTER ---
def recursive_to_dict(obj):
    """Converts Streamlit Secrets (AttrDict) into a standard Python dict."""
    if hasattr(obj, "items"):
        return {k: recursive_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [recursive_to_dict(v) for v in obj]
    return obj

# --- AUTHENTICATION LOGIC (MEMORY ONLY) ---
@st.cache_data(show_spinner=False)
def get_gmail_service():
    creds = None
    
    # 1. Load Token if exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 2. Login Flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # DIRECT MEMORY READ: No file creation needed
            if 'google_credentials' in st.secrets:
                secrets_dict = recursive_to_dict(st.secrets['google_credentials'])
                
                # Fix format if user pasted "flat" keys
                if "installed" not in secrets_dict and "web" not in secrets_dict:
                    secrets_dict = {"installed": secrets_dict}
                
                # This line prevents the JSONDecodeError!
                flow = InstalledAppFlow.from_client_config(secrets_dict, SCOPES)
                
            elif os.path.exists('credentials.json'):
                # Fallback for local testing
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else:
                st.error("🚨 Missing Credentials")
                return None

            # open_browser=False prevents server crashes on Cloud
            creds = flow.run_local_server(port=0, open_browser=False)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

# --- SCANNER LOGIC ---
def categorize_subscription(subject, sender, snippet):
    text = f"{subject} {sender} {snippet}".lower()
    if any(w in text for w in ['netflix', 'hulu', 'disney', 'hbo', 'prime', 'youtube']): return "Streaming"
    if any(w in text for w in ['spotify', 'apple music', 'pandora', 'audible']): return "Music/Audio"
    if any(w in text for w in ['adobe', 'microsoft', 'slack', 'zoom', 'canva', 'chatgpt']): return "Software/SaaS"
    if any(w in text for w in ['aws', 'azure', 'digitalocean', 'godaddy', 'hostinger']): return "Tech Infrastructure"
    if any(w in text for w in ['gym', 'fitness', 'peloton', 'myfitnesspal']): return "Health"
    if any(w in text for w in ['food', 'hello fresh', 'uber eats', 'doordash']): return "Food"
    return "General Subscription"

@st.cache_data(show_spinner=False)
def scan_inbox(_service, days_back=90):
    query = f'(subject:(receipt OR invoice OR subscription OR renewal OR "trial ending" OR "auto-renew") OR from:(billing OR noreply OR support)) newer_than:{days_back}d -category:promotions'
    try:
        with st.spinner("🔍 Scanning inbox for vampires..."):
            results = _service.users().messages().list(userId='me', q=query, maxResults=60).execute()
        messages = results.get('messages', [])
        if not messages: return pd.DataFrame()
        
        found_subs = []
        progress_bar = st.progress(0)
        for idx, msg in enumerate(messages):
            try:
                msg_data = _service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = msg_data['payload']['headers']
                snippet = msg_data.get('snippet', '')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                date = next((h['value'] for h in headers if h['name'] == 'Date'), "")
                
                cost_match = re.search(r'[\$\£\€](\d+[,.]?\d*\.\d{2})', snippet)
                if not cost_match: cost_match = re.search(r'(\d+[,.]?\d*\.\d{2})\s*[\$\£\€]', snippet)
                cost = float(cost_match.group(1).replace(',', '')) if cost_match else 0.0
                clean_sender = re.sub(r'<[^>]+>', '', sender).replace('"', '').strip()
                
                if cost > 0 or any(x in subject.lower() for x in ['renew', 'subscription', 'bill']):
                    found_subs.append({"Sender": clean_sender, "Subject": subject, "Cost": cost, "Type": categorize_subscription(subject, clean_sender, snippet), "Date": date})
                time.sleep(0.05)
                progress_bar.progress((idx + 1) / len(messages))
            except HttpError: continue
        progress_bar.empty()
        return pd.DataFrame(found_subs)
    except HttpError as e:
        st.error(f"Gmail API Error: {e}")
        return pd.DataFrame()

# --- UI ---
st.markdown('<h1 class="main-header">🧛 Vampire Subscription Hunter</h1>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### 🔧 Configuration")
    scan_days = st.slider("Scan Period (days)", 30, 180, 90)
    st.info("🔒 **Privacy:** Data is processed locally. We never see your emails.")

col1, col2 = st.columns([2, 1])
with col1: st.markdown('<div class="warning-box"><h4>💡 Did You Know?</h4>The average person wastes <strong>$200+ per month</strong> on forgotten subscriptions.</div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="success-box"><h4>✅ Goal</h4>Find hidden costs and cancel them instantly.</div>', unsafe_allow_html=True)

st.markdown("---")
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b: scan_button = st.button("🚀 Connect Gmail & Start Scan", type="primary", use_container_width=True)

if scan_button:
    service = get_gmail_service()
    if service:
        df = scan_inbox(service, scan_days)
        if not df.empty:
            st.success(f"🎯 Found {len(df)} potential subscriptions!")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Monthly Waste", f"${df['Cost'].sum():.2f}")
            m2.metric("Avg. Item Cost", f"${df['Cost'].mean():.2f}")
            m3.metric("Active Subs", len(df))
            m4.metric("Unique Services", df['Sender'].nunique())
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.pie(df, values='Cost', names='Type', title='Cost by Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
            with c2: st.plotly_chart(px.bar(df.nlargest(10, 'Cost'), x='Cost', y='Sender', orientation='h', title='Most Expensive Vampires', color='Cost', color_continuous_scale='reds'), use_container_width=True)
            st.subheader("📋 Detailed Subscription List")
            st.dataframe(df[['Sender', 'Cost', 'Subject', 'Date', 'Type']], column_config={"Cost": st.column_config.NumberColumn(format="$%.2f")}, use_container_width=True)
            st.download_button("📥 Export to CSV", df.to_csv(index=False), f"vampire_scan_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            st.markdown("---")
            st.markdown(f"""<div style="background-color: #e3f2fd; padding: 2rem; border-radius: 10px; text-align: center; border: 1px solid #90caf9;"><h2 style="color: #0d47a1;">🛑 Stop Losing Money!</h2><p style="font-size: 1.1rem;">You are wasting <strong>${df['Cost'].sum():.2f} / month</strong>. Use these tools to fix it now:</p><div style="margin-top: 20px;"><a href="{LINK_ROCKET_MONEY}" target="_blank" class="cta-button cta-rocket">✂️ Cancel with Rocket Money</a><a href="{LINK_TRIM}" target="_blank" class="cta-button cta-trim">📉 Lower Bills with Trim</a><a href="{LINK_POCKETGUARD}" target="_blank" class="cta-button cta-guard">🛡️ Budget with PocketGuard</a></div></div>""", unsafe_allow_html=True)
        else: st.info("✅ No subscriptions found! Your inbox is clean.")
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>⚠️ Estimates based on email subject lines. Verify with your bank.</div>", unsafe_allow_html=True)
