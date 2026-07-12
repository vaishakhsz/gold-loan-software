import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. GOOGLE SHEETS CONNECTION INITIALIZATION
# ==========================================
def get_gsheets_connection():
    """Create and return Google Sheets connection"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn

def get_next_id(worksheet_name, conn):
    """Get the next available ID for a worksheet"""
    try:
        df = conn.read(worksheet=worksheet_name)
        if df.empty or len(df) == 0:
            return 1
        return int(df['id'].max()) + 1
    except:
        return 1

def init_sheets():
    """Initialize Google Sheets with required worksheets"""
    conn = get_gsheets_connection()
    
    # Define sheet structures
    parties_columns = [
        'id', 'name', 'guardian_name', 'dob', 'mobile', 'whatsapp',
        'address', 'pincode', 'pan_masked', 'occupation', 'qualification', 
        'kyc_status', 'created_at'
    ]
    
    loans_columns = [
        'id', 'party_id', 'party_name', 'principal', 'interest_rate', 
        'duration_months', 'emi', 'processing_fee', 'admin_fee', 
        'documentation_fee', 'net_disbursed', 'interest_amount', 
        'total_payable', 'gold_description', 'items_count', 'gross_weight',
        'net_weight', 'purity_karat', 'appraised_value', 'vault_id',
        'gold_image_base64', 'status', 'disbursed_date', 'created_at'
    ]
    
    ledger_columns = [
        'id', 'loan_id', 'transaction_type', 'amount', 
        'transaction_date', 'created_at'
    ]
    
    # Create empty sheets if they don't exist
    try:
        # Try reading Parties sheet
        parties_df = conn.read(worksheet="Parties")
        if parties_df.empty:
            parties_df = pd.DataFrame(columns=parties_columns)
            conn.update(worksheet="Parties", data=parties_df)
    except:
        # Sheet doesn't exist, create it
        parties_df = pd.DataFrame(columns=parties_columns)
        conn.create(worksheet="Parties", data=parties_df)
    
    try:
        # Try reading Loans sheet
        loans_df = conn.read(worksheet="Loans")
        if loans_df.empty:
            loans_df = pd.DataFrame(columns=loans_columns)
            conn.update(worksheet="Loans", data=loans_df)
    except:
        loans_df = pd.DataFrame(columns=loans_columns)
        conn.create(worksheet="Loans", data=loans_df)
    
    try:
        # Try reading Ledger sheet
        ledger_df = conn.read(worksheet="Ledger")
        if ledger_df.empty:
            ledger_df = pd.DataFrame(columns=ledger_columns)
            conn.update(worksheet="Ledger", data=ledger_df)
    except:
        ledger_df = pd.DataFrame(columns=ledger_columns)
        conn.create(worksheet="Ledger", data=ledger_df)
    
    return conn

# Initialize sheets
try:
    conn = init_sheets()
except Exception as e:
    st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
    st.info("Please make sure your secrets.toml file is properly configured.")
    st.stop()

# ==========================================
# 2. DATABASE OPERATIONS (Now using Google Sheets)
# ==========================================
def add_party(party_data):
    """Add a new party to Google Sheets"""
    conn = get_gsheets_connection()
    parties_df = conn.read(worksheet="Parties")
    
    if parties_df.empty:
        parties_df = pd.DataFrame(columns=party_data.keys())
    
    new_id = get_next_id("Parties", conn)
    party_data['id'] = new_id
    party_data['created_at'] = str(datetime.now().date())
    
    new_row = pd.DataFrame([party_data])
    parties_df = pd.concat([parties_df, new_row], ignore_index=True)
    conn.update(worksheet="Parties", data=parties_df)
    return new_id

def update_party(party_id, updated_data):
    """Update an existing party record"""
    conn = get_gsheets_connection()
    parties_df = conn.read(worksheet="Parties")
    
    if not parties_df.empty:
        idx = parties_df[parties_df['id'] == party_id].index
        if len(idx) > 0:
            for key, value in updated_data.items():
                parties_df.loc[idx[0], key] = value
            conn.update(worksheet="Parties", data=parties_df)
            return True
    return False

def delete_party(party_id):
    """Delete a party record"""
    conn = get_gsheets_connection()
    parties_df = conn.read(worksheet="Parties")
    
    if not parties_df.empty:
        parties_df = parties_df[parties_df['id'] != party_id]
        conn.update(worksheet="Parties", data=parties_df)
        return True
    return False

def add_loan(loan_data):
    """Add a new loan record"""
    conn = get_gsheets_connection()
    loans_df = conn.read(worksheet="Loans")
    
    if loans_df.empty:
        loans_df = pd.DataFrame(columns=loan_data.keys())
    
    new_id = get_next_id("Loans", conn)
    loan_data['id'] = new_id
    loan_data['created_at'] = str(datetime.now().date())
    
    new_row = pd.DataFrame([loan_data])
    loans_df = pd.concat([loans_df, new_row], ignore_index=True)
    conn.update(worksheet="Loans", data=loans_df)
    return new_id

def update_loan_status(loan_id, status):
    """Update loan status"""
    conn = get_gsheets_connection()
    loans_df = conn.read(worksheet="Loans")
    
    if not loans_df.empty:
        loans_df.loc[loans_df['id'] == loan_id, 'status'] = status
        conn.update(worksheet="Loans", data=loans_df)
        return True
    return False

def add_ledger_entry(entry_data):
    """Add a transaction to ledger"""
    conn = get_gsheets_connection()
    ledger_df = conn.read(worksheet="Ledger")
    
    if ledger_df.empty:
        ledger_df = pd.DataFrame(columns=entry_data.keys())
    
    new_id = get_next_id("Ledger", conn)
    entry_data['id'] = new_id
    entry_data['created_at'] = str(datetime.now().date())
    
    new_row = pd.DataFrame([entry_data])
    ledger_df = pd.concat([ledger_df, new_row], ignore_index=True)
    conn.update(worksheet="Ledger", data=ledger_df)
    return new_id

def get_all_parties():
    """Get all party records"""
    conn = get_gsheets_connection()
    try:
        df = conn.read(worksheet="Parties")
        return df if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def get_all_loans():
    """Get all loan records"""
    conn = get_gsheets_connection()
    try:
        df = conn.read(worksheet="Loans")
        return df if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def get_ledger_for_loan(loan_id):
    """Get ledger entries for a specific loan"""
    conn = get_gsheets_connection()
    try:
        df = conn.read(worksheet="Ledger")
        if not df.empty:
            return df[df['loan_id'] == loan_id]
    except:
        pass
    return pd.DataFrame()

# ==========================================
# 3. STREAMLIT UI & STYLE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

# Custom Styles
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF6EE !important;
    }
    .gold-header { 
        color: #8B6508; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .stMetric { 
        background-color: #FFFDF7 !important; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #E3C16F !important;
        box-shadow: 0px 2px 4px rgba(227, 193, 111, 0.1);
    }
    div[data-testid="stForm"] {
        background-color: #FFFDF9 !important;
        border: 1px solid #E3C16F !important;
        border-radius: 10px;
    }
    .agreement-box { 
        border: 2px solid #b8860b; 
        padding: 30px; 
        background-color: #fcfcf4; 
        border-radius: 10px; 
        font-family: 'Inter', sans-serif; 
        color: #333; 
        line-height: 1.7; 
    }
    .agreement-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 15px; 
        margin-bottom: 15px; 
    }
    .agreement-table th, .agreement-table td { 
        border: 1px solid #b8860b; 
        padding: 10px; 
        text-align: left; 
    }
    .agreement-table th { 
        background-color: #f5f0db; 
        color: #b8860b; 
    }
    .printable-ledger { 
        font-family: Arial, sans-serif; 
        padding: 25px; 
        border: 1px solid #ccc; 
        background-color: white; 
        color: black; 
        border-radius: 5px; 
    }
    .printable-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 10px; 
    }
    .printable-table th, .printable-table td { 
        border: 1px solid #000; 
        padding: 8px; 
        text-align: left; 
    }
    .printable-table th { 
        background-color: #f2f2f2; 
    }
    .receipt-box { 
        border: 2px dashed #333; 
        padding: 20px; 
        margin-top: 15px; 
        background-color: #fff; 
    }
    </style>
""", unsafe_allow_html=True)

# Fetch Live System Counters
parties_df = get_all_parties()
loans_df = get_all_loans()
ledger_df = conn.read(worksheet="Ledger") if not conn.read(worksheet="Ledger").empty else pd.DataFrame()

count_parties = len(parties_df) if not parties_df.empty else 0
count_loans = len(loans_df) if not loans_df.empty else 0
count_gold = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
count_tx = len(ledger_df) if not ledger_df.empty else 0

# Helper function to generate agreement HTML
def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row.get('gold_image_base64') and loan_row['gold_image_base64']:
        image_html_tag = f"""
        <div style="margin-top:20px; margin-bottom:20px; text-align:center;">
            <p><b>പണയം വെച്ച ആഭരണത്തിന്റെ ഫോട്ടോ (Pledged Asset Photo):</b></p>
            <img src="data:image/jpeg;base64,{loan_row['gold_image_base64']}" style="max-width:320px; max-height:240px; border:3px solid #b8860b; border-radius:8px;"/>
        </div>
        """
    
    return f"""
    <div class="agreement-box">
        <h2 class="gold-header">സ്വർണ്ണപ്പണയ വായ്പാ കരാർ പത്രം (Gold Loan Agreement)</h2>
        <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}</p>
        <hr style="border-top: 1px solid #b8860b;">
        
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row['name']}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</b> {party_row.get('guardian_name', 'N/A') or 'N/A'}</li>
            <li><b>വിലാസം (Address):</b> {party_row.get('address', 'N/A') or 'N/A'}, {party_row.get('pincode', '') or ''}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
            <li><b>തൊഴിൽ (Occupation):</b> {party_row.get('occupation', 'N/A') or 'N/A'}</li>
            <li><b>യോഗ്യത (Qualification):</b> {party_row.get('qualification', 'N/A') or 'N/A'}</li>
        </ul>

        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table class="agreement-table">
            <tr><th>വിവരണം (Description)</th><th>തുക / നിരക്ക് (Amount / Rate)</th></tr>
            <tr><td>അനുവദിച്ച വായ്പ തുക (Principal / Disbursement)</td><td><b>₹{float(loan_row['principal']):,.2f}</b></td></tr>
            <tr><td>പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td>{loan_row['interest_rate']}%</td></tr>
            <tr><td>കാലാവധി (Tenure)</td><td>{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
            <tr><td>പ്രതിമാസ തവണ (EMI)</td><td><b>₹{float(loan_row['emi']):,.2f}</b></td></tr>
            <tr style="font-weight:bold; background-color: #fff0f6;"><td>ആകെ പലിശ തുക (Interest Amount)</td><td>₹{float(loan_row['interest_amount']):,.2f}</td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത് (Total Payable)</td><td>₹{float(loan_row['total_payable']):,.2f}</td></tr>
        </table>

        <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം (Description):</b> {loan_row.get('gold_description', 'N/A') or 'N/A'}</li>
            <li><b>ആകെ എണ്ണം (Count):</b> {loan_row['items_count']} Nos</li>
            <li><b>ഭാരം (Weight):</b> {loan_row['net_weight']} ഗ്രാം</li>
            <li><b>പ്യൂരിറ്റി (Purity):</b> {loan_row['purity_karat']} Karat</li>
            <li><b>മൂല്യം (Value):</b> ₹{float(loan_row['appraised_value']):,.2f}</li>
            <li><b>വോൾട്ട് സൂചിക (Vault ID):</b> `{loan_row.get('vault_id', 'N/A')}`</li>
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

# Helper function to generate Fee Receipt HTML
def generate_fee_receipt_html(loan_row, party_row):
    total_fees = float(loan_row['processing_fee']) + float(loan_row['admin_fee']) + float(loan_row['documentation_fee'])
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
                <tr><td style="text-align:center;">1</td><td>പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td>₹{float(loan_row['processing_fee']):,.2f}</td></tr>
                <tr><td style="text-align:center;">2</td><td>അഡ്മിൻ ഫീസ് (Admin Fee)</td><td>₹{float(loan_row['admin_fee']):,.2f}</td></tr>
                <tr><td style="text-align:center;">3</td><td>ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td>₹{float(loan_row['documentation_fee']):,.2f}</td></tr>
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
# 4. SIDEBAR NAVIGATION
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
    "💾 Data Management"
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
st.sidebar.write(f"💍 Active Gold: **{count_gold}**")
st.sidebar.write(f"📝 Transactions: **{count_tx}**")

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    loans_df = get_all_loans()
    parties_df = get_all_parties()
    
    if not loans_df.empty:
        total_active_loans = len(loans_df[loans_df['status'] == 'Active'])
        total_disbursed = loans_df['principal'].astype(float).sum()
        total_gold_wt = loans_df[loans_df['status'] == 'Active']['net_weight'].astype(float).sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Loan Accounts", total_active_loans)
        col2.metric("Total Disbursement (Principal Amount)", f"₹{total_disbursed:,.2f}")
        col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
        
        st.subheader("📈 Live Master Monitoring Stream")
        if not loans_df.empty and not parties_df.empty:
            merged_df = loans_df.merge(parties_df[['id', 'name']], left_on='party_id', right_on='id', how='left')
            dashboard_df = merged_df[['id', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']]
            dashboard_df.columns = ['Loan ID', 'Customer Name', 'Principal (₹)', 'Interest (₹)', 'Total Payable (₹)', 'Monthly EMI (₹)', 'Status']
            st.dataframe(dashboard_df, use_container_width=True)
    else:
        st.info("No loan data available yet.")



