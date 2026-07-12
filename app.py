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
        # Create new worksheet
        worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="30")
        # Initialize with headers
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
        if len(data) <= 1:  # Only header or empty
            return 1
        
        # Get all values from id column (first column)
        ids = []
        for row in data[1:]:  # Skip header
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

# Initialize sheets
try:
    init_sheets()
except Exception as e:
    st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
    st.stop()

# ==========================================
# 2. DATABASE OPERATIONS
# ==========================================
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
    return new_id

def update_loan_status(loan_id, status):
    """Update loan status"""
    ws = get_worksheet("Loans")
    try:
        cell = ws.find(str(loan_id), in_column=1)
        if cell:
            ws.update_cell(cell.row, 22, status)  # Column 22 is 'status'
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
    return new_id

def get_all_parties():
    """Get all parties as DataFrame"""
    ws = get_worksheet("Parties")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

def get_all_loans():
    """Get all loans as DataFrame"""
    ws = get_worksheet("Loans")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

def get_all_ledger():
    """Get all ledger entries as DataFrame"""
    ws = get_worksheet("Ledger")
    try:
        data = ws.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame(columns=data[0] if data else [])
    except:
        return pd.DataFrame()

def get_ledger_for_loan(loan_id):
    """Get ledger for specific loan"""
    df = get_all_ledger()
    if not df.empty:
        result = df[df['loan_id'].astype(str) == str(loan_id)]
        return result
    return pd.DataFrame()

def get_party_by_id(party_id):
    """Get specific party by ID"""
    df = get_all_parties()
    if not df.empty:
        result = df[df['id'].astype(str) == str(party_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None

def get_loan_by_id(loan_id):
    """Get specific loan by ID"""
    df = get_all_loans()
    if not df.empty:
        result = df[df['id'].astype(str) == str(loan_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None

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
ledger_df = get_all_ledger()

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

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    loans_df = get_all_loans()
    parties_df = get_all_parties()
    
    if not loans_df.empty:
        active_loans = loans_df[loans_df['status'] == 'Active']
        total_active_loans = len(active_loans)
        total_disbursed = pd.to_numeric(loans_df['principal'], errors='coerce').sum()
        total_gold_wt = pd.to_numeric(active_loans['net_weight'], errors='coerce').sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Loan Accounts", total_active_loans)
        col2.metric("Total Disbursement (Principal Amount)", f"₹{total_disbursed:,.2f}")
        col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
        
        st.subheader("📈 Live Master Monitoring Stream")
        if not loans_df.empty and not parties_df.empty:
            merged_df = loans_df.merge(parties_df[['id', 'name']], left_on='party_id', right_on='id', how='left', suffixes=('_loan', '_party'))
            dashboard_df = merged_df[['id_loan', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']]
            dashboard_df.columns = ['Loan ID', 'Customer Name', 'Principal (₹)', 'Interest (₹)', 'Total Payable (₹)', 'Monthly EMI (₹)', 'Status']
            st.dataframe(dashboard_df, use_container_width=True)
    else:
        st.info("No loan data available yet.")

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
                party_data = {
                    'name': name,
                    'guardian_name': guardian_name,
                    'dob': str(dob),
                    'mobile': mobile,
                    'whatsapp': whatsapp,
                    'address': address,
                    'pincode': pincode,
                    'pan_masked': pan,
                    'occupation': occupation,
                    'qualification': qualification,
                    'kyc_status': kyc_status
                }
                new_id = add_party(party_data)
                st.success(f"Successfully registered: {name} (ID: {new_id})")
                st.rerun()
            else:
                st.error("Name and Mobile fields are required.")

# ==========================================
# MODULE: EDIT & DELETE PARTY DETAILS
# ==========================================
elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core (Edit / Delete Customer Accounts)")
    parties_df = get_all_parties()
    
    if parties_df.empty:
        st.info("No customer data available.")
    else:
        party_ids = parties_df['id'].tolist()
        party_names = parties_df['name'].tolist()
        
        party_to_edit = st.selectbox(
            "Select Party Profile to Manage", 
            party_ids,
            format_func=lambda x: f"ID: {x} | {parties_df[parties_df['id']==x]['name'].values[0]} ({parties_df[parties_df['id']==x]['kyc_status'].values[0]})"
        )
        
        selected_row = parties_df[parties_df['id'] == party_to_edit].iloc[0]
        
        tab_edit, tab_delete = st.tabs(["✏️ Edit Details", "❌ Delete Profile Permanently"])
        
        with tab_edit:
            with st.form("edit_party_form_main"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("പേര് (Name)", value=selected_row['name'])
                    edit_guardian = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര്", value=selected_row.get('guardian_name', ''))
                    edit_mobile = st.text_input("മൊബൈൽ നമ്പർ (Mobile)", value=selected_row['mobile'])
                    edit_whatsapp = st.text_input("WhatsApp Number", value=selected_row.get('whatsapp', ''))
                with col2:
                    edit_occupation = st.text_input("തൊഴിൽ (Occupation)", value=selected_row.get('occupation', ''))
                    edit_qualification = st.text_input("യോഗ്യത (Qualification)", value=selected_row.get('qualification', ''))
                    edit_address = st.text_area("വിലാസം (Address)", value=selected_row.get('address', ''))
                    edit_pincode = st.text_input("Pincode", value=selected_row.get('pincode', ''))
                    current_kyc = selected_row.get('kyc_status', 'Pending')
                    kyc_options = ["Pending", "Verified", "Suspended"]
                    edit_kyc = st.selectbox("KYC Status", kyc_options, index=kyc_options.index(current_kyc) if current_kyc in kyc_options else 0)
                
                if st.form_submit_button("Save All Updates"):
                    updated_data = {
                        'name': edit_name,
                        'guardian_name': edit_guardian,
                        'mobile': edit_mobile,
                        'whatsapp': edit_whatsapp,
                        'occupation': edit_occupation,
                        'qualification': edit_qualification,
                        'address': edit_address,
                        'pincode': edit_pincode,
                        'kyc_status': edit_kyc
                    }
                    if update_party(party_to_edit, updated_data):
                        st.success("All updates saved successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to update party.")
                    
        with tab_delete:
            st.warning(f"⚠️ Warning: You are about to permanently delete the profile of **{selected_row['name']}**.")
            st.error("This will delete the customer profile. Make sure there are no open loans attached to this party.")
            
            confirm_delete_text = st.text_input("Type 'DELETE' to confirm action:")
            if st.button("Confirm Account Destruction"):
                if confirm_delete_text == "DELETE":
                    loans_df = get_all_loans()
                    if not loans_df.empty:
                        has_active_loans = len(loans_df[(loans_df['party_id'].astype(str) == str(party_to_edit)) & (loans_df['status'] == 'Active')])
                    else:
                        has_active_loans = 0
                    
                    if has_active_loans > 0:
                        st.error("Cannot delete profile: This customer still has active gold loan files recorded.")
                    else:
                        if delete_party(party_to_edit):
                            st.success("Customer profile deleted from logs successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete party.")
                else:
                    st.error("Confirmation string does not match.")

# ==========================================
# PARENT MODULE: GOLD LOAN MANAGEMENT
# ==========================================
elif choice == "💰 Gold Loan Management":
    
    # 💸 SUB-MODULE 1: LOAN DISBURSEMENT MODULE
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation (Disbursement = Principal)")
        
        parties_df = get_all_parties()
        
        if parties_df.empty:
            st.warning("⚠️ No customers available. Please register a customer first.")
        else:
            verified_parties = parties_df[parties_df['kyc_status'] == 'Verified']
            
            if verified_parties.empty:
                st.warning("⚠️ No Verified Customers Available. Please verify a profile inside Party Management first.")
            else:
                party_options = dict(zip(verified_parties['id'], verified_parties['name']))
                
                with st.form("disbursement_calculator_form"):
                    selected_party = st.selectbox("Select Verified Borrower Profile", list(party_options.keys()), format_func=lambda x: f"{party_options[x]} (ID: {x})")
                    
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
                            
                            party_name = party_options[selected_party]
                            
                            loan_data = {
                                'party_id': selected_party,
                                'party_name': party_name,
                                'principal': principal,
                                'interest_rate': interest_rate,
                                'duration_months': duration,
                                'emi': calculated_emi,
                                'processing_fee': processing_fee,
                                'admin_fee': admin_fee,
                                'documentation_fee': doc_fee,
                                'net_disbursed': principal,
                                'interest_amount': interest_amount,
                                'total_payable': total_payable,
                                'gold_description': gold_description,
                                'items_count': items_count,
                                'gross_weight': gross_wt,
                                'net_weight': net_wt,
                                'purity_karat': purity,
                                'appraised_value': appraised_val,
                                'vault_id': vault_id,
                                'gold_image_base64': base64_image_str,
                                'disbursed_date': today_str
                            }
                            
                            loan_id = add_loan(loan_data)
                            
                            # Add disbursement to ledger
                            ledger_entry = {
                                'loan_id': loan_id,
                                'transaction_type': 'Disbursement',
                                'amount': principal,
                                'transaction_date': today_str
                            }
                            add_ledger_entry(ledger_entry)
                            
                            st.success(f"Loan Account #{loan_id} successfully created.")
                            st.session_state['active_contract_loan_id'] = loan_id
                            st.rerun()

                if 'active_contract_loan_id' in st.session_state:
                    l_id = st.session_state['active_contract_loan_id']
                    loan_row = get_loan_by_id(l_id)
                    if loan_row:
                        party_row = get_party_by_id(loan_row['party_id'])
                        
                        if party_row:
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
        loans_df = get_all_loans()
        
        if loans_df.empty:
            st.info("No loan records available.")
        else:
            active_loans = loans_df[loans_df['status'] == 'Active']
            
            if active_loans.empty:
                st.info("No active loan records open currently.")
            else:
                loan_options = {}
                for _, al in active_loans.iterrows():
                    loan_options[al['id']] = f"Loan #{al['id']} - Holder: {al.get('party_name', 'Unknown')} (₹{al['principal']})"
                
                selected_loan = st.selectbox("Select Target Portfolio File", list(loan_options.keys()), format_func=lambda x: loan_options[x])
                
                # Fetch loan details
                loan_row_data = get_loan_by_id(selected_loan)
                
                if loan_row_data:
                    total_liability = float(loan_row_data.get('total_payable', 0))
                    principal = float(loan_row_data.get('principal', 0))
                    
                    # Calculate repayments
                    ledger_entries = get_ledger_for_loan(selected_loan)
                    total_repaid = 0
                    if not ledger_entries.empty:
                        repayments = ledger_entries[ledger_entries['transaction_type'].isin(['Repayment', 'Interest Settlement'])]
                        total_repaid = pd.to_numeric(repayments['amount'], errors='coerce').sum()
                    
                    live_outstanding_balance = max(0, total_liability - total_repaid)
                    
                    tab_post, tab_view, tab_print = st.tabs(["💳 Collection Repayment Entry", "📑 View Balancing Ledger Statement", "🖨️ Generate Printable Sheet"])
                    
                    with tab_post:
                        if live_outstanding_balance <= 0.0:
                            st.success("🎉 Already Repaid / Bill completely paid in full.")
                        else:
                            with st.form("repayment_ledger_post_form"):
                                repay_amt = st.number_input("Repayment Collected (₹)", min_value=0.0, max_value=live_outstanding_balance, step=100.0)
                                repay_date = st.date_input("Settlement Date")
                                type_tx = st.selectbox("Allocation Type", ["Repayment", "Interest Settlement"])
                                
                                if st.form_submit_button("Post Entry"):
                                    if repay_amt > 0:
                                        ledger_entry = {
                                            'loan_id': selected_loan,
                                            'transaction_type': type_tx,
                                            'amount': repay_amt,
                                            'transaction_date': str(repay_date)
                                        }
                                        add_ledger_entry(ledger_entry)
                                        
                                        # Check if fully repaid
                                        if repay_amt >= live_outstanding_balance:
                                            update_loan_status(selected_loan, 'Closed')
                                        
                                        st.success("Repayment entry saved inside ledger.")
                                        st.rerun()
                    
                    with tab_view:
                        col_m1, col_m2, col_m3 = st.columns(3)
                        col_m1.metric("Disbursement / Principal Amount", f"₹{principal:,.2f}")
                        col_m2.metric("Total Payable (with Interest)", f"₹{total_liability:,.2f}")
                        
                        if live_outstanding_balance <= 0.0:
                            col_m3.metric("Current Outstanding Balance", "Already Repaid")
                        else:
                            col_m3.metric("Current Outstanding Balance", f"₹{live_outstanding_balance:,.2f}", delta_color="inverse")
                        
                        if not ledger_entries.empty:
                            display_df = ledger_entries[['transaction_type', 'amount', 'transaction_date']]
                            display_df.columns = ['Activity Type', 'Value (₹)', 'Date']
                            st.table(display_df)
                        else:
                            st.info("No transactions recorded yet.")
                    
                    with tab_print:
                        st.markdown("### 🖨️ Printable Ledger Statement")
                        p_loan = loan_row_data
                        p_party = get_party_by_id(p_loan['party_id'])
                        
                        tx_rows = get_ledger_for_loan(selected_loan)
                        
                        table_html_rows = ""
                        total_repaid_print = 0
                        if not tx_rows.empty:
                            for _, tx in tx_rows.iterrows():
                                display_type = "Loan Disbursement (Principal)" if tx['transaction_type'] == "Disbursement" else tx['transaction_type']
                                table_html_rows += f"<tr><td>{tx['transaction_date']}</td><td>{display_type}</td><td>₹{float(tx['amount']):,.2f}</td></tr>"
                                if tx['transaction_type'] in ['Repayment', 'Interest Settlement']:
                                    total_repaid_print += float(tx['amount'])
                        
                        balance_left = total_liability - total_repaid_print
                        
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
                                <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {p_party['name'] if p_party else 'N/A'}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{p_loan['id']}</td></tr>
                                <tr><td><b>ഫോൺ (Mobile):</b> {p_party['mobile'] if p_party else 'N/A'}</td><td><b>തീയതി (Date Issued):</b> {p_loan['disbursed_date']}</td></tr>
                                <tr><td colspan="2"><b>മേൽവിലാസം (Address):</b> {p_party.get('address', 'N/A') if p_party else 'N/A'}</td></tr>
                            </table>
                            
                            <table class="printable-table">
                                <thead>
                                    <tr><th>തീയതി (Date)</th><th>വിവരണം (Description)</th><th>തുക (Amount)</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>{p_loan['disbursed_date']}</td><td>Fixed Term Interest Charged</td><td>₹{float(p_loan['interest_amount']):,.2f}</td></tr>
                                    {table_html_rows}
                                </tbody>
                            </table>
                            
                            <div style="margin-top:20px; text-align:right; font-size:16px;">
                                <p><b>അസ്സൽ തുക (Principal/Disbursed Amount):</b> ₹{principal:,.2f}</p>
                                <p><b>ആകെ പലിശ (Total Interest Charged):</b> ₹{float(p_loan['interest_amount']):,.2f}</p>
                                <hr style="border-top: 1px solid #000; width: 40%; margin-left: auto;">
                                <p><b>ആകെ അടയ്ക്കേണ്ടത് (Total Payable):</b> ₹{total_liability:,.2f}</p>
                                <p style="color:green;"><b>ഇതുവരെ അടച്ചത് (Total Repaid):</b> ₹{total_repaid_print:,.2f}</p>
                                <p style="color:red; font-size:18px;"><b>ബാക്കി കുടിശ്ശിക (Outstanding Balance):</b> {balance_html_str}</p>
                            </div>
                        </div>
                        """
                        st.download_button(label="📥 ഡൗൺലോഡ് ലെഡ്ജർ (Download HTML Ledger)", data=printable_html, file_name=f"Ledger_Loan_{selected_loan}.html", mime="text/html")

# ==========================================
# MODULE: GOLD PLEDGE MANAGEMENT
# ==========================================
elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory Vault Details")
    loans_df = get_all_loans()
    
    if loans_df.empty:
        st.info("No vaulted items found inside database logs.")
    else:
        active_loans = loans_df[loans_df['status'] == 'Active']
        
        if active_loans.empty:
            st.info("No active gold pledges found.")
        else:
            for _, row in active_loans.iterrows():
                with st.container():
                    col_text, col_img = st.columns([2, 1])
                    with col_text:
                        st.markdown(f"### 📦 Loan Account Portfolio Reference #{row['id']}")
                        st.write(f"👤 **ഉടമസ്ഥൻ:** {row.get('party_name', 'N/A')}")
                        st.write(f"📝 **ആഭരണ വിവരണം:** {row.get('gold_description', 'N/A')}")
                        st.write(f"🔢 **എണ്ണം:** {row.get('items_count', 0)} Nos | ⚖️ **തൂക്കം:** {row.get('net_weight', 0)} ഗ്രാം")
                        st.write(f"🔒 **വോൾട്ട് സൂചിക:** `{row.get('vault_id', 'N/A')}`")
                    with col_img:
                        if row.get('gold_image_base64') and str(row['gold_image_base64']).strip():
                            try:
                                img_bytes = base64.b64decode(row['gold_image_base64'])
                                st.image(img_bytes, caption="Pledged Gold Asset", width=180)
                            except:
                                st.write("Image data corrupted")
                    st.markdown("---")

# ==========================================
# MODULE: LOAN AGREEMENT MALAYALAM
# ==========================================
elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement Console")
    loans_df = get_all_loans()
    
    if loans_df.empty:
        st.info("No loan files to fetch sheets for.")
    else:
        loan_options = {}
        for _, al in loans_df.iterrows():
            loan_options[al['id']] = f"Loan #{al['id']} Ledger Account - {al.get('party_name', 'Unknown')}"
        
        target_contract = st.selectbox("Select Target Active Portfolio File", list(loan_options.keys()), format_func=lambda x: loan_options[x])
        
        loan_row = get_loan_by_id(target_contract)
        if loan_row:
            party_row = get_party_by_id(loan_row['party_id'])
            
            if party_row:
                tab_contract_view, tab_receipt_view = st.tabs(["📜 വൗച്ചർ ഡൗൺലോഡ് (Agreement Form)", "🧾 രസീത് ഡൗൺലോഡ് (Fee Receipt)"])
                
                with tab_contract_view:
                    agreement_html = generate_agreement_html(loan_row, party_row)
                    st.download_button(label="📥 ഡൗൺലോഡ് കരാർ പത്രം (Download Agreement HTML)", data=agreement_html, file_name=f"Agreement_Loan_{loan_row['id']}.html", mime="text/html")
                    
                with tab_receipt_view:
                    fee_html = generate_fee_receipt_html(loan_row, party_row)
                    st.download_button(label="📥 ഡൗൺലോഡ് ഫീസ് രസീത് (Download Fee Receipt HTML)", data=fee_html, file_name=f"Fee_Receipt_Loan_{loan_row['id']}.html", mime="text/html")
            else:
                st.error("Party details not found.")

# ==========================================
# MODULE: EMI SCHEDULE MATRIX
# ==========================================
elif choice == "📅 EMI Schedule":
    st.header("📅 Monthly Recovery Projection Mapping (EMI Schedule)")
    loans_df = get_all_loans()
    
    if loans_df.empty:
        st.info("No active loan tracking matrices found.")
    else:
        active_loans = loans_df[loans_df['status'] == 'Active']
        
        if active_loans.empty:
            st.info("No active loans found.")
        else:
            loan_options = {}
            for _, al in active_loans.iterrows():
                loan_options[al['id']] = f"Loan #{al['id']} - Account: {al.get('party_name', 'Unknown')} (EMI: ₹{float(al['emi']):,.2f})"
            
            selected_sched = st.selectbox("Select Target Loan ID Schedule Map", list(loan_options.keys()), format_func=lambda x: loan_options[x])
            
            target_l = get_loan_by_id(selected_sched)
            
            if target_l:
                schedule_rows_html = ""
                remaining_reduction_pool = float(target_l['total_payable'])
                duration = int(target_l['duration_months'])
                emi_amount = float(target_l['emi'])
                
                schedule_list = []
                for index in range(1, duration + 1):
                    remaining_reduction_pool -= emi_amount
                    current_rem = max(0.0, remaining_reduction_pool)
                    
                    if current_rem < 0.01:
                        display_rem = "Already Repaid"
                    else:
                        display_rem = f"₹{current_rem:,.2f}"
                        
                    schedule_rows_html += f"""
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;">Month {index}</td>
                        <td style="border: 1px solid #000; padding: 8px;">₹{emi_amount:,.2f}</td>
                        <td style="border: 1px solid #000; padding: 8px;">{display_rem}</td>
                    </tr>
                    """
                    schedule_list.append({
                        "Installment": f"Month No. {index}",
                        "Payment Amount (₹)": f"₹{emi_amount:,.2f}",
                        "Outstanding Balance": display_rem
                    })
                    
                st.table(pd.DataFrame(schedule_list))
                
                party_row = get_party_by_id(target_l['party_id'])
                
                printable_schedule_html = f"""
                <div class="printable-ledger">
                    <h2 style="text-align:center;margin-bottom:2px;">AURA LOAN MANAGEMENT SYSTEM</h2>
                    <h4 style="text-align:center;margin-top:0px;color:#555;">📊 പ്രതിമാസ തവണ വിവരപ്പട്ടിക (EMI SCHEDULE PLAN)</h4>
                    <hr>
                    <table style="width:100%; margin-bottom:20px; font-size:14px;">
                        <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {target_l.get('party_name', 'N/A')}</td><td><b>ലോൺ നമ്പർ (Loan ID):</b> #{target_l['id']}</td></tr>
                        <tr><td><b>ഫോൺ (Mobile):</b> {party_row['mobile'] if party_row else 'N/A'}</td><td><b>അസ്സൽ വായ്പ (Principal/Disbursed):</b> ₹{float(target_l['principal']):,.2f}</td></tr>
                        <tr><td><b>ആകെ അടയ്ക്കേണ്ടത് (Total Liability):</b> ₹{float(target_l['total_payable']):,.2f}</td></tr>
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

# ==========================================
# MODULE: DATA MANAGEMENT
# ==========================================
elif choice == "💾 Data Management":
    st.header("💾 Data Management & Export")
    
    st.subheader("📥 Download Data as CSV")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        parties_df = get_all_parties()
        if not parties_df.empty:
            csv_parties = parties_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Parties CSV",
                data=csv_parties,
                file_name="parties_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No party data")
    
    with col2:
        loans_df = get_all_loans()
        if not loans_df.empty:
            csv_loans = loans_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Loans CSV",
                data=csv_loans,
                file_name="loans_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No loan data")
    
    with col3:
        ledger_df = get_all_ledger()
        if not ledger_df.empty:
            csv_ledger = ledger_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Ledger CSV",
                data=csv_ledger,
                file_name="ledger_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No ledger data")
    
    st.markdown("---")
    st.subheader("📊 Data Summary")
    
    if not loans_df.empty:
        st.write(f"**Total Parties:** {count_parties}")
        st.write(f"**Total Loans:** {count_loans}")
        st.write(f"**Active Loans:** {count_gold}")
        st.write(f"**Total Transactions:** {count_tx}")
        
        # Calculate totals
        total_principal = pd.to_numeric(loans_df['principal'], errors='coerce').sum()
        total_interest = pd.to_numeric(loans_df['interest_amount'], errors='coerce').sum()
        total_payable = pd.to_numeric(loans_df['total_payable'], errors='coerce').sum()
        
        st.write(f"**Total Principal Disbursed:** ₹{total_principal:,.2f}")
        st.write(f"**Total Interest Charged:** ₹{total_interest:,.2f}")
        st.write(f"**Total Amount Payable:** ₹{total_payable:,.2f}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#8B6508;'>© 2024 AuraLoan - Premium Gold Loan Management System</p>", unsafe_allow_html=True)
