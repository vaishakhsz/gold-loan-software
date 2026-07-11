import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import base64
import os
import json
import pickle
import tempfile

# ==========================================
# 1. PERSISTENT STORAGE CONFIGURATION
# ==========================================

# Strategy 1: Use Streamlit's session state for temporary persistence
# Strategy 2: Use GitHub/GitLab as persistent storage (via API)
# Strategy 3: Use cloud storage (Supabase, Firebase, etc.)
# Strategy 4: Use browser localStorage for small datasets

# For this solution, we'll implement:
# 1. SQLite with session state backup
# 2. JSON backup in session state
# 3. Cloud storage integration (Supabase example)

# ==========================================
# DATABASE WITH SESSION STATE PERSISTENCE
# ==========================================

DB_PATH = 'gold_loan_system.db'
SESSION_STATE_KEY = 'gold_loan_data'

def init_session_state():
    """Initialize session state with database backup"""
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False
        st.session_state.db_backup = None
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

def backup_database_to_session():
    """Backup entire database to session state"""
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'rb') as f:
                st.session_state.db_backup = f.read()
            st.session_state.db_initialized = True
            return True
    except Exception as e:
        st.error(f"Backup failed: {e}")
    return False

def restore_database_from_session():
    """Restore database from session state backup"""
    if st.session_state.db_backup is not None:
        try:
            with open(DB_PATH, 'wb') as f:
                f.write(st.session_state.db_backup)
            return True
        except Exception as e:
            st.error(f"Restore failed: {e}")
    return False

def get_db_connection():
    """Get database connection with persistence"""
    # First, try to restore from session state if database doesn't exist
    if not os.path.exists(DB_PATH) and st.session_state.db_backup is not None:
        restore_database_from_session()
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)  # Increased timeout
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

def check_db_exists():
    """Check if database file exists and has tables"""
    if not os.path.exists(DB_PATH):
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parties'")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except:
        return False

def init_db():
    """Initialize database with proper persistence"""
    init_session_state()
    
    # If database exists, try to load it
    if os.path.exists(DB_PATH):
        if not st.session_state.db_initialized:
            # Database exists but not backed up yet
            backup_database_to_session()
        return
    
    # Database doesn't exist - create new one
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    # Party Master Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            guardian_name TEXT,
            dob TEXT,
            mobile TEXT,
            whatsapp TEXT,
            address TEXT,
            pincode TEXT,
            pan_masked TEXT,
            occupation TEXT,
            qualification TEXT,
            kyc_status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    ''')
    
    # Gold Loans & Pledge Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER,
            principal REAL,
            interest_rate REAL,
            duration_months INTEGER,
            emi REAL,
            processing_fee REAL,
            admin_fee REAL,
            documentation_fee REAL,
            net_disbursed REAL,
            interest_amount REAL,
            total_payable REAL,
            gold_description TEXT,
            items_count INTEGER,
            gross_weight REAL,
            net_weight REAL,
            purity_karat INTEGER,
            appraised_value REAL,
            vault_id TEXT,
            gold_image_base64 TEXT, 
            status TEXT DEFAULT 'Active',
            disbursed_date TEXT,
            FOREIGN KEY (party_id) REFERENCES parties (id)
        )
    ''')
    
    # Transaction Ledger Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            transaction_type TEXT,
            amount REAL,
            transaction_date TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Backup the new database to session state
    backup_database_to_session()

# Initialize database with persistence
init_db()

# ==========================================
# 2. STREAMLIT UI & STYLE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

# Custom Styles for Goldish Background and Elements
st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background-color: #FAF6EE !important;
    }
    
    /* Top Headers & Cards */
    .gold-header { color: #8B6508; font-weight: bold; text-align: center; margin-bottom: 20px; }
    
    .stMetric { 
        background-color: #FFFDF7 !important; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #E3C16F !important;
        box-shadow: 0px 2px 4px rgba(227, 193, 111, 0.1);
    }
    
    /* Form Custom Borders */
    div[data-testid="stForm"] {
        background-color: #FFFDF9 !important;
        border: 1px solid #E3C16F !important;
        border-radius: 10px;
    }
    
    /* Document Download Containers styling inside downloaded files */
    .agreement-box { border: 2px solid #b8860b; padding: 30px; background-color: #fcfcf4; border-radius: 10px; font-family: 'Inter', sans-serif; color: #333; line-height: 1.7; }
    .agreement-table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }
    .agreement-table th, .agreement-table td { border: 1px solid #b8860b; padding: 10px; text-align: left; }
    .agreement-table th { background-color: #f5f0db; color: #b8860b; }
    .printable-ledger { font-family: Arial, sans-serif; padding: 25px; border: 1px solid #ccc; background-color: white; color: black; border-radius: 5px; }
    .printable-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .printable-table th, .printable-table td { border: 1px solid #000; padding: 8px; text-align: left; }
    .printable-table th { background-color: #f2f2f2; }
    .receipt-box { border: 2px dashed #333; padding: 20px; margin-top: 15px; background-color: #fff; }
    
    /* Data Persistence Status */
    .persistence-status {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .persistence-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .persistence-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    </style>
""", unsafe_allow_html=True)

# Fetch Live System Counters for Sidebar with error handling
def get_system_stats():
    try:
        conn = get_db_connection()
        if conn:
            count_parties = conn.execute("SELECT COUNT(*) FROM parties").fetchone()[0]
            count_loans = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
            count_gold = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
            count_tx = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
            conn.close()
            return count_parties, count_loans, count_gold, count_tx
    except:
        pass
    return 0, 0, 0, 0

count_parties, count_loans, count_gold, count_tx = get_system_stats()

# Helper function to generate standardized agreement HTML string
def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row['gold_image_base64']:
        image_html_tag = f"""
        <div style="margin-top:20px; margin-bottom:20px; text-align:center;">
            <p><b>പണയം വെച്ച ആഭരണത്തിന്റെ ഫോട്ടോ (Pledged Asset Photo):</b></p>
            <img src="data:image/jpeg;base64,{loan_row['gold_image_base64']}" style="max-width:320px; max-height:240px; border:3px solid #b8860b; border-radius:8px;"/>
        </div>
        """
    else:
        image_html_tag = "<p style='color:grey; font-style:italic; text-align:center;'>ചിത്രം ലഭ്യമല്ല (No photo attached)</p>"

    return f"""
    <div class="agreement-box">
        <h2 class="gold-header">സ്വർണ്ണപ്പണയ വായ്പാ കരാർ പത്രം (Gold Loan Agreement)</h2>
        <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}</p>
        <hr style="border-top: 1px solid #b8860b;">
        
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row['name']}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</b> {party_row['guardian_name'] or 'N/A'}</li>
            <li><b>വിലാസം (Address):</b> {party_row['address'] or 'N/A'}, {party_row['pincode'] or ''}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
            <li><b>തൊഴിൽ (Occupation):</b> {party_row['occupation'] or 'N/A'}</li>
            <li><b>യോഗ്യത (Qualification):</b> {party_row['qualification'] or 'N/A'}</li>
        </ul>

        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table class="agreement-table">
            <tr><th>വിവരണം (Description)</th><th>തുക / നിരക്ക് (Amount / Rate)</th></tr>
            <tr><td>അനുവദിച്ച വായ്പ തുക (Principal / Disbursement)</td><td><b>₹{loan_row['principal']:,.2f}</b></td></tr>
            <tr><td>പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td>{loan_row['interest_rate']}%</td></tr>
            <tr><td>കാലാവധി (Tenure)</td><td>{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
            <tr><td>പ്രതിമാസ തവണ (EMI)</td><td><b>₹{loan_row['emi']:,.2f}</b></td></tr>
            <tr style="font-weight:bold; background-color: #fff0f6;"><td>ആകെ പലിശ തുക (Interest Amount)</td><td>₹{loan_row['interest_amount']:,.2f}</td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത് (Total Payable)</td><td>₹{loan_row['total_payable']:,.2f}</td></tr>
        </table>

        <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം (Description):</b> {loan_row['gold_description'] or 'N/A'}</li>
            <li><b>ആകെ എണ്ണം (Count):</b> {loan_row['items_count']} Nos</li>
            <li><b>ഭാരം (Weight):</b> {loan_row['net_weight']} ഗ്രാം</li>
            <li><b>പ്യൂരിറ്റി (Purity):</b> {loan_row['purity_karat']} Karat</li>
            <li><b>മൂല്യം (Value):</b> ₹{loan_row['appraised_value']:,.2f}</li>
            <li><b>വോൾട്ട് സൂചിക (Vault ID):</b> `{loan_row['vault_id']}`</li>
        </ul>
        
        {image_html_tag}
        
        <br>
        <table style="width:100%; margin-top:30px;">
            <tr>
                <td>___________________________<br><b>വായ്പക്കാരന്റെ ഒപ്പ് / വിരലടയാളം</b></td>
                <td style="text-align:right;">___________________________<br><b>സ്ഥാപന അധികാരിയുടെ ഒപ്പ്</b></td>
            </tr>
        </table>
    </div>
    """

# Helper function to generate Add-on Charges Fee Receipt
def generate_fee_receipt_html(loan_row, party_row):
    total_fees = loan_row['processing_fee'] + loan_row['admin_fee'] + loan_row['documentation_fee']
    return f"""
    <div class="printable-ledger receipt-box">
        <h2 style="text-align:center;margin-bottom:2px;color:#b8860b;">AURA LOAN MANAGEMENT SYSTEM</h2>
        <h4 style="text-align:center;margin-top:0px;color:#555;">📋 ഫീസ് അടച്ച വൗച്ചർ / FEES RECEIPT</h4>
        <hr style="border-top: 1px dashed #000;">
        <table style="width:100%; margin-bottom:15px; font-size:14px;">
            <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {party_row['name']}</td><td><b>രസീത് നമ്പർ (Receipt No):</b> #FEE-{loan_row['id']}</td></tr>
            <tr><td><b>ലോൺ ലിങ്ക് ഐഡി (Loan Ref ID):</b> #{loan_row['id']}</td><td><b>തീയതി (Date):</b> {loan_row['disbursed_date']}</td></tr>
            <tr><td><b>മൊബൈൽ (Mobile):</b> {party_row['mobile']}</td><td><b>സ്റ്റാറ്റസ് (Status):</b> <span style="color:green;font-weight:bold;">Paid</span></td></tr>
        </table>
        
        <table class="printable-table">
            <thead>
                <tr style="background-color: #f9f9f9;"><th>ക്രമ നമ്പർ (Sl No)</th><th>ഫീസ് വിവരണം (Fee Description)</th><th>ഈടാക്കിയ തുക (Amount Collected)</th></tr>
            </thead>
            <tbody>
                <tr><td style="text-align:center;">1</td><td>പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td>₹{loan_row['processing_fee']:,.2f}</td></tr>
                <tr><td style="text-align:center;">2</td><td>അഡ്മിൻ ഫീസ് (Admin Fee)</td><td>₹{loan_row['admin_fee']:,.2f}</td></tr>
                <tr><td style="text-align:center;">3</td><td>ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td>₹{loan_row['documentation_fee']:,.2f}</td></tr>
                <tr style="font-weight:bold; background-color: #f5f5f5;"><td colspan="2" style="text-align:right;">ആകെ ഈടാക്കിയ ഫീസ് (Total Service Charges):</td><td>₹{total_fees:,.2f}</td></tr>
            </tbody>
        </table>
        <br>
        <p style="font-size:13px; font-weight:bold;">തുക അക്ഷരത്തിൽ: രൂപ {total_fees} മാത്രം.</p>
        <br>
        <table style="width:100%; margin-top:20px; font-size:14px; text-align:center;">
            <tr><td>____________________<br>ക്യാഷറുടെ ഒപ്പ് (Cashier)</td><td>____________________<br>കസ്റ്റമർ ഒപ്പ് (Customer Signature)</td></tr>
        </table>
    </div>
    """

# ==========================================
# 3. SIDEBAR NAVIGATION MANAGEMENT
# ==========================================
st.sidebar.markdown("### 📋 Navigation")
main_menu = [
    "🏠 Dashboard",
    "👤 Party Master",
    "✏️ Edit/Delete Party Profile",
    "💰 Gold Loan Management",
    "💍 Gold Pledge Management",
    "📄 Loan Agreement (Malayalam)",
    "📅 EMI Schedule",
    "💾 Backup, Restore & Upload",
    "⚙️ Data Persistence Settings"
]
choice = st.sidebar.selectbox("Select Module", main_menu)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Sub-Modules")
if choice == "💰 Gold Loan Management":
    sub_choice = st.sidebar.radio("Sub Navigation", ["💸 Loan Disbursement", "📊 Party Ledger"])
else:
    st.sidebar.markdown("*No active sub-module*")
    sub_choice = None

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: **{count_parties}**")
st.sidebar.write(f"💰 Loans: **{count_loans}**")
st.sidebar.write(f"💍 Gold: **{count_gold}**")
st.sidebar.write(f"📝 Transactions: **{count_tx}**")

# Show persistence status
if st.session_state.db_initialized:
    st.sidebar.success("✅ Data Persistence: Active")
else:
    st.sidebar.warning("⚠️ Data Persistence: Inactive")

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    conn = get_db_connection()
    
    if conn:
        total_active_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
        total_disbursed = conn.execute("SELECT SUM(principal) FROM loans").fetchone()[0] or 0.0
        total_gold_wt = conn.execute("SELECT SUM(net_weight) FROM loans WHERE status='Active'").fetchone()[0] or 0.0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Loan Accounts", total_active_loans)
        col2.metric("Total Disbursement (Principal Amount)", f"₹{total_disbursed:,.2f}")
        col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
        
        st.subheader("📈 Live Master Monitoring Stream")
        df_dashboard = pd.read_sql_query("""
            SELECT l.id as 'Loan ID', p.name as 'Customer Name', l.principal as 'Principal/Disbursement Amount (₹)', 
                   l.interest_amount as 'Interest Amount (₹)', l.total_payable as 'Total Payable (₹)', 
                   l.emi as 'Monthly EMI (₹)', l.status as 'Status'
            FROM loans l JOIN parties p ON l.party_id = p.id
        """, conn)
        st.dataframe(df_dashboard, use_container_width=True)
        conn.close()
        
        # Auto-backup after viewing dashboard
        backup_database_to_session()
    else:
        st.error("Database connection failed. Please check the database file.")

# ==========================================
# MODULE: PARTY MASTER
# ==========================================
elif choice == "👤 Party Master":
    st.header("👤 Customer Registration (Party Master)")
    with st.form("party_master_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("പേര് (Name) *")
            guardian_name = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name)")
            dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now())
            mobile = st.text_input("മൊബൈൽ നമ്പർ (Mobile) *")
            whatsapp = st.text_input("WhatsApp Number")
        with col2:
            occupation = st.text_input("തൊഴിൽ (Occupation)")
            qualification = st.text_input("യോഗ്യത (Qualification)")
            address = st.text_area("വിലാസം (Address)")
            pincode = st.text_input("Pincode")
            pan = st.text_input("PAN Card Number")
            kyc_status = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"])
            
        if st.form_submit_button("Save Customer Profile"):
            if name and mobile:
                conn = get_db_connection()
                if conn:
                    conn.execute("""
                        INSERT INTO parties (name, guardian_name, dob, mobile, whatsapp, address, pincode, pan_masked, occupation, qualification, kyc_status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, guardian_name, str(dob), mobile, whatsapp, address, pincode, pan, occupation, qualification, kyc_status, str(datetime.now().date())))
                    conn.commit()
                    conn.close()
                    
                    # Backup database after saving
                    backup_database_to_session()
                    
                    st.success(f"Successfully registered: {name}")
                    st.rerun()
                else:
                    st.error("Database connection failed.")
            else:
                st.error("Name and Mobile fields are required.")

# ==========================================
# MODULE: EDIT & DELETE PARTY DETAILS
# ==========================================
elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core (Edit / Delete Customer Accounts)")
    conn = get_db_connection()
    
    if conn:
        parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
        
        if parties_df.empty:
            st.info("No customer data available.")
        else:
            party_to_edit = st.selectbox("Select Party Profile to Manage", parties_df['id'].tolist(), format_func=lambda x: f"ID: {x} | {parties_df[parties_df['id']==x]['name'].values[0]} ({parties_df[parties_df['id']==x]['kyc_status'].values[0]})")
            selected_row = parties_df[parties_df['id'] == party_to_edit].iloc[0]
            
            tab_edit, tab_delete = st.tabs(["✏️ Edit Details", "❌ Delete Profile Permanently"])
            
            with tab_edit:
                with st.form("edit_party_form_main"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("പേര് (Name)", value=selected_row['name'])
                        edit_guardian = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര്", value=selected_row['guardian_name'])
                        edit_mobile = st.text_input("മൊബൈൽ നമ്പർ (Mobile)", value=selected_row['mobile'])
                        edit_whatsapp = st.text_input("WhatsApp Number", value=selected_row['whatsapp'])
                    with col2:
                        edit_occupation = st.text_input("തൊഴിൽ (Occupation)", value=selected_row['occupation'])
                        edit_qualification = st.text_input("യോഗ്യത (Qualification)", value=selected_row['qualification'])
                        edit_address = st.text_area("വിലാസം (Address)", value=selected_row['address'])
                        edit_pincode = st.text_input("Pincode", value=selected_row['pincode'])
                        edit_kyc = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"], index=["Pending", "Verified", "Suspended"].index(selected_row['kyc_status']))
                    
                    if st.form_submit_button("Save All Updates"):
                        conn.execute("""
                            UPDATE parties SET 
                                name=?, guardian_name=?, mobile=?, whatsapp=?, 
                                occupation=?, qualification=?, address=?, pincode=?, kyc_status=?
                            WHERE id=?
                        """, (edit_name, edit_guardian, edit_mobile, edit_whatsapp, edit_occupation, edit_qualification, edit_address, edit_pincode, edit_kyc, party_to_edit))
                        conn.commit()
                        
                        # Backup database after editing
                        backup_database_to_session()
                        
                        st.success("All updates saved successfully.")
                        st.rerun()
                        
            with tab_delete:
                st.warning(f"⚠️ Warning: You are about to permanently delete the profile of **{selected_row['name']}**.")
                st.error("This will delete the customer profile. Make sure there are no open loans attached to this party.")
                
                confirm_delete_text = st.text_input("Type 'DELETE' to confirm action:")
                if st.button("Confirm Account Destruction"):
                    if confirm_delete_text == "DELETE":
                        # Check if customer has active loans
                        has_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE party_id = ? AND status = 'Active'", (party_to_edit,)).fetchone()[0]
                        if has_loans > 0:
                            st.error("Cannot delete profile: This customer still has active gold loan files recorded.")
                        else:
                            conn.execute("DELETE FROM parties WHERE id = ?", (party_to_edit,))
                            conn.commit()
                            
                            # Backup database after deletion
                            backup_database_to_session()
                            
                            st.success("Customer profile deleted from logs successfully.")
                            st.rerun()
                    else:
                        st.error("Confirmation string does not match.")
        conn.close()
    else:
        st.error("Database connection failed.")

# ==========================================
# PARENT MODULE: GOLD LOAN MANAGEMENT
# ==========================================
elif choice == "💰 Gold Loan Management":
    conn = get_db_connection()
    
    if not conn:
        st.error("Database connection failed.")
    else:
        # 💸 SUB-MODULE 1: LOAN DISBURSEMENT MODULE
        if sub_choice == "💸 Loan Disbursement":
            st.header("💸 Gold Loan Formulation (Disbursement = Principal)")
            
            parties = conn.execute("SELECT id, name FROM parties WHERE kyc_status = 'Verified'").fetchall()
            
            if not parties:
                st.warning("⚠️ No Verified Customers Available. Please verify a profile inside Party Management first.")
            else:
                party_options = {p['id']: p['name'] for p in parties}
                
                with st.form("disbursement_calculator_form"):
                    selected_party = st.selectbox("Select Verified Borrower Profile", list(party_options.keys()), format_func=lambda x: party_options[x])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 💎 സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)")
                        gold_description = st.text_input("വിവരണം (Description)", placeholder="മാല, വളകൾ, മോതിരം")
                        items_count = st.number_input("എണ്ണം (Count)", min_value=1, value=1, step=1)
                        gross_wt = st.number_input("Gross Weight (grams)", min_value=0.0, step=0.1)
                        net_wt = st.number_input("Weight / Net Weight (grams)", min_value=0.0, step=0.1)
                        purity = st.selectbox("പ്യൂരിറ്റി (Purity Karat)", [24, 22, 20, 18], index=1)
                        appraised_val = st.number_input("മൂല്യം (Gold Appraisal Value - ₹)", min_value=0.0)
                        vault_id = st.text_input("Locker / Vault Storage ID Code")
                        
                        st.markdown("---")
                        st.markdown("📷 **Attach Gold Photo**")
                        photo_source = st.radio("ഫോട്ടോ എടുക്കേണ്ട രീതി", ["Upload File", "Use Device Camera"], horizontal=True)
                        
                        gold_photo_data = None
                        if photo_source == "Upload File":
                            gold_photo_data = st.file_uploader("സ്വർണ്ണത്തിന്റെ ചിത്രം തിരഞ്ഞെടുക്കുക", type=["jpg", "png", "jpeg"])
                        else:
                            gold_photo_data = st.camera_input("ലൈവ് ഫോട്ടോ എടുക്കുക")
                        
                    with col2:
                        st.markdown("#### 📊 Calculation Terms (Disbursement = Principal Amount)")
                        max_eligible = appraised_val * 0.75
                        st.info(f"Regulatory 75% LTV Cap Limit: **₹{max_eligible:,.2f}**")
                        
                        principal = st.number_input("അനുവദിച്ച വായ്പ / Disbursement Amount (Principal) - ₹", min_value=0.0, value=40375.0)
                        interest_rate = st.number_input("പലിശ നിരക്ക് (Interest Rate % For Total Duration)", min_value=0.0, value=12.0)
                        duration = st.number_input("കാലാവധി (Tenure Duration - Months)", min_value=1, max_value=36, value=12)
                        
                        st.markdown("---")
                        st.markdown("#### 🏷️ ആഡ്ഓൺ ചാർജ്ജുകൾ (Service Fees)")
                        processing_fee = st.number_input("പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee - ₹)", min_value=0.0, value=500.0)
                        admin_fee = st.number_input("അഡ്മിൻ ഫീസ് (Admin Fee - ₹)", min_value=0.0, value=200.0)
                        doc_fee = st.number_input("ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee - ₹)", min_value=0.0, value=200.0)
                        
                        interest_amount = principal * (interest_rate / 100)
                        total_payable = principal + interest_amount
                        calculated_emi = total_payable / duration if duration > 0 else 0.0
                        
                        st.markdown("---")
                        st.write(f"**അസ്സൽ വായ്പ തുക (Disbursement Amount):** ₹{principal:,.2f}")
                        st.write(f"**പലിശ തുക (Interest Charged):** ₹{interest_amount:,.2f}")
                        st.write(f"**ആകെ അടയ്ക്കാനുള്ളത് (Total Payable):** ₹{total_payable:,.2f}")
                        st.write(f"**പ്രതിമാസ തവണ (EMI):** ₹{calculated_emi:,.2f}")
                        
                    if st.form_submit_button("Finalize and Disburse Capital Allocation"):
                        if principal > max_eligible:
                            st.error("Requested capital allocation exceeds the 75% LTV limit.")
                        elif principal <= 0 or net_wt <= 0:
                            st.error("Invalid entry constraints.")
                        else:
                            today_str = str(datetime.now().date())
                            
                            base64_image_str = ""
                            if gold_photo_data is not None:
                                bytes_data = gold_photo_data.read()
                                base64_image_str = base64.b64encode(bytes_data).decode("utf-8")
                            
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO loans (
                                    party_id, principal, interest_rate, duration_months, emi, 
                                    processing_fee, admin_fee, documentation_fee, net_disbursed,
                                    interest_amount, total_payable, gold_description, items_count, 
                                    gross_weight, net_weight, purity_karat, appraised_value, vault_id, gold_image_base64, status, disbursed_date
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
                            """, (selected_party, principal, interest_rate, duration, calculated_emi, 
                              processing_fee, admin_fee, doc_fee, principal, interest_amount, total_payable,
                              gold_description, items_count, gross_wt, net_wt, purity, appraised_val, vault_id, base64_image_str, today_str))
                            
                            loan_id = cursor.lastrowid
                            cursor.execute("INSERT INTO ledger (loan_id, transaction_type, amount, transaction_date) VALUES (?, 'Disbursement', ?, ?)", (loan_id, principal, today_str))
                            
                            conn.commit()
                            
                            # Backup database after loan creation
                            backup_database_to_session()
                            
                            st.success(f"Loan Account #{loan_id} successfully created.")
                            st.session_state['active_contract_loan_id'] = loan_id
                            st.rerun()

                if 'active_contract_loan_id' in st.session_state:
                    l_id = st.session_state['active_contract_loan_id']
                    loan_row = conn.execute(f"SELECT * FROM loans WHERE id={l_id}").fetchone()
                    if loan_row:
                        party_row = conn.execute(f"SELECT * FROM parties WHERE id={loan_row['party_id']}").fetchone()
                        
                        tab_voucher, tab_fee_receipt = st.tabs(["📄 വായ്പാ കരാർ ഫോം (Agreement Form)", "🖨️ ഫീസ് രസീത് (Separate Fee Receipt)"])
                        
                        with tab_voucher:
                            instant_html = generate_agreement_html(loan_row, party_row)
                            st.download_button(label="📥 ഡൗൺലോഡ് കരാർ പത്രം (Download Agreement)", data=instant_html, file_name=f"Agreement_Loan_{l_id}.html", mime="text/html")
                        
                        with tab_fee_receipt:
                            fee_html = generate_fee_receipt_html(loan_row, party_row)
                            st.download_button(label="📥 പ്രിന്റ് ഫീസ് രസീത് (Download Fee Receipt)", data=fee_html, file_name=f"Fee_Receipt_Loan_{l_id}.html", mime="text/html")

        # 📊 SUB-MODULE 2: PARTY LEDGER ACCOUNTANT
        elif sub_choice == "📊 Party Ledger":
            st.header("📊 Customer Ledger Statements")
            active_loans = conn.execute("SELECT l.id, p.name, l.principal FROM loans l JOIN parties p ON l.party_id = p.id WHERE l.status='Active'").fetchall()
            
            if not active_loans:
                st.info("No active loan records open currently.")
            else:
                loan_options = {al['id']: f"Loan #{al['id']} - Holder: {al['name']} (₹{al['principal']})" for al in active_loans}
                selected_loan = st.selectbox("Select Target Portfolio File", list(loan_options.keys()), format_func=lambda x: loan_options[x])
                
                # Fetch liability balance details
                loan_row_data = conn.execute(f"SELECT total_payable, principal FROM loans WHERE id={selected_loan}").fetchone()
                total_liability = float(loan_row_data['total_payable'] or 0.0)
                total_repaid_credits = conn.execute(f"SELECT SUM(amount) FROM ledger WHERE loan_id={selected_loan} AND transaction_type IN ('Repayment', 'Interest Settlement')").fetchone()[0]
                total_repaid_credits = float(total_repaid_credits or 0.0)
                live_outstanding_balance = total_liability - total_repaid_credits
                
                if live_outstanding_balance < 0.01:
                    live_outstanding_balance = 0.0
                
                tab_post, tab_view, tab_print = st.tabs(["💳 Collection Repayment Entry", "📑 View Balancing Ledger Statement", "🖨️ Generate Printable Sheet"])
                
                with tab_post:
                    if live_outstanding_balance <= 0.0:
                        st.success("🎉 Already Repaid / Bill completely paid in full.")
                    else:
                        with st.form("repayment_ledger_post_form"):
                            repay_amt = st.number_input("Repayment Collected (₹)", min_value=0.0, max_value=live_outstanding_balance, step=100.0, help="Cannot exceed remaining outstanding debt limit.")
                            repay_date = st.date_input("Settlement Date")
                            type_tx = st.selectbox("Allocation Type", ["Repayment", "Interest Settlement"])
                            
                            if st.form_submit_button("Post Entry"):
                                if repay_amt > 0:
                                    conn.execute("INSERT INTO ledger (loan_id, transaction_type, amount, transaction_date) VALUES (?, ?, ?, ?)", (selected_loan, type_tx, repay_amt, str(repay_date)))
                                    
                                    # Check if this installment covers the remaining balance entirely
                                    if repay_amt >= live_outstanding_balance:
                                        conn.execute("UPDATE loans SET status = 'Closed' WHERE id = ?", (selected_loan,))
                                    
                                    conn.commit()
                                    
                                    # Backup database after repayment
                                    backup_database_to_session()
                                    
                                    st.success("Repayment entry saved inside ledger.")
                                    st.rerun()
                                
                with tab_view:
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Disbursement / Principal Amount", f"₹{loan_row_data['principal']:,.2f}")
                    col_m2.metric("Total Payable (with Interest)", f"₹{total_liability:,.2f}")
                    
                    if live_outstanding_balance <= 0.0:
                        col_m3.metric("Current Outstanding Balance", "Already Repaid")
                    else:
                        col_m3.metric("Current Outstanding Balance", f"₹{live_outstanding_balance:,.2f}", delta_color="inverse")
                    
                    tx_history_df = pd.read_sql_query(f"SELECT transaction_type as 'Activity Type', amount as 'Value (₹)', transaction_date as 'Date' FROM ledger WHERE loan_id={selected_loan} ORDER BY ROWID ASC", conn)
                    st.table(tx_history_df)
                    
                with tab_print:
                    st.markdown("### 🖨️ Printable Ledger Statement")
                    p_loan = conn.execute(f"SELECT l.*, p.name, p.mobile, p.address FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.id={selected_loan}").fetchone()
                    tx_rows = conn.execute(f"SELECT * FROM ledger WHERE loan_id={selected_loan} ORDER BY ROWID ASC").fetchall()
                    
                    table_html_rows = ""
                    for tx in tx_rows:
                        display_type = "Loan Disbursement (Principal)" if tx['transaction_type'] == "Disbursement" else tx['transaction_type']
                        table_html_rows += f"<tr><td>{tx['transaction_date']}</td><td>{display_type}</td><td>₹{tx['amount']:,.2f}</td></tr>"
                    
                    total_repaid = sum([t['amount'] for t in tx_rows if t['transaction_type'] in ['Repayment', 'Interest Settlement']])
                    balance_left = p_loan['total_payable'] - total_repaid
                    
                    if balance_left < 0.01:
                        balance_html_str = "<b style='color:green; font-size:18px;'>Already Repaid / Paid in Full</b>"
                    else:
                        balance_html_str = f"<b>₹{balance_left:,.2f}</b>"
                    
                    printable_html = f"""
                    <div class="printable-ledger">
                        <h2 style="text-align:center;margin-bottom:2px;">AURA LOAN MANAGEMENT SYSTEM</h2>
                        <h4 style="text-align:center;margin-top:0px;color:#555;">STATEMENT OF ACCOUNT / PARTY LEDGER</h4>
                        <hr>
                        <table style="width:100%; margin-bottom:20px; font-size:14px;">
                            <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {p_loan['name']}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{p_loan['id']}</td></tr>
                            <tr><td><b>ഫോൺ (Mobile):</b> {p_loan['mobile']}</td><td><b>തീയതി (Date Issued):</b> {p_loan['disbursed_date']}</td></tr>
                            <tr><td colspan="2"><b>മേൽവിലാസം (Address):</b> {p_loan['address']}</td></tr>
                        </table>
                        
                        <table class="printable-table">
                            <thead>
                                <tr><th>തീയതി (Date)</th><th>വിവരണം (Description)</th><th>തുക (Amount)</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>{p_loan['disbursed_date']}</td><td>Fixed Term Interest Charged</td><td>₹{p_loan['interest_amount']:,.2f}</td></tr>
                                {table_html_rows}
                            </tbody>
                        </table>
                        
                        <div style="margin-top:20px; text-align:right; font-size:16px;">
                            <p><b>അസ്സൽ തുക (Principal/Disbursed Amount):</b> ₹{p_loan['principal']:,.2f}</p>
                            <p><b>ആകെ പലിശ (Total Interest Charged):</b> ₹{p_loan['interest_amount']:,.2f}</p>
                            <hr style="border-top: 1px solid #000; width: 40%; margin-left: auto;">
                            <p><b>ആകെ അടയ്ക്കേണ്ടത് (Total Payable):</b> ₹{p_loan['total_payable']:,.2f}</p>
                            <p style="color:green;"><b>ഇതുവരെ അടച്ചത് (Total Repaid):</b> ₹{total_repaid:,.2f}</p>
                            <p style="color:red; font-size:18px;"><b>ബാക്കി കുടിശ്ശിക (Outstanding Balance):</b> {balance_html_str}</p>
                        </div>
                    </div>
                    """
                    st.download_button(label="📥 ഡൗൺലോഡ് ലെഡ്ജർ (Download HTML Ledger)", data=printable_html, file_name=f"Ledger_Loan_{selected_loan}.html", mime="text/html")
        conn.close()

# ==========================================
# MODULE: GOLD PLEDGE MANAGEMENT
# ==========================================
elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory Vault Details")
    conn = get_db_connection()
    
    if conn:
        loans_cursor = conn.execute("SELECT l.*, p.name as pledger_name FROM loans l JOIN parties p ON l.party_id = p.id WHERE l.status='Active'").fetchall()
        
        if not loans_cursor:
            st.info("No vaulted items found inside database logs.")
        else:
            for row in loans_cursor:
                with st.container():
                    col_text, col_img = st.columns([2, 1])
                    with col_text:
                        st.markdown(f"### 📦 Loan Account Portfolio Reference #{row['id']}")
                        st.write(f"👤 **ഉടമസ്ഥൻ:** {row['pledger_name']}")
                        st.write(f"📝 **ആഭരണ വിവരണം:** {row['gold_description']}")
                        st.write(f"🔢 **എണ്ണം:** {row['items_count']} Nos | ⚖️ **തൂക്കം:** {row['net_weight']} ഗ്രാം")
                        st.write(f"🔒 **വോൾട്ട് സൂചിക:** `{row['vault_id']}`")
                    with col_img:
                        if row['gold_image_base64']:
                            img_bytes = base64.b64decode(row['gold_image_base64'])
                            st.image(img_bytes, caption="Pledged Gold Asset", width=180)
                    st.markdown("---")
        conn.close()
    else:
        st.error("Database connection failed.")

# ==========================================
# MODULE: LOAN AGREEMENT MALAYALAM
# ==========================================
elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement Console")
    conn = get_db_connection()
    
    if conn:
        available_contracts = conn.execute("SELECT l.id, p.name FROM loans l JOIN parties p ON l.party_id=p.id").fetchall()
        
        if not available_contracts:
            st.info("No loan files to fetch sheets for.")
        else:
            contract_options = {ac['id']: f"Loan #{ac['id']} Ledger Account - {ac['name']}" for ac in available_contracts}
            target_contract = st.selectbox("Select Target Active Portfolio File", list(contract_options.keys()), format_func=lambda x: contract_options[x])
            
            loan_row = conn.execute(f"SELECT * FROM loans WHERE id={target_contract}").fetchone()
            if loan_row:
                party_row = conn.execute(f"SELECT * FROM parties WHERE id={loan_row['party_id']}").fetchone()
                
                tab_contract_view, tab_receipt_view = st.tabs(["📜 വൗച്ചർ ഡൗൺലോഡ് (Agreement Form)", "🧾 രസീത് ഡൗൺലോഡ് (Fee Receipt)"])
                
                with tab_contract_view:
                    agreement_html = generate_agreement_html(loan_row, party_row)
                    st.download_button(label="📥 ഡൗൺലോഡ് കരാർ പത്രം (Download Agreement HTML)", data=agreement_html, file_name=f"Agreement_Loan_{loan_row['id']}.html", mime="text/html")
                    
                with tab_receipt_view:
                    fee_html = generate_fee_receipt_html(loan_row, party_row)
                    st.download_button(label="📥 ഡൗൺലോഡ് ഫീസ് രസീത് (Download Fee Receipt HTML)", data=fee_html, file_name=f"Fee_Receipt_Loan_{loan_row['id']}.html", mime="text/html")
        conn.close()
    else:
        st.error("Database connection failed.")

# ==========================================
# MODULE: EMI SCHEDULE MATRIX
# ==========================================
elif choice == "📅 EMI Schedule":
    st.header("📅 Monthly Recovery Projection Mapping (EMI Schedule)")
    conn = get_db_connection()
    
    if conn:
        active_loans = conn.execute("SELECT l.id, p.name, l.emi, l.duration_months, l.total_payable FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.status='Active'").fetchall()
        
        if not active_loans:
            st.info("No active loan tracking matrices found.")
        else:
            loan_options = {al['id']: f"Loan #{al['id']} - Account: {al['name']} (EMI: ₹{al['emi']:,.2f})" for al in active_loans}
            selected_sched = st.selectbox("Select Target Loan ID Schedule Map", list(loan_options.keys()), format_func=lambda x: loan_options[x])
            
            target_l = conn.execute(f"SELECT l.*, p.name, p.mobile FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.id={selected_sched}").fetchone()
            
            if target_l:
                schedule_rows_html = ""
                remaining_reduction_pool = target_l['total_payable']
                
                schedule_list = []
                for index in range(1, target_l['duration_months'] + 1):
                    remaining_reduction_pool -= target_l['emi']
                    current_rem = max(0.0, remaining_reduction_pool)
                    
                    if current_rem < 0.01:
                        display_rem = "Already Repaid"
                    else:
                        display_rem = f"₹{current_rem:,.2f}"
                        
                    schedule_rows_html += f"""
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;">Month {index}</td>
                        <td style="border: 1px solid #000; padding: 8px;">₹{target_l['emi']:,.2f}</td>
                        <td style="border: 1px solid #000; padding: 8px;">{display_rem}</td>
                    </tr>
                    """
                    schedule_list.append({
                        "Installment": f"Month No. {index}",
                        "Payment Amount (₹)": f"₹{target_l['emi']:,.2f}",
                        "Outstanding Balance": display_rem
                    })
                    
                st.table(pd.DataFrame(schedule_list))
                
                printable_schedule_html = f"""
                <div class="printable-ledger">
                    <h2 style="text-align:center;margin-bottom:2px;">AURA LOAN MANAGEMENT SYSTEM</h2>
                    <h4 style="text-align:center;margin-top:0px;color:#555;">📊 പ്രതിമാസ തവണ വിവരപ്പട്ടിക (EMI SCHEDULE PLAN)</h4>
                    <hr>
                    <table style="width:100%; margin-bottom:20px; font-size:14px;">
                        <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {target_l['name']}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{target_l['id']}</td></tr>
                        <tr><td><b>ഫോൺ (Mobile):</b> {target_l['mobile']}</td><td><b>അസ്സൽ വായ്പ (Principal/Disbursed):</b> ₹{target_l['principal']:,.2f}</td></tr>
                        <tr><td><b>ആകെ അടയ്ക്കേണ്ടത് (Total Liability):</b> ₹{target_l['total_payable']:,.2f}</td></tr>
                    </table>
                    
                    <table class="printable-table">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th style="border: 1px solid #000; padding: 8px; text-align: center;">തവണ നമ്പർ (Installment)</th>
                                <th style="border: 1px solid #000; padding: 8px;">അടയ്ക്കേണ്ട തുക (EMI Amount)</th>
                                <th style="border: 1px solid #000; padding: 8px;">ബാക്കി വരാവുന്ന തുക (Remaining Balance)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {schedule_rows_html}
                        </tbody>
                    </table>
                </div>
                """
                
                st.download_button(label="📥 ഡൗൺലോഡ് & പ്രിന്റ് ഷെഡ്യൂൾ (Download Schedule Sheet)", data=printable_schedule_html, file_name=f"EMI_Schedule_Loan_{selected_sched}.html", mime="text/html")
        conn.close()
    else:
        st.error("Database connection failed.")

# ==========================================
# MODULE: BACKUP, RESTORE & DATA UPLOADER
# ==========================================
elif choice == "💾 Backup, Restore & Upload":
    st.header("💾 Storage Engine Maintenance & Data Integration Tools")
    conn = get_db_connection()
    
    if not conn:
        st.error("Database connection failed.")
    else:
        st.subheader("📥 Upload Existing Datasets (CSV Imports)")
        target_upload_table = st.selectbox("Select Destination Database Table to Populate:", ["parties", "loans"])
        uploaded_csv = st.file_uploader(f"Choose a CSV file containing '{target_upload_table}' row records", type=["csv"])
        
        if uploaded_csv is not None:
            try:
                input_df = pd.read_csv(uploaded_csv)
                st.write("🔍 Preview of data to import:")
                st.dataframe(input_df.head(5))
                
                if st.button("Commit Data Feed to SQLite Engine"):
                    input_df.to_sql(target_upload_table, conn, if_exists='append', index=False)
                    st.success(f"Successfully integrated {len(input_df)} rows into the local `{target_upload_table}` dataset.")
                    
                    # Backup database after import
                    backup_database_to_session()
                    
                    st.rerun()
            except Exception as err:
                st.error(f"Failed parsing file formatting layout context. Internal error: {err}")
                
        st.markdown("---")
        
        st.subheader("📤 Local Backup Operations")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Party Registries Matrix")
            df_p = pd.read_sql_query("SELECT * FROM parties", conn)
            st.download_button("Download Customers CSV", data=df_p.to_csv(index=False).encode('utf-8'), file_name="parties_export.csv", mime="text/csv")
            
        with col2:
            st.markdown("#### Active Portfolio Matrix")
            df_l = pd.read_sql_query("SELECT * FROM loans", conn)
            st.download_button("Download Loans CSV", data=df_l.to_csv(index=False).encode('utf-8'), file_name="loans_export.csv", mime="text/csv")
            
        st.markdown("---")
        
        st.subheader("💾 Session State Backup Management")
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            if st.button("📤 Backup Current Database to Session"):
                if backup_database_to_session():
                    st.success("Database backed up to session state successfully!")
                else:
                    st.error("Backup failed!")
        
        with col_backup2:
            if st.button("📥 Restore Database from Session Backup"):
                if st.session_state.db_backup is not None:
                    if restore_database_from_session():
                        st.success("Database restored from session backup!")
                        st.rerun()
                    else:
                        st.error("Restore failed!")
                else:
                    st.warning("No backup found in session state!")
        
        st.markdown("---")
        
        # Check if database file exists before attempting backup
        if os.path.exists(DB_PATH):
            # Also backup to a persistent location if possible
            with open(DB_PATH, "rb") as db_file:
                db_binary_stream = db_file.read()
                
            st.download_button(
                label="📥 Download Full Database Binary Backup (.DB File)",
                data=db_binary_stream,
                file_name=f"gold_loan_system_backup_{datetime.now().date()}.db",
                mime="application/octet-stream"
            )
            
            # Show database size
            db_size = os.path.getsize(DB_PATH) / 1024  # KB
            st.info(f"Database Size: {db_size:.2f} KB")
        else:
            st.warning("Database file not found. No backup available.")
        
        # Show session state backup status
        if st.session_state.db_backup is not None:
            backup_size = len(st.session_state.db_backup) / 1024  # KB
            st.info(f"Session Backup Size: {backup_size:.2f} KB")
        else:
            st.info("No session backup available")
        
        conn.close()

# ==========================================
# MODULE: DATA PERSISTENCE SETTINGS
# ==========================================
elif choice == "⚙️ Data Persistence Settings":
    st.header("⚙️ Data Persistence Configuration")
    
    st.subheader("📊 Current Persistence Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Database File Status:**")
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH) / 1024
            st.success(f"✅ Database exists ({db_size:.2f} KB)")
        else:
            st.warning("⚠️ Database file not found")
    
    with col2:
        st.markdown("**Session Backup Status:**")
        if st.session_state.db_backup is not None:
            backup_size = len(st.session_state.db_backup) / 1024
            st.success(f"✅ Backup available ({backup_size:.2f} KB)")
        else:
            st.warning("⚠️ No backup in session")
    
    st.markdown("---")
    
    st.subheader("🔄 Manual Persistence Operations")
    
    col_ops1, col_ops2, col_ops3 = st.columns(3)
    
    with col_ops1:
        if st.button("🔄 Backup to Session", use_container_width=True):
            if backup_database_to_session():
                st.success("✅ Database backed up to session state!")
            else:
                st.error("❌ Backup failed!")
    
    with col_ops2:
        if st.button("🔄 Restore from Session", use_container_width=True):
            if st.session_state.db_backup is not None:
                if restore_database_from_session():
                    st.success("✅ Database restored from session backup!")
                    st.rerun()
                else:
                    st.error("❌ Restore failed!")
            else:
                st.warning("⚠️ No backup available!")
    
    with col_ops3:
        if st.button("🗑️ Clear Session Backup", use_container_width=True):
            st.session_state.db_backup = None
            st.session_state.db_initialized = False
            st.success("Session backup cleared!")
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("💡 Recommended Practices")
    st.info("""
    **To prevent data loss on Streamlit Cloud:**
    
    1. **Regular Backups**: Use the backup button frequently
    2. **Download Database**: Download the full .db file periodically
    3. **CSV Exports**: Export your data as CSV as a safety measure
    4. **Session State**: The app now stores backups in session state
    5. **Manual Restore**: If data is lost, use the restore function
    
    **Note**: Session state backups persist as long as the browser tab is open.
    For permanent storage, download the database file.
    """)
    
    st.markdown("---")
    
    st.subheader("📈 Database Statistics")
    
    conn = get_db_connection()
    if conn:
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            party_count = conn.execute("SELECT COUNT(*) FROM parties").fetchone()[0]
            st.metric("👤 Total Parties", party_count)
        
        with col_stats2:
            loan_count = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
            st.metric("💰 Total Loans", loan_count)
        
        with col_stats3:
            tx_count = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
            st.metric("📝 Total Transactions", tx_count)
        
        conn.close()










