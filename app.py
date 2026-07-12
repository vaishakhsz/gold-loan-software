# Fix for segmentation fault - MUST be at the very top
import os
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'

import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. GOOGLE SHEETS CONNECTION INITIALIZATION
# ==========================================
def get_credentials():
    """Get credentials from secrets"""
    creds_dict = {
        "type": "service_account",
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return credentials

def get_gspread_client():
    """Create gspread client"""
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    return gc

def get_worksheet(sheet_name):
    """Get or create worksheet"""
    gc = get_gspread_client()
    spreadsheet_id = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    try:
        sh = gc.open_by_key(spreadsheet_id)
    except Exception as e:
        st.error(f"Cannot access spreadsheet. Make sure it's shared with: {st.secrets['connections']['gsheets']['client_email']}")
        st.stop()
    
    try:
        worksheet = sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="30")
        if sheet_name == "Parties":
            headers = ['id', 'name', 'guardian_name', 'dob', 'mobile', 'whatsapp',
                      'address', 'pincode', 'pan_masked', 'occupation', 'qualification', 
                      'kyc_status', 'created_at']
        elif sheet_name == "Loans":
            headers = ['id', 'party_id', 'party_name', 'principal', 'interest_rate', 
                      'duration_months', 'emi', 'processing_fee', 'admin_fee', 
                      'documentation_fee', 'net_disbursed', 'interest_amount', 
                      'total_payable', 'gold_description', 'items_count', 'gross_weight',
                      'net_weight', 'purity_karat', 'appraised_value', 'vault_id',
                      'gold_image_base64', 'status', 'disbursed_date', 'created_at']
        elif sheet_name == "Ledger":
            headers = ['id', 'loan_id', 'transaction_type', 'amount', 
                      'transaction_date', 'created_at']
        else:
            headers = []
        
        if headers:
            worksheet.append_row(headers)
    
    return worksheet

def get_next_id(worksheet):
    """Get next available ID"""
    try:
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return 1
        
        ids = []
        for row in data[1:]:
            if row and row[0].isdigit():
                ids.append(int(row[0]))
        
        return max(ids) + 1 if ids else 1
    except:
        return 1

def init_sheets():
    """Initialize all required sheets"""
    sheets = ["Parties", "Loans", "Ledger"]
    for sheet in sheets:
        get_worksheet(sheet)
    return True

# Initialize sheets with caching to prevent reloads
@st.cache_resource
def initialize_connection():
    """Initialize Google Sheets connection once"""
    try:
        init_sheets()
        return True
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
        return False

# Initialize
if not initialize_connection():
    st.stop()

# ==========================================
# 2. DATABASE OPERATIONS
# ==========================================
@st.cache_data(ttl=60)
def get_all_parties_cached():
    """Get all parties as DataFrame with caching"""
    ws = get_worksheet("Parties")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_all_loans_cached():
    """Get all loans as DataFrame with caching"""
    ws = get_worksheet("Loans")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_all_ledger_cached():
    """Get all ledger entries as DataFrame with caching"""
    ws = get_worksheet("Ledger")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

def add_party(party_data):
    """Add a new party record"""
    ws = get_worksheet("Parties")
    new_id = get_next_id(ws)
    
    row = [
        new_id,
        party_data.get('name', ''),
        party_data.get('guardian_name', ''),
        str(party_data.get('dob', '')),
        party_data.get('mobile', ''),
        party_data.get('whatsapp', ''),
        party_data.get('address', ''),
        party_data.get('pincode', ''),
        party_data.get('pan_masked', ''),
        party_data.get('occupation', ''),
        party_data.get('qualification', ''),
        party_data.get('kyc_status', 'Pending'),
        str(datetime.now().date())
    ]
    
    ws.append_row(row)
    # Clear cache after adding
    get_all_parties_cached.clear()
    return new_id

def update_party(party_id, updated_data):
    """Update party record"""
    ws = get_worksheet("Parties")
    try:
        cell = ws.find(str(party_id), in_column=1)
        if cell:
            row_num = cell.row
            
            column_map = {
                'name': 2, 'guardian_name': 3, 'dob': 4, 'mobile': 5,
                'whatsapp': 6, 'address': 7, 'pincode': 8, 'pan_masked': 9,
                'occupation': 10, 'qualification': 11, 'kyc_status': 12
            }
            
            for key, value in updated_data.items():
                if key in column_map:
                    ws.update_cell(row_num, column_map[key], str(value))
            
            # Clear cache after updating
            get_all_parties_cached.clear()
            return True
    except:
        pass
    return False

def delete_party(party_id):
    """Delete party record"""
    ws = get_worksheet("Parties")
    try:
        cell = ws.find(str(party_id), in_column=1)
        if cell:
            ws.delete_rows(cell.row)
            # Clear cache after deleting
            get_all_parties_cached.clear()
            return True
    except:
        pass
    return False

def add_loan(loan_data):
    """Add new loan record"""
    ws = get_worksheet("Loans")
    new_id = get_next_id(ws)
    
    row = [
        new_id,
        loan_data.get('party_id', ''),
        loan_data.get('party_name', ''),
        loan_data.get('principal', 0),
        loan_data.get('interest_rate', 0),
        loan_data.get('duration_months', 0),
        loan_data.get('emi', 0),
        loan_data.get('processing_fee', 0),
        loan_data.get('admin_fee', 0),
        loan_data.get('documentation_fee', 0),
        loan_data.get('net_disbursed', 0),
        loan_data.get('interest_amount', 0),
        loan_data.get('total_payable', 0),
        loan_data.get('gold_description', ''),
        loan_data.get('items_count', 0),
        loan_data.get('gross_weight', 0),
        loan_data.get('net_weight', 0),
        loan_data.get('purity_karat', 0),
        loan_data.get('appraised_value', 0),
        loan_data.get('vault_id', ''),
        loan_data.get('gold_image_base64', ''),
        'Active',
        str(datetime.now().date()),
        str(datetime.now().date())
    ]
    
    ws.append_row(row)
    # Clear caches
    get_all_loans_cached.clear()
    return new_id

def update_loan_status(loan_id, status):
    """Update loan status"""
    ws = get_worksheet("Loans")
    try:
        cell = ws.find(str(loan_id), in_column=1)
        if cell:
            ws.update_cell(cell.row, 22, status)
            # Clear cache
            get_all_loans_cached.clear()
            return True
    except:
        pass
    return False

def add_ledger_entry(entry_data):
    """Add ledger transaction"""
    ws = get_worksheet("Ledger")
    new_id = get_next_id(ws)
    
    row = [
        new_id,
        entry_data.get('loan_id', ''),
        entry_data.get('transaction_type', ''),
        entry_data.get('amount', 0),
        str(entry_data.get('transaction_date', datetime.now().date())),
        str(datetime.now().date())
    ]
    
    ws.append_row(row)
    # Clear cache
    get_all_ledger_cached.clear()
    return new_id

def get_party_by_id(party_id):
    """Get specific party by ID"""
    df = get_all_parties_cached()
    if not df.empty:
        result = df[df['id'].astype(str) == str(party_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None

def get_loan_by_id(loan_id):
    """Get specific loan by ID"""
    df = get_all_loans_cached()
    if not df.empty:
        result = df[df['id'].astype(str) == str(loan_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None

def get_ledger_for_loan(loan_id):
    """Get ledger for specific loan"""
    df = get_all_ledger_cached()
    if not df.empty:
        result = df[df['loan_id'].astype(str) == str(loan_id)]
        return result
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
parties_df = get_all_parties_cached()
loans_df = get_all_loans_cached()
ledger_df = get_all_ledger_cached()

count_parties = len(parties_df) if not parties_df.empty else 0
count_loans = len(loans_df) if not loans_df.empty else 0
count_gold = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
count_tx = len(ledger_df) if not ledger_df.empty else 0

# Helper function to generate agreement HTML
def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row.get('gold_image_base64') and str(loan_row['gold_image_base64']).strip():
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

# [Rest of your modules remain the same - Dashboard, Party Master, Edit/Delete, 
# Gold Loan Management, Gold Pledge, Loan Agreement, EMI Schedule, Data Management]

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    if not loans_df.empty:
        active_loans = loans_df[loans_df['status'] == 'Active']
        total_active_loans = len(active_loans)
        total_disbursed = pd.to_numeric(loans_df['principal'], errors='coerce').sum()
        total_gold_wt = pd.to_numeric(active_loans['net_weight'], errors='coerce').sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Loan Accounts", total_active_loans)
        col2.metric("Total Disbursement", f"₹{total_disbursed:,.2f}")
        col3.metric("Total Gold Vaulted", f"{total_gold_wt:.2f} g")
        
        st.subheader("📈 Portfolio Overview")
        if not parties_df.empty:
            merged_df = loans_df.merge(parties_df[['id', 'name']], left_on='party_id', right_on='id', how='left')
            dashboard_df = merged_df[['id_x', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']]
            dashboard_df.columns = ['Loan ID', 'Customer', 'Principal', 'Interest', 'Total Payable', 'EMI', 'Status']
            st.dataframe(dashboard_df, use_container_width=True)
    else:
        st.info("No loan data available yet.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#8B6508;'>© 2024 AuraLoan - Gold Loan Management System</p>", unsafe_allow_html=True)
