import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import time

# ==========================================
# 1. GOOGLE SHEETS CONNECTION
# ==========================================

try:
    from st_gsheets_connection import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    st.error("Please install: pip install streamlit-gsheets-connection")

# Define column structures
PARTIES_COLUMNS = [
    'id', 'name', 'guardian_name', 'dob', 'mobile', 'whatsapp',
    'address', 'pincode', 'pan_masked', 'occupation', 'qualification',
    'kyc_status', 'created_at'
]

LOANS_COLUMNS = [
    'id', 'party_id', 'principal', 'interest_rate', 'duration_months',
    'emi', 'processing_fee', 'admin_fee', 'documentation_fee',
    'net_disbursed', 'interest_amount', 'total_payable',
    'gold_description', 'items_count', 'gross_weight', 'net_weight',
    'purity_karat', 'appraised_value', 'vault_id', 'gold_image_base64',
    'status', 'disbursed_date'
]

LEDGER_COLUMNS = [
    'id', 'loan_id', 'transaction_type', 'amount', 'transaction_date'
]

# ==========================================
# 2. GOOGLE SHEETS OPERATIONS
# ==========================================

def get_connection():
    """Get Google Sheets connection"""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def create_sheet_with_columns(conn, sheet_name, columns):
    """Create a sheet with proper columns"""
    try:
        # Try to read existing sheet
        df = conn.read(worksheet=sheet_name, ttl=0)
        
        # If sheet exists but has wrong columns, update it
        if not df.empty:
            # Check if all columns exist
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                for col in missing_cols:
                    df[col] = None
                conn.update(worksheet=sheet_name, data=df)
                st.info(f"✅ Updated {sheet_name} with missing columns")
            return df
        
        # Sheet is empty, create with columns
        df = pd.DataFrame(columns=columns)
        conn.update(worksheet=sheet_name, data=df)
        st.info(f"✅ Created {sheet_name} with {len(columns)} columns")
        return df
        
    except Exception as e:
        # Sheet doesn't exist, create it
        try:
            df = pd.DataFrame(columns=columns)
            conn.update(worksheet=sheet_name, data=df)
            st.info(f"✅ Created new sheet: {sheet_name}")
            return df
        except Exception as create_error:
            st.error(f"Failed to create {sheet_name}: {create_error}")
            return pd.DataFrame(columns=columns)

def init_sheets():
    """Initialize all sheets with proper columns"""
    conn = get_connection()
    if conn is None:
        st.error("❌ Could not connect to Google Sheets")
        return False
    
    try:
        # Create each sheet with proper columns
        create_sheet_with_columns(conn, "parties", PARTIES_COLUMNS)
        create_sheet_with_columns(conn, "loans", LOANS_COLUMNS)
        create_sheet_with_columns(conn, "ledger", LEDGER_COLUMNS)
        return True
    except Exception as e:
        st.error(f"Error initializing sheets: {e}")
        return False

# ==========================================
# 3. DATA ACCESS FUNCTIONS
# ==========================================

def get_parties(force_reload=False):
    """Get all parties"""
    cache_key = 'parties_cache'
    
    if not force_reload and cache_key in st.session_state:
        return st.session_state[cache_key]
    
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(columns=PARTIES_COLUMNS)
    
    try:
        df = conn.read(worksheet="parties", ttl=0)
        
        # If empty, create with columns
        if df.empty:
            df = pd.DataFrame(columns=PARTIES_COLUMNS)
        else:
            # Ensure all columns exist
            for col in PARTIES_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            
            # Convert id to int
            if 'id' in df.columns:
                df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        st.session_state[cache_key] = df
        return df
    except Exception as e:
        st.error(f"Error reading parties: {e}")
        return pd.DataFrame(columns=PARTIES_COLUMNS)

def get_loans(force_reload=False):
    """Get all loans"""
    cache_key = 'loans_cache'
    
    if not force_reload and cache_key in st.session_state:
        return st.session_state[cache_key]
    
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(columns=LOANS_COLUMNS)
    
    try:
        df = conn.read(worksheet="loans", ttl=0)
        
        if df.empty:
            df = pd.DataFrame(columns=LOANS_COLUMNS)
        else:
            for col in LOANS_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            
            if 'id' in df.columns:
                df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        st.session_state[cache_key] = df
        return df
    except Exception as e:
        st.error(f"Error reading loans: {e}")
        return pd.DataFrame(columns=LOANS_COLUMNS)

def get_ledger(force_reload=False):
    """Get all ledger entries"""
    cache_key = 'ledger_cache'
    
    if not force_reload and cache_key in st.session_state:
        return st.session_state[cache_key]
    
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(columns=LEDGER_COLUMNS)
    
    try:
        df = conn.read(worksheet="ledger", ttl=0)
        
        if df.empty:
            df = pd.DataFrame(columns=LEDGER_COLUMNS)
        else:
            for col in LEDGER_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            
            if 'id' in df.columns:
                df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        st.session_state[cache_key] = df
        return df
    except Exception as e:
        st.error(f"Error reading ledger: {e}")
        return pd.DataFrame(columns=LEDGER_COLUMNS)

def update_sheet(sheet_name, data):
    """Update a sheet in Google Sheets"""
    conn = get_connection()
    if conn is None:
        return False
    
    try:
        conn.update(worksheet=sheet_name, data=data)
        
        # Clear cache
        cache_key = f"{sheet_name}_cache"
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        
        return True
    except Exception as e:
        st.error(f"Error updating {sheet_name}: {e}")
        return False

def get_next_id(df, id_column='id'):
    """Get next available ID"""
    if df is None or df.empty or id_column not in df.columns:
        return 1
    try:
        max_id = df[id_column].max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    except:
        return 1

# ==========================================
# 4. DATA MANIPULATION FUNCTIONS
# ==========================================

def add_party(data):
    """Add new party"""
    try:
        df = get_parties(force_reload=True)
        new_id = get_next_id(df)
        
        new_row = {
            'id': new_id,
            'name': data.get('name', ''),
            'guardian_name': data.get('guardian_name', ''),
            'dob': str(data.get('dob', '')),
            'mobile': data.get('mobile', ''),
            'whatsapp': data.get('whatsapp', ''),
            'address': data.get('address', ''),
            'pincode': data.get('pincode', ''),
            'pan_masked': data.get('pan_masked', ''),
            'occupation': data.get('occupation', ''),
            'qualification': data.get('qualification', ''),
            'kyc_status': data.get('kyc_status', 'Pending'),
            'created_at': str(datetime.now().date())
        }
        
        # Add row
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df['id'] = df['id'].astype(int)
        
        if update_sheet("parties", df):
            return new_id
        return None
    except Exception as e:
        st.error(f"Error adding party: {e}")
        return None

def add_loan(data):
    """Add new loan"""
    try:
        df = get_loans(force_reload=True)
        new_id = get_next_id(df)
        
        new_row = {
            'id': new_id,
            'party_id': int(data.get('party_id', 0)),
            'principal': float(data.get('principal', 0)),
            'interest_rate': float(data.get('interest_rate', 0)),
            'duration_months': int(data.get('duration_months', 0)),
            'emi': float(data.get('emi', 0)),
            'processing_fee': float(data.get('processing_fee', 0)),
            'admin_fee': float(data.get('admin_fee', 0)),
            'documentation_fee': float(data.get('documentation_fee', 0)),
            'net_disbursed': float(data.get('principal', 0)),
            'interest_amount': float(data.get('interest_amount', 0)),
            'total_payable': float(data.get('total_payable', 0)),
            'gold_description': data.get('gold_description', ''),
            'items_count': int(data.get('items_count', 0)),
            'gross_weight': float(data.get('gross_weight', 0)),
            'net_weight': float(data.get('net_weight', 0)),
            'purity_karat': int(data.get('purity_karat', 22)),
            'appraised_value': float(data.get('appraised_value', 0)),
            'vault_id': data.get('vault_id', ''),
            'gold_image_base64': data.get('gold_image_base64', ''),
            'status': 'Active',
            'disbursed_date': str(datetime.now().date())
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df['id'] = df['id'].astype(int)
        
        if update_sheet("loans", df):
            # Add to ledger
            add_ledger_entry({
                'loan_id': new_id,
                'transaction_type': 'Disbursement',
                'amount': float(data.get('principal', 0)),
                'transaction_date': str(datetime.now().date())
            })
            return new_id
        return None
    except Exception as e:
        st.error(f"Error adding loan: {e}")
        return None

def add_ledger_entry(data):
    """Add ledger entry"""
    try:
        df = get_ledger(force_reload=True)
        new_id = get_next_id(df)
        
        new_row = {
            'id': new_id,
            'loan_id': int(data.get('loan_id', 0)),
            'transaction_type': data.get('transaction_type', ''),
            'amount': float(data.get('amount', 0)),
            'transaction_date': data.get('transaction_date', str(datetime.now().date()))
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df['id'] = df['id'].astype(int)
        
        if update_sheet("ledger", df):
            return new_id
        return None
    except Exception as e:
        st.error(f"Error adding ledger entry: {e}")
        return None

def update_party(party_id, data):
    """Update party"""
    try:
        df = get_parties(force_reload=True)
        if df.empty:
            return False
        
        mask = df['id'] == party_id
        if not mask.any():
            return False
        
        for key, value in data.items():
            if key in df.columns:
                df.loc[mask, key] = value
        
        return update_sheet("parties", df)
    except Exception as e:
        st.error(f"Error updating party: {e}")
        return False

def delete_party(party_id):
    """Delete party"""
    try:
        df = get_parties(force_reload=True)
        if df.empty:
            return False
        
        df = df[df['id'] != party_id]
        return update_sheet("parties", df)
    except Exception as e:
        st.error(f"Error deleting party: {e}")
        return False

def update_loan_status(loan_id, status):
    """Update loan status"""
    try:
        df = get_loans(force_reload=True)
        if df.empty:
            return False
        
        mask = df['id'] == loan_id
        if not mask.any():
            return False
        
        df.loc[mask, 'status'] = status
        return update_sheet("loans", df)
    except Exception as e:
        st.error(f"Error updating loan status: {e}")
        return False

def force_reload_all():
    """Force reload all data"""
    st.session_state.pop('parties_cache', None)
    st.session_state.pop('loans_cache', None)
    st.session_state.pop('ledger_cache', None)
    
    get_parties(force_reload=True)
    get_loans(force_reload=True)
    get_ledger(force_reload=True)
    
    st.success("✅ All data reloaded successfully!")
    st.rerun()

# ==========================================
# 5. HTML GENERATORS (Keep from previous)
# ==========================================

def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row.get('gold_image_base64') and pd.notna(loan_row['gold_image_base64']):
        image_html_tag = f"""
        <div style="margin-top:20px; margin-bottom:20px; text-align:center;">
            <p><b>പണയം വെച്ച ആഭരണത്തിന്റെ ഫോട്ടോ (Pledged Asset Photo):</b></p>
            <img src="data:image/jpeg;base64,{loan_row['gold_image_base64']}" style="max-width:320px; max-height:240px; border:3px solid #b8860b; border-radius:8px;"/>
        </div>
        """
    else:
        image_html_tag = "<p style='color:grey; font-style:italic; text-align:center;'>ചിത്രം ലഭ്യമല്ല (No photo attached)</p>"

    return f"""
    <div style="border:2px solid #b8860b; padding:30px; background-color:#fcfcf4; border-radius:10px; font-family:'Inter', sans-serif; color:#333; line-height:1.7;">
        <h2 style="color:#8B6508; font-weight:bold; text-align:center; margin-bottom:20px;">സ്വർണ്ണപ്പണയ വായ്പാ കരാർ പത്രം (Gold Loan Agreement)</h2>
        <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}</p>
        <hr style="border-top: 1px solid #b8860b;">
        
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row['name']}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</b> {party_row.get('guardian_name', 'N/A')}</li>
            <li><b>വിലാസം (Address):</b> {party_row.get('address', 'N/A')}, {party_row.get('pincode', '')}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
            <li><b>തൊഴിൽ (Occupation):</b> {party_row.get('occupation', 'N/A')}</li>
            <li><b>യോഗ്യത (Qualification):</b> {party_row.get('qualification', 'N/A')}</li>
        </ul>

        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table style="width:100%; border-collapse:collapse; margin-top:15px; margin-bottom:15px;">
            <tr><th style="border:1px solid #b8860b; padding:10px; text-align:left;">വിവരണം (Description)</th><th style="border:1px solid #b8860b; padding:10px; text-align:left;">തുക / നിരക്ക് (Amount / Rate)</th></tr>
            <tr><td style="border:1px solid #b8860b; padding:10px;">അനുവദിച്ച വായ്പ തുക (Principal / Disbursement)</td><td style="border:1px solid #b8860b; padding:10px;"><b>₹{loan_row['principal']:,.2f}</b></td></tr>
            <tr><td style="border:1px solid #b8860b; padding:10px;">പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td style="border:1px solid #b8860b; padding:10px;">{loan_row['interest_rate']}%</td></tr>
            <tr><td style="border:1px solid #b8860b; padding:10px;">കാലാവധി (Tenure)</td><td style="border:1px solid #b8860b; padding:10px;">{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
            <tr><td style="border:1px solid #b8860b; padding:10px;">പ്രതിമാസ തവണ (EMI)</td><td style="border:1px solid #b8860b; padding:10px;"><b>₹{loan_row['emi']:,.2f}</b></td></tr>
            <tr style="font-weight:bold; background-color: #fff0f6;"><td style="border:1px solid #b8860b; padding:10px;">ആകെ പലിശ തുക (Interest Amount)</td><td style="border:1px solid #b8860b; padding:10px;">₹{loan_row['interest_amount']:,.2f}</td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td style="border:1px solid #b8860b; padding:10px;">ആകെ തിരിച്ചടയ്ക്കാനുള്ളത് (Total Payable)</td><td style="border:1px solid #b8860b; padding:10px;">₹{loan_row['total_payable']:,.2f}</td></tr>
        </table>

        <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം (Description):</b> {loan_row.get('gold_description', 'N/A')}</li>
            <li><b>ആകെ എണ്ണം (Count):</b> {loan_row.get('items_count', 0)} Nos</li>
            <li><b>ഭാരം (Weight):</b> {loan_row.get('net_weight', 0)} ഗ്രാം</li>
            <li><b>പ്യൂരിറ്റി (Purity):</b> {loan_row.get('purity_karat', 22)} Karat</li>
            <li><b>മൂല്യം (Value):</b> ₹{loan_row.get('appraised_value', 0):,.2f}</li>
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

def generate_fee_receipt_html(loan_row, party_row):
    total_fees = float(loan_row.get('processing_fee', 0)) + float(loan_row.get('admin_fee', 0)) + float(loan_row.get('documentation_fee', 0))
    return f"""
    <div style="font-family:Arial, sans-serif; padding:25px; border:1px solid #ccc; background-color:white; color:black; border-radius:5px; border:2px dashed #333; padding:20px; margin-top:15px; background-color:#fff;">
        <h2 style="text-align:center;margin-bottom:2px;color:#b8860b;">AURA LOAN MANAGEMENT SYSTEM</h2>
        <h4 style="text-align:center;margin-top:0px;color:#555;">📋 ഫീസ് അടച്ച വൗച്ചർ / FEES RECEIPT</h4>
        <hr style="border-top: 1px dashed #000;">
        <table style="width:100%; margin-bottom:15px; font-size:14px;">
            <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {party_row['name']}</td><td><b>രസീത് നമ്പർ (Receipt No):</b> #FEE-{loan_row['id']}</td></tr>
            <tr><td><b>ലോൺ ലിങ്ക് ഐഡി (Loan Ref ID):</b> #{loan_row['id']}</td><td><b>തീയതി (Date):</b> {loan_row['disbursed_date']}</td></tr>
            <tr><td><b>മൊബൈൽ (Mobile):</b> {party_row['mobile']}</td><td><b>സ്റ്റാറ്റസ് (Status):</b> <span style="color:green;font-weight:bold;">Paid</span></td></tr>
        </table>
        
        <table style="width:100%; border-collapse:collapse; margin-top:10px;">
            <thead>
                <tr style="background-color: #f9f9f9;"><th style="border:1px solid #000; padding:8px; text-align:left;">ക്രമ നമ്പർ (Sl No)</th><th style="border:1px solid #000; padding:8px; text-align:left;">ഫീസ് വിവരണം (Fee Description)</th><th style="border:1px solid #000; padding:8px; text-align:left;">ഈടാക്കിയ തുക (Amount Collected)</th></tr>
            </thead>
            <tbody>
                <tr><td style="border:1px solid #000; padding:8px; text-align:center;">1</td><td style="border:1px solid #000; padding:8px;">പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td style="border:1px solid #000; padding:8px;">₹{float(loan_row.get('processing_fee', 0)):,.2f}</td></tr>
                <tr><td style="border:1px solid #000; padding:8px; text-align:center;">2</td><td style="border:1px solid #000; padding:8px;">അഡ്മിൻ ഫീസ് (Admin Fee)</td><td style="border:1px solid #000; padding:8px;">₹{float(loan_row.get('admin_fee', 0)):,.2f}</td></tr>
                <tr><td style="border:1px solid #000; padding:8px; text-align:center;">3</td><td style="border:1px solid #000; padding:8px;">ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td style="border:1px solid #000; padding:8px;">₹{float(loan_row.get('documentation_fee', 0)):,.2f}</td></tr>
                <tr style="font-weight:bold; background-color: #f5f5f5;"><td colspan="2" style="border:1px solid #000; padding:8px; text-align:right;">ആകെ ഈടാക്കിയ ഫീസ് (Total Service Charges):</td><td style="border:1px solid #000; padding:8px;">₹{total_fees:,.2f}</td></tr>
            </tbody>
        </table>
        <br>
        <p style="font-size:13px; font-weight:bold;">തുക അക്ഷരത്തിൽ: രൂപ {total_fees:,.2f} മാത്രം.</p>
        <br>
        <table style="width:100%; margin-top:20px; font-size:14px; text-align:center;">
            <tr><td>____________________<br>ക്യാഷറുടെ ഒപ്പ് (Cashier)</td><td>____________________<br>കസ്റ്റമർ ഒപ്പ് (Customer Signature)</td></tr>
        </table>
    </div>
    """

# ==========================================
# 6. INITIALIZATION
# ==========================================

# Initialize session state
if 'parties_cache' not in st.session_state:
    st.session_state['parties_cache'] = None
if 'loans_cache' not in st.session_state:
    st.session_state['loans_cache'] = None
if 'ledger_cache' not in st.session_state:
    st.session_state['ledger_cache'] = None
if 'init_done' not in st.session_state:
    st.session_state['init_done'] = False

# Initialize Google Sheets
if not st.session_state['init_done'] and GSHEETS_AVAILABLE:
    with st.spinner("Initializing Google Sheets..."):
        if init_sheets():
            st.session_state['init_done'] = True
            st.success("✅ Google Sheets initialized successfully!")
        else:
            st.error("❌ Failed to initialize Google Sheets")

# ==========================================
# 7. SYSTEM STATS
# ==========================================

def get_system_stats():
    try:
        df_parties = get_parties()
        df_loans = get_loans()
        df_ledger = get_ledger()
        
        count_parties = len(df_parties) if df_parties is not None and not df_parties.empty else 0
        count_loans = len(df_loans) if df_loans is not None and not df_loans.empty else 0
        count_gold = len(df_loans[df_loans['status'] == 'Active']) if df_loans is not None and not df_loans.empty and 'status' in df_loans.columns else 0
        count_tx = len(df_ledger) if df_ledger is not None and not df_ledger.empty else 0
        
        return count_parties, count_loans, count_gold, count_tx
    except:
        return 0, 0, 0, 0

# ==========================================
# 8. STREAMLIT UI
# ==========================================

st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background-color: #FAF6EE !important; }
    .gold-header { color: #8B6508; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .stMetric { 
        background-color: #FFFDF7 !important; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #E3C16F !important;
        box-shadow: 0px 2px 4px rgba(227, 193, 111, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

count_parties, count_loans, count_gold, count_tx = get_system_stats()

# Sidebar
st.sidebar.markdown("### 📋 Navigation")
main_menu = [
    "🏠 Dashboard",
    "👤 Party Master",
    "✏️ Edit/Delete Party Profile",
    "💰 Gold Loan Management",
    "💍 Gold Pledge Management",
    "📄 Loan Agreement (Malayalam)",
    "📅 EMI Schedule",
    "💾 Backup & Restore",
    "🔄 Force Reload"
]
choice = st.sidebar.selectbox("Select Module", main_menu)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Sub-Modules")
if choice == "💰 Gold Loan Management":
    sub_choice = st.sidebar.radio("Sub Navigation", ["💸 Loan Disbursement", "📊 Party Ledger"])
else:
    sub_choice = None

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: **{count_parties}**")
st.sidebar.write(f"💰 Loans: **{count_loans}**")
st.sidebar.write(f"💍 Gold: **{count_gold}**")
st.sidebar.write(f"📝 Transactions: **{count_tx}**")

if GSHEETS_AVAILABLE:
    st.sidebar.success("✅ Google Sheets: Connected")
else:
    st.sidebar.error("❌ Google Sheets: Not Available")

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# 9. DASHBOARD MODULE
# ==========================================

if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    df_parties = get_parties()
    df_loans = get_loans()
    
    if df_parties is not None and not df_parties.empty and df_loans is not None and not df_loans.empty:
        total_active_loans = len(df_loans[df_loans['status'] == 'Active']) if 'status' in df_loans.columns else 0
        total_disbursed = df_loans['principal'].sum() if 'principal' in df_loans.columns else 0
        total_gold_wt = df_loans[df_loans['status'] == 'Active']['net_weight'].sum() if 'status' in df_loans.columns and 'net_weight' in df_loans.columns else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Loan Accounts", total_active_loans)
        col2.metric("Total Disbursement (Principal Amount)", f"₹{total_disbursed:,.2f}")
        col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
        
        st.subheader("📈 Live Master Monitoring Stream")
        try:
            df_merged = df_loans.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
            df_display = df_merged[['id_x', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']].copy()
            df_display.columns = ['Loan ID', 'Customer Name', 'Principal/Disbursement Amount (₹)', 
                                 'Interest Amount (₹)', 'Total Payable (₹)', 'Monthly EMI (₹)', 'Status']
            st.dataframe(df_display, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display dashboard data: {e}")
    else:
        st.info("📋 No data available yet. Start by adding customers and loans.")

# ==========================================
# 10. PARTY MASTER MODULE
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
                data = {
                    'name': name,
                    'guardian_name': guardian_name,
                    'dob': dob,
                    'mobile': mobile,
                    'whatsapp': whatsapp,
                    'address': address,
                    'pincode': pincode,
                    'pan_masked': pan,
                    'occupation': occupation,
                    'qualification': qualification,
                    'kyc_status': kyc_status
                }
                new_id = add_party(data)
                if new_id:
                    st.success(f"✅ Successfully registered: {name} (ID: {new_id})")
                    st.rerun()
                else:
                    st.error("❌ Failed to save customer. Please try again.")
            else:
                st.error("Name and Mobile fields are required.")

# ==========================================
# 11. EDIT/DELETE PARTY PROFILE MODULE
# ==========================================

elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core (Edit / Delete Customer Accounts)")
    
    df_parties = get_parties()
    
    if df_parties is None or df_parties.empty:
        st.info("No customer data available.")
    else:
        party_to_edit = st.selectbox("Select Party Profile to Manage", df_parties['id'].tolist(), 
                                   format_func=lambda x: f"ID: {x} | {df_parties[df_parties['id']==x]['name'].values[0]} ({df_parties[df_parties['id']==x]['kyc_status'].values[0]})")
        selected_row = df_parties[df_parties['id'] == party_to_edit].iloc[0]
        
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
                    edit_kyc = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"], 
                                          index=["Pending", "Verified", "Suspended"].index(selected_row['kyc_status']))
                
                if st.form_submit_button("Save All Updates"):
                    data = {
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
                    if update_party(party_to_edit, data):
                        st.success("✅ All updates saved successfully.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update. Please try again.")
        
        with tab_delete:
            st.warning(f"⚠️ Warning: You are about to permanently delete the profile of **{selected_row['name']}**.")
            
            df_loans = get_loans()
            has_active_loans = False
            if df_loans is not None and not df_loans.empty:
                has_active_loans = len(df_loans[(df_loans['party_id'] == party_to_edit) & (df_loans['status'] == 'Active')]) > 0
            
            if has_active_loans:
                st.error("❌ Cannot delete: This customer has active loans.")
            else:
                confirm_delete_text = st.text_input("Type 'DELETE' to confirm action:")
                if st.button("Confirm Account Destruction"):
                    if confirm_delete_text == "DELETE":
                        if delete_party(party_to_edit):
                            st.success("✅ Customer profile deleted successfully.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete.")
                    else:
                        st.error("Confirmation string does not match.")

# ==========================================
# 12. GOLD LOAN MANAGEMENT (Partial - Add your full code here)
# ==========================================

elif choice == "💰 Gold Loan Management":
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation")
        
        df_parties = get_parties()
        df_verified = df_parties[df_parties['kyc_status'] == 'Verified'] if df_parties is not None and not df_parties.empty else pd.DataFrame()
        
        if df_verified.empty:
            st.warning("⚠️ No Verified Customers Available.")
        else:
            party_options = {row['id']: row['name'] for _, row in df_verified.iterrows()}
            
            with st.form("disbursement_form"):
                selected_party = st.selectbox("Select Customer", list(party_options.keys()), format_func=lambda x: party_options[x])
                
                col1, col2 = st.columns(2)
                with col1:
                    gold_description = st.text_input("Gold Description")
                    items_count = st.number_input("Items Count", min_value=1, value=1)
                    net_wt = st.number_input("Net Weight (grams)", min_value=0.0, step=0.1)
                    purity = st.selectbox("Purity Karat", [24, 22, 20, 18], index=1)
                    appraised_val = st.number_input("Appraisal Value (₹)", min_value=0.0)
                
                with col2:
                    principal = st.number_input("Disbursement Amount (₹)", min_value=0.0, value=40375.0)
                    interest_rate = st.number_input("Interest Rate %", min_value=0.0, value=12.0)
                    duration = st.number_input("Tenure (Months)", min_value=1, max_value=36, value=12)
                    processing_fee = st.number_input("Processing Fee (₹)", min_value=0.0, value=500.0)
                    admin_fee = st.number_input("Admin Fee (₹)", min_value=0.0, value=200.0)
                    doc_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, value=200.0)
                    
                    interest_amount = principal * (interest_rate / 100)
                    total_payable = principal + interest_amount
                    calculated_emi = total_payable / duration if duration > 0 else 0.0
                    
                    st.write(f"**EMI:** ₹{calculated_emi:,.2f}")
                    st.write(f"**Total Payable:** ₹{total_payable:,.2f}")
                
                if st.form_submit_button("Disburse Loan"):
                    loan_data = {
                        'party_id': selected_party,
                        'principal': principal,
                        'interest_rate': interest_rate,
                        'duration_months': duration,
                        'emi': calculated_emi,
                        'processing_fee': processing_fee,
                        'admin_fee': admin_fee,
                        'documentation_fee': doc_fee,
                        'interest_amount': interest_amount,
                        'total_payable': total_payable,
                        'gold_description': gold_description,
                        'items_count': items_count,
                        'net_weight': net_wt,
                        'purity_karat': purity,
                        'appraised_value': appraised_val,
                        'vault_id': '',
                        'gold_image_base64': ''
                    }
                    
                    new_loan_id = add_loan(loan_data)
                    if new_loan_id:
                        st.success(f"✅ Loan #{new_loan_id} created!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create loan")

    elif sub_choice == "📊 Party Ledger":
        st.header("📊 Customer Ledger")
        st.info("Ledger module - Add your code here")

# ==========================================
# 13. OTHER MODULES (Add your remaining modules here)
# ==========================================

elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Management")
    st.info("Gold Pledge Management module - Add your code here")

elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Loan Agreement")
    st.info("Loan Agreement module - Add your code here")

elif choice == "📅 EMI Schedule":
    st.header("📅 EMI Schedule")
    st.info("EMI Schedule module - Add your code here")

elif choice == "💾 Backup & Restore":
    st.header("💾 Backup & Restore")
    st.info("Backup module - Add your code here")

elif choice == "🔄 Force Reload":
    st.header("🔄 Force Reload")
    if st.button("Force Reload All Data"):
        force_reload_all()




