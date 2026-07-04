
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import base64

# ==========================================
# 1. PERMANENT DATA STORAGE STORAGE SETUP
# ==========================================
def get_db_connection():
    # check_same_thread=False guarantees stability and prevents row drops on sync refreshing
    conn = sqlite3.connect('gold_loan_system.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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
    
    # Gold Loans Table
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

init_db()

# ==========================================
# 2. UI STYLE & CONFIGURATION DEFINITIONS
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan ERP", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main-title { color: #2C3E50; font-weight: 800; text-align: center; font-size: 32px; margin-bottom: 5px; }
    .sub-title { color: #7F8C8D; text-align: center; font-size: 16px; margin-bottom: 30px; }
    .gold-header { color: #b8860b; font-weight: bold; text-align: center; margin-bottom: 20px; font-size: 24px; }
    .section-card { background-color: #F8F9F9; padding: 25px; border-radius: 12px; border: 1px solid #E5E8E8; margin-bottom: 20px; }
    .agreement-box { border: 2px solid #b8860b; padding: 40px; background-color: #fcfcf4; border-radius: 10px; font-family: 'Inter', sans-serif; color: #333; line-height: 1.8; }
    .agreement-table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }
    .agreement-table th, .agreement-table td { border: 1px solid #b8860b; padding: 12px; text-align: left; }
    .agreement-table th { background-color: #f5f0db; color: #b8860b; font-weight: bold; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 1px solid #E5E8E8; }
    .printable-ledger { font-family: Arial, sans-serif; padding: 35px; border: 1px solid #BDC3C7; background-color: white; color: black; border-radius: 8px; }
    .printable-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .printable-table th, .printable-table td { border: 1px solid #000; padding: 10px; text-align: left; }
    .printable-table th { background-color: #EAEDED; }
    .receipt-box { border: 2px dashed #7F8C8D; padding: 25px; margin-top: 15px; background-color: #fff; }
    </style>
""", unsafe_allow_html=True)

conn = get_db_connection()
count_parties = conn.execute("SELECT COUNT(*) FROM parties").fetchone()[0]
count_loans = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
count_gold = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
count_tx = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
conn.close()

# HTML Document Templates
def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row['gold_image_base64']:
        image_html_tag = f"""
        <div style="margin-top:25px; margin-bottom:25px; text-align:center;">
            <p><b>പണയം വെച്ച ആഭരണത്തിന്റെ ഫോട്ടോ (Pledged Asset Photo):</b></p>
            <img src="data:image/jpeg;base64,{loan_row['gold_image_base64']}" style="max-width:320px; max-height:240px; border:3px solid #b8860b; border-radius:8px;"/>
        </div>
        """
    else:
        image_html_tag = "<p style='color:grey; font-style:italic; text-align:center;'>ചിത്രം ലഭ്യമല്ല (No photo attached)</p>"

    return f"""
    <div class="agreement-box">
        <h2 class="gold-header">സ്വർണ്ണപ്പണയ വായ്പാ കരാർ പത്രം (Gold Loan Agreement)</h2>
        <div style="text-align: center; margin-bottom: 20px;">
            <b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}
        </div>
        <hr style="border-top: 1px solid #b8860b;">
        
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row['name']}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര്:</b> {party_row['guardian_name'] or 'N/A'}</li>
            <li><b>മേൽവിലാസം (Address):</b> {party_row['address'] or 'N/A'}, {party_row['pincode'] or ''}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
        </ul>

        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table class="agreement-table">
            <tr><th>വിവരണം (Description)</th><th>തുക / നിരക്ക് (Amount / Rate)</th></tr>
            <tr><td><b>അനുവദിച്ച വായ്പ തുക (Principal / Disbursement Amount)</b></td><td><b>₹{loan_row['principal']:,.2f}</b></td></tr>
            <tr><td>പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td>{loan_row['interest_rate']}%</td></tr>
            <tr><td>കാലാവധി (Tenure)</td><td>{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
            <tr><td><b>പ്രതിമാസ തവണ (EMI)</b></td><td><b>₹{loan_row['emi']:,.2f}</b></td></tr>
            <tr style="background-color: #fff0f6;"><td>ആകെ പലിശ തുക (Interest Amount)</td><td>₹{loan_row['interest_amount']:,.2f}</td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത് (Total Payable)</td><td>₹{loan_row['total_payable']:,.2f}</td></tr>
        </table>

        <h3>💎 3. പണയ वस्तूക്കളുടെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം (Description):</b> {loan_row['gold_description'] or 'N/A'}</li>
            <li><b>ആകെ എണ്ണം / തൂക്കം:</b> {loan_row['items_count']} Nos / {loan_row['net_weight']} ഗ്രാം ({loan_row['purity_karat']}K)</li>
            <li><b>സേഫ് വോൾട്ട് ഐഡി (Vault ID):</b> `{loan_row['vault_id']}`</li>
        </ul>
        
        {image_html_tag}
        <br>
        <table style="width:100%; margin-top:35px;">
            <tr>
                <td>___________________________<br><b>വായ്പക്കാരന്റെ ഒപ്പ്</b></td>
                <td style="text-align:right;">___________________________<br><b>സ്ഥാപന അധികാരിയുടെ ഒപ്പ്</b></td>
            </tr>
        </table>
    </div>
    """

def generate_fee_receipt_html(loan_row, party_row):
    total_fees = loan_row['processing_fee'] + loan_row['admin_fee'] + loan_row['documentation_fee']
    return f"""
    <div class="printable-ledger receipt-box">
        <h2 style="text-align:center;margin-bottom:2px;color:#b8860b;">AURA LOAN MANAGEMENT SYSTEM</h2>
        <h4 style="text-align:center;margin-top:0px;color:#555;">📋 ഫീസ് അടച്ച വൗച്ചർ / FEES RECEIPT</h4>
        <hr style="border-top: 1px dashed #7F8C8D;">
        <table style="width:100%; margin-bottom:15px; font-size:14px;">
            <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {party_row['name']}</td><td><b>രസീത് നമ്പർ (Receipt No):</b> #FEE-{loan_row['id']}</td></tr>
            <tr><td><b>ലോൺ ലിങ്ക് ഐഡി (Loan Ref ID):</b> #{loan_row['id']}</td><td><b>തീയതി (Date):</b> {loan_row['disbursed_date']}</td></tr>
            <tr><td><b>മൊബൈൽ (Mobile):</b> {party_row['mobile']}</td><td><b>സ്റ്റാറ്റസ് (Status):</b> <span style="color:green;font-weight:bold;">Paid</span></td></tr>
        </table>
        
        <table class="printable-table">
            <thead>
                <tr style="background-color: #f9f9f9;"><th>Sl No</th><th>ഫീസ് വിവരണം (Fee Description)</th><th>ഈടാക്കിയ തുക (Amount)</th></tr>
            </thead>
            <tbody>
                <tr><td style="text-align:center;">1</td><td>പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td>₹{loan_row['processing_fee']:,.2f}</td></tr>
                <tr><td style="text-align:center;">2</td><td>അഡ്മിൻ ഫീസ് (Admin Fee)</td><td>₹{loan_row['admin_fee']:,.2f}</td></tr>
                <tr><td style="text-align:center;">3</td><td>ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td>₹{loan_row['documentation_fee']:,.2f}</td></tr>
                <tr style="font-weight:bold; background-color: #f5f5f5;"><td colspan="2" style="text-align:right;">ആകെ ലഭിച്ച തുക (Total Fees Collected):</td><td>₹{total_fees:,.2f}</td></tr>
            </tbody>
        </table>
        <br>
        <p style="font-size:13px; font-weight:bold;">തുക അക്ഷരത്തിൽ: രൂപ {total_fees} മാത്രം.</p>
        <br>
        <table style="width:100%; margin-top:20px; font-size:14px; text-align:center;">
            <tr><td>____________________<br>ക്യാഷർ (Cashier)</td><td>____________________<br>കസ്റ്റമർ ഒപ്പ് (Customer Signature)</td></tr>
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
    "✏️ Edit Party Details",
    "💰 Gold Loan Management",
    "💍 Gold Pledge Management",
    "📄 Loan Agreement (Malayalam)",
    "📅 EMI Schedule",
    "💾 Backup & Restore"
]
choice = st.sidebar.selectbox("Select Module", main_menu)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Sub-Modules")
if choice == "💰 Gold Loan Management":
    sub_choice = st.sidebar.radio("Sub Navigation Modules", ["💸 Loan Disbursement", "📊 Party Ledger"])
else:
    st.sidebar.markdown("*No active sub-module*")
    sub_choice = None

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Status")
st.sidebar.write(f"👤 Total Parties: **{count_parties}**")
st.sidebar.write(f"💰 Active Loans: **{count_loans}**")
st.sidebar.write(f"💍 Vaulted Items: **{count_gold}**")

st.markdown('<div class="main-title">💎 AuraLoan ERP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Secure Enterprise Gold Loan Management Workspace</div>', unsafe_allow_html=True)

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    conn = get_db_connection()
    
    total_active_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
    total_disbursed = conn.execute("SELECT SUM(principal) FROM loans").fetchone()[0] or 0.0
    total_gold_wt = conn.execute("SELECT SUM(net_weight) FROM loans WHERE status='Active'").fetchone()[0] or 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Loan Accounts", total_active_loans)
    col2.metric("Total Disbursement Amount (Principal)", f"₹{total_disbursed:,.2f}")
    col3.metric("Total Gold Vaulted (Net Weight)", f"{total_gold_wt:.2f} g")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📈 Live Portfolio Monitoring Stream")
    df_dashboard = pd.read_sql_query("""
        SELECT l.id as 'Loan ID', p.name as 'Customer Name', l.principal as 'Disbursement/Principal Amount (₹)', 
               l.interest_amount as 'Interest (₹)', l.total_payable as 'Total Payable (₹)', 
               l.emi as 'Monthly EMI (₹)', l.status as 'Status'
        FROM loans l JOIN parties p ON l.party_id = p.id
    """, conn)
    st.dataframe(df_dashboard, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    conn.close()

# ==========================================
# MODULE: PARTY MASTER
# ==========================================
elif choice == "👤 Party Master":
    st.header("👤 Customer Registration (Party Master)")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
                conn.execute("""
                    INSERT INTO parties (name, guardian_name, dob, mobile, whatsapp, address, pincode, pan_masked, occupation, qualification, kyc_status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, guardian_name, str(dob), mobile, whatsapp, address, pincode, pan, occupation, qualification, kyc_status, str(datetime.now().date())))
                conn.commit()
                conn.close()
                st.success(f"Successfully registered identity profile for: {name}")
                st.rerun()
            else:
                st.error("Name and Mobile fields are mandatory.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE: EDIT PARTY DETAILS
# ==========================================
elif choice == "✏️ Edit Party Details":
    st.header("✏️ Edit Complete Party Profile Details")
    conn = get_db_connection()
    parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
    
    if parties_df.empty:
        st.info("No customer profiles inside structural logs.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        party_to_edit = st.selectbox("Select Party Profile to Update", parties_df['id'].tolist(), format_func=lambda x: parties_df[parties_df['id']==x]['name'].values[0])
        selected_row = parties_df[parties_df['id'] == party_to_edit].iloc[0]
        
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
            
            if st.form_submit_button("Save Updates"):
                conn.execute("""
                    UPDATE parties SET 
                        name=?, guardian_name=?, mobile=?, whatsapp=?, 
                        occupation=?, qualification=?, address=?, pincode=?, kyc_status=?
                    WHERE id=?
                """, (edit_name, edit_guardian, edit_mobile, edit_whatsapp, edit_occupation, edit_qualification, edit_address, edit_pincode, edit_kyc, party_to_edit))
                conn.commit()
                st.success("Customer log modifications written successfully.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    conn.close()

# ==========================================
# PARENT MODULE: GOLD LOAN MANAGEMENT
# ==========================================
elif choice == "💰 Gold Loan Management":
    conn = get_db_connection()
    
    # 💸 SUB-MODULE 1: LOAN DISBURSEMENT MODULE
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation Engine")
        parties = conn.execute("SELECT id, name FROM parties WHERE kyc_status='Verified'").fetchall()
        
        if not parties:
            st.warning("⚠️ No Verified Customers Available. Please verify a profile inside Party Master maps first.")
        else:
            party_options = {p['id']: p['name'] for p in parties}
            
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
                    st.markdown("📷 **Collateral Asset Capture**")
                    photo_source = st.radio("ഫോട്ടോ എടുക്കേണ്ട രീതി", ["Upload File", "Use Device Camera"], horizontal=True)
                    
                    gold_photo_data = None
                    if photo_source == "Upload File":
                        gold_photo_data = st.file_uploader("Select Photo File", type=["jpg", "png", "jpeg"])
                    else:
                        gold_photo_data = st.camera_input("Capture Live Thumbnail")
                    
                with col2:
                    st.markdown("#### 📊 Calculation Rules Config (Disbursement = Principal)")
                    max_eligible = appraised_val * 0.75
                    st.info(f"Regulatory 75% LTV Cap Boundary: **₹{max_eligible:,.2f}**")
                    
                    # Core Sync Requirement: Disbursement Amount is mapped exactly into core Principal allocation
                    principal = st.number_input("അനുവദിച്ച വായ്പ തുക / Disbursement Amount (Principal) - ₹", min_value=0.0, value=40375.0)
                    interest_rate = st.number_input("പലിശ നിരക്ക് (Interest Rate % For Total Duration)", min_value=0.0, value=12.0)
                    duration = st.number_input("കാലാവധി (Tenure Duration - Months)", min_value=1, max_value=36, value=12)
                    
                    st.markdown("---")
                    st.markdown("#### 🏷️ ആഡ്ഓൺ ചാർജ്ജുകൾ (Service Fees Matrix Component)")
                    processing_fee = st.number_input("പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee - ₹)", min_value=0.0, value=500.0)
                    admin_fee = st.number_input("അഡ്മിൻ ഫീസ് (Admin Fee - ₹)", min_value=0.0, value=200.0)
                    doc_fee = st.number_input("ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee - ₹)", min_value=0.0, value=200.0)
                    
                    # LOGICAL EXECUTION STRUCTURE SYNCHRONIZED
                    interest_amount = principal * (interest_rate / 100)
                    total_payable = principal + interest_amount
                    calculated_emi = total_payable / duration if duration > 0 else 0.0
                    
                    st.markdown("---")
                    st.write(f"**അസ്സൽ വായ്പ / നൽകിയ തുക (Disbursement Amount):** ₹{principal:,.2f}")
                    st.write(f"**പ്രതിമാസ തവണ (EMI):** ₹{calculated_emi:,.2f}")
                    
                if st.form_submit_button("Disburse Capital Asset Allocation Line"):
                    if principal > max_eligible:
                        st.error("Requested volume violates the regulatory 75% LTV framework.")
                    elif principal <= 0 or net_wt <= 0:
                        st.error("Invalid input metrics inside fields.")
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
                        st.success(f"🎉 Loan Account #{loan_id} successfully finalized! View receipts inside 'Loan Agreement (Malayalam)' module.")
            st.markdown('</div>', unsafe_allow_html=True)

    # 📊 SUB-MODULE 2: PARTY LEDGER ACCOUNTANT
    elif sub_choice == "📊 Party Ledger":
        st.header("📊 Customer Ledger Statements Node")
        active_loans = conn.execute("SELECT l.id, p.name, l.principal FROM loans l JOIN parties p ON l.party_id = p.id WHERE l.status='Active'").fetchall()
        
        if not active_loans:
            st.info("No active open-balance files currently processing inside ledger lines.")
        else:
            loan_options = {al['id']: f"Loan ID #{al['id']} - Holder: {al['name']} (₹{al['principal']})" for al in active_loans}
            selected_loan = st.selectbox("Select Target Portfolio File", list(loan_options.keys()), format_func=lambda x: loan_options[x])
            
            tab_post, tab_view, tab_print = st.tabs(["💳 Record Repayment Entry", "📑 View Live Balances", "🖨️ Printable Document Generator"])
            
            with tab_post:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                with st.form("repayment_ledger_post_form"):
                    repay_amt = st.number_input("Repayment Amount Collected (₹)", min_value=0.0, step=100.0)
                    repay_date = st.date_input("Settlement Date")
                    type_tx = st.selectbox("Allocation Matrix Class", ["Repayment", "Interest Settlement"])
                    
                    if st.form_submit_button("Post Transaction"):
                        if repay_amt > 0:
                            conn.execute("INSERT INTO ledger (loan_id, transaction_type, amount, transaction_date) VALUES (?, ?, ?, ?)", (selected_loan, type_tx, repay_amt, str(repay_date)))
                            conn.commit()
                            st.success("Entry successfully written against active portfolio row index.")
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                            
            with tab_view:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                loan_row_data = conn.execute(f"SELECT total_payable, principal FROM loans WHERE id={selected_loan}").fetchone()
                total_liability = float(loan_row_data['total_payable'] or 0.0)
                total_repaid_credits = conn.execute(f"SELECT SUM(amount) FROM ledger WHERE loan_id={selected_loan} AND transaction_type IN ('Repayment', 'Interest Settlement')").fetchone()[0]
                total_repaid_credits = float(total_repaid_credits or 0.0)
                live_outstanding_balance = total_liability - total_repaid_credits
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Disbursement/Principal Amount", f"₹{loan_row_data['principal']:,.2f}")
                col_m2.metric("Total Liability (with Interest)", f"₹{total_liability:,.2f}")
                col_m3.metric("Current Outstanding Balance", f"₹{live_outstanding_balance:,.2f}", delta_color="inverse")
                
                tx_history_df = pd.read_sql_query(f"SELECT transaction_type as 'Activity Type', amount as 'Value (₹)', transaction_date as 'Date' FROM ledger WHERE loan_id={selected_loan} ORDER BY ROWID ASC", conn)
                st.table(tx_history_df)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with tab_print:
                p_loan = conn.execute(f"SELECT l.*, p.name, p.mobile, p.address FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.id={selected_loan}").fetchone()
                tx_rows = conn.execute(f"SELECT * FROM ledger WHERE loan_id={selected_loan} ORDER BY ROWID ASC").fetchall()
                
                table_html_rows = ""
                for tx in tx_rows:
                    display_type = "Loan Disbursement (Principal)" if tx['transaction_type'] == "Disbursement" else tx['transaction_type']
                    table_html_rows += f"<tr><td>{tx['transaction_date']}</td><td>{display_type}</td><td>₹{tx['amount']:,.2f}</td></tr>"
                
                total_repaid = sum([t['amount'] for t in tx_rows if t['transaction_type'] in ['Repayment', 'Interest Settlement']])
                balance_left = p_loan['total_payable'] - total_repaid
                
                printable_html = f"""
                <div class="printable-ledger">
                    <h2 style="text-align:center;margin-bottom:2px;">AURA LOAN MANAGEMENT SYSTEM</h2>
                    <h4 style="text-align:center;margin-top:0px;color:#555;">STATEMENT OF ACCOUNT / PARTY LEDGER</h4>
                    <hr>
                    <table style="width:100%; margin-bottom:20px; font-size:14px;">
                        <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {p_loan['name']}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{p_loan['id']}</td></tr>
                        <tr><td><b>ഫോൺ (Mobile):</b> {p_loan['mobile']}</td><td><b>തീയതി (Date Issued):</b> {p_loan['disbursed_date']}</td></tr>
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
                        <p><b>അസ്സൽ തുക (Disbursement Principal):</b> ₹{p_loan['principal']:,.2f}</p>
                        <p><b>ആകെ പലിശ (Total Interest Charged):</b> ₹{p_loan['interest_amount']:,.2f}</p>
                        <hr style="border-top: 1px solid #000; width: 40%; margin-left: auto;">
                        <p><b>ആകെ അടയ്ക്കേണ്ടത് (Total Payable):</b> ₹{p_loan['total_payable']:,.2f}</p>
                        <p style="color:green;"><b>ഇതുവരെ അടച്ചത് (Total Repaid):</b> ₹{total_repaid:,.2f}</p>
                        <p style="color:red; font-size:18px;"><b>ബാക്കി കുടിശ്ശിക (Outstanding Balance):</b> <b>₹{balance_left:,.2f}</b></p>
                    </div>
                </div>
                """
                st.markdown(printable_html, unsafe_allow_html=True)
                st.download_button(label="📥 ഡൗൺലോഡ് ലെഡ്ജർ (Download HTML Sheet)", data=printable_html, file_name=f"Ledger_Loan_{selected_loan}.html", mime="text/html")
    conn.close()

# ==========================================
# MODULE: GOLD PLEDGE MANAGEMENT
# ==========================================
elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory Vault Details")
    conn = get_db_connection()
    loans_cursor = conn.execute("SELECT l.*, p.name as pledger_name FROM loans l JOIN parties p ON l.party_id = p.id WHERE l.status='Active'").fetchall()
    
    if not loans_cursor:
        st.info("No physical items inside security vaults currently logged.")
    else:
        for row in loans_cursor:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            col_text, col_img = st.columns([2, 1])
            with col_text:
                st.markdown(f"### 📦 Loan Account Portfolio Reference #{row['id']}")
                st.write(f"👤 **ഉടമസ്ഥൻ:** {row['pledger_name']}")
                st.write(f"📝 **ആഭരണ വിവരണം:** {row['gold_description']}")
                st.write(f"🔢 **ആകെ എണ്ണം / തൂക്കം:** {row['items_count']} Nos / {row['net_weight']} ഗ്രാം")
                st.write(f"🔒 **വോൾട്ട് സൂചിക ഐഡി:** `{row['vault_id']}`")
            with col_img:
                if row['gold_image_base64']:
                    img_bytes = base64.b64decode(row['gold_image_base64'])
                    st.image(img_bytes, caption="Pledged Asset Document Photo", width=180)
            st.markdown('</div>', unsafe_allow_html=True)
    conn.close()

# ==========================================
# MODULE: LOAN AGREEMENT MALAYALAM (ISOLATED DOWNSTREAM INTERFACE)
# ==========================================
elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement Console")
    conn = get_db_connection()
    available_contracts = conn.execute("SELECT l.id, p.name FROM loans l JOIN parties p ON l.party_id=p.id").fetchall()
    
    if not available_contracts:
        st.info("No records to pull configuration agreement files for.")
    else:
        contract_options = {ac['id']: f"Loan File Record #{ac['id']} - Customer Name: {ac['name']}" for ac in available_contracts}
        target_contract = st.selectbox("Select Target Portfolio Record", list(contract_options.keys()), format_func=lambda x: contract_options[x])
        
        loan_row = conn.execute(f"SELECT * FROM loans WHERE id={target_contract}").fetchone()
        party_row = conn.execute(f"SELECT * FROM parties WHERE id={loan_row['party_id']}").fetchone()
        
        tab_contract_view, tab_receipt_view = st.tabs(["📜 കരാർ പത്രം (Agreement)", "🧾 ഫീസ് രസീത് (Fee Receipt)"])
        
        with tab_contract_view:
            agreement_html = generate_agreement_html(loan_row, party_row)
            st.markdown(agreement_html, unsafe_allow_html=True)
            st.download_button(label="📥 ഡൗൺലോഡ് കരാർ പത്രം (Download Agreement HTML Sheet)", data=agreement_html, file_name=f"Agreement_Loan_{loan_row['id']}.html", mime="text/html")
            
        with tab_receipt_view:
            fee_html = generate_fee_receipt_html(loan_row, party_row)
            st.markdown(fee_html, unsafe_allow_html=True)
            st.download_button(label="📥 ഡൗൺലോഡ് ഫീസ് രസീത് (Download Fee Receipt)", data=fee_html, file_name=f"Fee_Receipt_Loan_{loan_row['id']}.html", mime="text/html")
    conn.close()

# ==========================================
# MODULE: EMI SCHEDULE MATRIX
# ==========================================
elif choice == "📅 EMI Schedule":
    st.header("📅 Monthly Recovery Projection Mapping (EMI Schedule)")
    conn = get_db_connection()
    active_loans = conn.execute("SELECT l.id, p.name, l.emi, l.duration_months, l.total_payable FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.status='Active'").fetchall()
    
    if not active_loans:
        st.info("No active loan lines running projection amortizations.")
    else:
        loan_options = {al['id']: f"Loan Reference Account Line #{al['id']} (Holder: {al['name']})" for al in active_loans}
        selected_sched = st.selectbox("Select Target Loan Plan ID", list(loan_options.keys()), format_func=lambda x: loan_options[x])
        
        target_l = conn.execute(f"SELECT l.*, p.name, p.mobile FROM loans l JOIN parties p ON l.party_id=p.id WHERE l.id={selected_sched}").fetchone()
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        schedule_rows_html = ""
        remaining_reduction_pool = target_l['total_payable']
        
        schedule_list = []
        for index in range(1, target_l['duration_months'] + 1):
            remaining_reduction_pool -= target_l['emi']
            current_rem = max(0.0, remaining_reduction_pool)
            
            schedule_rows_html += f"""
            <tr>
                <td style="border: 1px solid #000; padding: 10px; text-align: center;">Month {index}</td>
                <td style="border: 1px solid #000; padding: 10px;">₹{target_l['emi']:,.2f}</td>
                <td style="border: 1px solid #000; padding: 10px;">₹{current_rem:,.2f}</td>
            </tr>
            """
            schedule_list.append({
                "Installment Sequence": f"Month No. {index}",
                "Payment Amount (₹)": f"₹{target_l['emi']:,.2f}",
                "Outstanding Balance (₹)": f"₹{current_rem:,.2f}"
            })
            
        st.table(pd.DataFrame(schedule_list))
        st.markdown('</div>', unsafe_allow_html=True)
        
        printable_schedule_html = f"""
        <div class="printable-ledger">
            <h2 style="text-align:center;margin-bottom:2px;">AURA LOAN MANAGEMENT SYSTEM</h2>
            <h4 style="text-align:center;margin-top:0px;color:#555;">📊 പ്രതിമാസ തവണ വിവരപ്പട്ടിക (EMI SCHEDULE PLAN)</h4>
            <hr>
            <table style="width:100%; margin-bottom:20px; font-size:14px;">
                <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {target_l['name']}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{target_l['id']}</td></tr>
                <tr><td><b>ഫോൺ (Mobile):</b> {target_l['mobile']}</td><td><b>അസ്സൽ വായ്പ (Principal/Disbursed Amount):</b> ₹{target_l['principal']:,.2f}</td></tr>
                <tr><td><b>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത്:</b> ₹{target_l['total_payable']:,.2f}</td></tr>
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
        
        with st.expander("🖨️ പ്രിന്റ് ചെയ്യാവുന്ന EMI ഷെഡ്യൂൾ വൗച്ചർ കാണുക"):
            st.markdown(printable_schedule_html, unsafe_allow_html=True)
            st.download_button(label="📥 ഡൗൺലോഡ് & പ്രിന്റ് ഷെഡ്യൂൾ", data=printable_schedule_html, file_name=f"EMI_Schedule_Loan_{selected_sched}.html", mime="text/html")
    conn.close()

# ==========================================
# MODULE: BACKUP & RESTORE DATA
# ==========================================
elif choice == "💾 Backup & Restore":
    st.header("💾 Core Database Snapshots Engine")
    conn = get_db_connection()
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    with open("gold_loan_system.db", "rb") as db_file:
        db_binary_stream = db_file.read()
        
    st.download_button(
        label="📥 Download Persistent SQL Storage Snapshot (.DB File)",
        data=db_binary_stream,
        file_name=f"gold_loan_system_backup_{datetime.now().date()}.db",
        mime="application/octet-stream"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    conn.close()




