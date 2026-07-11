import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import time
import json
import os

# ==========================================
# 1. GOOGLE SHEETS CONNECTION WITH FALLBACK
# ==========================================

# Try to import GSheetsConnection, fallback to CSV if not available
try:
    from st_gsheets_connection import GSheetsConnection
    GSHEETS_AVAILABLE = True
    st.info("✅ Google Sheets connection available")
except ImportError:
    GSHEETS_AVAILABLE = False
    st.warning("⚠️ Google Sheets not available. Using CSV fallback.")

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
# 2. CSV FALLBACK SYSTEM (for when Google Sheets fails)
# ==========================================

def load_csv_data(filename, columns):
    """Load data from CSV file"""
    try:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df
        else:
            return pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return pd.DataFrame(columns=columns)

def save_csv_data(filename, df):
    """Save data to CSV file"""
    try:
        # Create backups directory
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        # Save to main file
        df.to_csv(filename, index=False)
        
        # Also save a backup
        backup_filename = f"backups/{filename.replace('.csv', '')}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(backup_filename, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")
        return False

# ==========================================
# 3. GOOGLE SHEETS HELPERS
# ==========================================

def get_sheets_connection():
    """Get connection to Google Sheets with retry logic"""
    if not GSHEETS_AVAILABLE:
        return None
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            return conn
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"Failed to connect to Google Sheets after {max_retries} attempts: {e}")
                return None
    return None

def create_sheet_if_not_exists(conn, sheet_name, columns):
    """Create a sheet with proper columns if it doesn't exist"""
    try:
        # Try to read the sheet
        df = conn.read(worksheet=sheet_name, ttl=0)
        
        # If sheet exists but is empty or missing columns, recreate it
        if df.empty or not all(col in df.columns for col in columns):
            df = pd.DataFrame(columns=columns)
            conn.update(worksheet=sheet_name, data=df)
            return df
        return df
    except Exception as e:
        # Sheet doesn't exist, create it
        try:
            df = pd.DataFrame(columns=columns)
            conn.update(worksheet=sheet_name, data=df)
            return df
        except Exception as create_error:
            st.error(f"Failed to create sheet '{sheet_name}': {create_error}")
            return pd.DataFrame(columns=columns)

def init_sheets():
    """Initialize all sheets with proper columns"""
    if not GSHEETS_AVAILABLE:
        return False
    
    conn = get_sheets_connection()
    if conn is None:
        return False
    
    try:
        create_sheet_if_not_exists(conn, "parties", PARTIES_COLUMNS)
        create_sheet_if_not_exists(conn, "loans", LOANS_COLUMNS)
        create_sheet_if_not_exists(conn, "ledger", LEDGER_COLUMNS)
        return True
    except Exception as e:
        st.error(f"Error initializing sheets: {e}")
        return False

# ==========================================
# 4. DATA OPERATIONS (with Google Sheets or CSV fallback)
# ==========================================

def get_data_from_sheets_or_csv(sheet_name, columns, csv_filename):
    """Get data from Google Sheets or fallback to CSV"""
    if GSHEETS_AVAILABLE:
        try:
            conn = get_sheets_connection()
            if conn is not None:
                df = conn.read(worksheet=sheet_name, ttl=0)
                # Ensure all columns exist
                for col in columns:
                    if col not in df.columns:
                        df[col] = None
                
                # Convert id to int
                if 'id' in df.columns:
                    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
                
                # Cache in session state
                cache_key = f"{sheet_name}_cache"
                st.session_state[cache_key] = df
                
                # Also save as CSV backup
                save_csv_data(csv_filename, df)
                
                return df
        except Exception as e:
            st.warning(f"Google Sheets error for {sheet_name}: {e}. Using CSV fallback.")
    
    # Fallback to CSV
    return load_csv_data(csv_filename, columns)

def update_sheet_or_csv(sheet_name, data, csv_filename):
    """Update Google Sheets or fallback to CSV"""
    if GSHEETS_AVAILABLE:
        try:
            conn = get_sheets_connection()
            if conn is not None:
                conn.update(worksheet=sheet_name, data=data)
                
                # Clear cache after update
                cache_key = f"{sheet_name}_cache"
                if cache_key in st.session_state:
                    del st.session_state[cache_key]
                
                # Save as CSV backup
                save_csv_data(csv_filename, data)
                return True
        except Exception as e:
            st.warning(f"Google Sheets update error for {sheet_name}: {e}. Using CSV fallback.")
    
    # Fallback to CSV
    return save_csv_data(csv_filename, data)

# ==========================================
# 5. DATA ACCESS FUNCTIONS
# ==========================================

def get_parties(force_reload=False):
    """Get all parties"""
    cache_key = 'parties_cache'
    
    if not force_reload and cache_key in st.session_state and st.session_state[cache_key] is not None:
        return st.session_state[cache_key]
    
    df = get_data_from_sheets_or_csv("parties", PARTIES_COLUMNS, "parties.csv")
    st.session_state[cache_key] = df
    return df

def get_loans(force_reload=False):
    """Get all loans"""
    cache_key = 'loans_cache'
    
    if not force_reload and cache_key in st.session_state and st.session_state[cache_key] is not None:
        return st.session_state[cache_key]
    
    df = get_data_from_sheets_or_csv("loans", LOANS_COLUMNS, "loans.csv")
    st.session_state[cache_key] = df
    return df

def get_ledger(force_reload=False):
    """Get all ledger entries"""
    cache_key = 'ledger_cache'
    
    if not force_reload and cache_key in st.session_state and st.session_state[cache_key] is not None:
        return st.session_state[cache_key]
    
    df = get_data_from_sheets_or_csv("ledger", LEDGER_COLUMNS, "ledger.csv")
    st.session_state[cache_key] = df
    return df

def get_next_id(df, id_column='id'):
    """Get next available ID safely"""
    if df.empty or id_column not in df.columns:
        return 1
    try:
        max_id = df[id_column].max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    except:
        return 1

def add_party(data):
    """Add new party"""
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
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df['id'] = df['id'].astype(int)
    
    if update_sheet_or_csv("parties", df, "parties.csv"):
        st.session_state.pop('parties_cache', None)
        return new_id
    return None

def add_loan(data):
    """Add new loan"""
    df = get_loans(force_reload=True)
    new_id = get_next_id(df)
    
    new_row = {
        'id': new_id,
        'party_id': data.get('party_id', 0),
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
    
    if update_sheet_or_csv("loans", df, "loans.csv"):
        # Add to ledger
        add_ledger_entry({
            'loan_id': new_id,
            'transaction_type': 'Disbursement',
            'amount': float(data.get('principal', 0)),
            'transaction_date': str(datetime.now().date())
        })
        st.session_state.pop('loans_cache', None)
        return new_id
    return None

def add_ledger_entry(data):
    """Add ledger entry"""
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
    
    if update_sheet_or_csv("ledger", df, "ledger.csv"):
        st.session_state.pop('ledger_cache', None)
        return new_id
    return None

def update_party(party_id, data):
    """Update party"""
    df = get_parties(force_reload=True)
    mask = df['id'] == party_id
    if not mask.any():
        return False
    
    for key, value in data.items():
        if key in df.columns:
            df.loc[mask, key] = value
    
    if update_sheet_or_csv("parties", df, "parties.csv"):
        st.session_state.pop('parties_cache', None)
        return True
    return False

def delete_party(party_id):
    """Delete party"""
    df = get_parties(force_reload=True)
    df = df[df['id'] != party_id]
    
    if update_sheet_or_csv("parties", df, "parties.csv"):
        st.session_state.pop('parties_cache', None)
        return True
    return False

def update_loan_status(loan_id, status):
    """Update loan status"""
    df = get_loans(force_reload=True)
    mask = df['id'] == loan_id
    if not mask.any():
        return False
    
    df.loc[mask, 'status'] = status
    
    if update_sheet_or_csv("loans", df, "loans.csv"):
        st.session_state.pop('loans_cache', None)
        return True
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
# 6. HTML GENERATORS
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
# 7. INITIALIZATION
# ==========================================

# Initialize session state for caching
if 'parties_cache' not in st.session_state:
    st.session_state['parties_cache'] = None
if 'loans_cache' not in st.session_state:
    st.session_state['loans_cache'] = None
if 'ledger_cache' not in st.session_state:
    st.session_state['ledger_cache'] = None
if 'init_done' not in st.session_state:
    st.session_state['init_done'] = False

# Initialize sheets (if Google Sheets available)
if not st.session_state['init_done'] and GSHEETS_AVAILABLE:
    with st.spinner("Initializing Google Sheets connection..."):
        if init_sheets():
            st.session_state['init_done'] = True
else:
    st.session_state['init_done'] = True

# ==========================================
# 8. STREAMLIT UI
# ==========================================

st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

# Custom Styles
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

# Get system stats
def get_system_stats():
    try:
        df_parties = get_parties()
        df_loans = get_loans()
        df_ledger = get_ledger()
        
        count_parties = len(df_parties) if not df_parties.empty else 0
        count_loans = len(df_loans) if not df_loans.empty else 0
        count_gold = len(df_loans[df_loans['status'] == 'Active']) if not df_loans.empty and 'status' in df_loans.columns else 0
        count_tx = len(df_ledger) if not df_ledger.empty else 0
        
        return count_parties, count_loans, count_gold, count_tx
    except Exception as e:
        return 0, 0, 0, 0

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

# Show persistence status
if GSHEETS_AVAILABLE:
    try:
        conn = get_sheets_connection()
        if conn is not None:
            st.sidebar.success("✅ Google Sheets: Connected")
        else:
            st.sidebar.warning("⚠️ Google Sheets: Not Connected (Using CSV fallback)")
    except:
        st.sidebar.warning("⚠️ Google Sheets: Not Connected (Using CSV fallback)")
else:
    st.sidebar.info("ℹ️ Using CSV Storage (Google Sheets not available)")

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# 9. MODULES
# ==========================================

if choice == "🔄 Force Reload":
    st.header("🔄 Force Reload Data")
    st.warning("⚠️ This will clear all cached data and reload from source")
    
    if st.button("🔄 Force Reload All Data", use_container_width=True):
        force_reload_all()

elif choice == "💾 Backup & Restore":
    st.header("💾 Backup & Restore System")
    
    tab1, tab2 = st.tabs(["📤 Create Backup", "📥 Restore Backup"])
    
    with tab1:
        st.subheader("Create Manual Backup")
        if st.button("📤 Create Backup of All Data", use_container_width=True):
            with st.spinner("Creating backup..."):
                df_parties = get_parties(force_reload=True)
                df_loans = get_loans(force_reload=True)
                df_ledger = get_ledger(force_reload=True)
                
                if save_csv_data("parties_backup.csv", df_parties):
                    st.success("✅ Parties backup created")
                if save_csv_data("loans_backup.csv", df_loans):
                    st.success("✅ Loans backup created")
                if save_csv_data("ledger_backup.csv", df_ledger):
                    st.success("✅ Ledger backup created")
    
    with tab2:
        st.subheader("Restore from Backup")
        st.warning("⚠️ This will restore data from the last backup!")
        
        if st.button("📥 Restore All Data from Backup", use_container_width=True):
            # Restore from backups
            df_parties = load_csv_data("parties_backup.csv", PARTIES_COLUMNS)
            df_loans = load_csv_data("loans_backup.csv", LOANS_COLUMNS)
            df_ledger = load_csv_data("ledger_backup.csv", LEDGER_COLUMNS)
            
            if not df_parties.empty:
                update_sheet_or_csv("parties", df_parties, "parties.csv")
                st.success("✅ Parties restored")
            if not df_loans.empty:
                update_sheet_or_csv("loans", df_loans, "loans.csv")
                st.success("✅ Loans restored")
            if not df_ledger.empty:
                update_sheet_or_csv("ledger", df_ledger, "ledger.csv")
                st.success("✅ Ledger restored")
            
            force_reload_all()

elif choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    df_parties = get_parties()
    df_loans = get_loans()
    
    if not df_parties.empty and not df_loans.empty:
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
        st.info("No data available yet. Start by adding customers and loans.")

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

elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core (Edit / Delete Customer Accounts)")
    
    df_parties = get_parties()
    
    if df_parties.empty:
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
            
            # Check if customer has active loans
            df_loans = get_loans()
            has_active_loans = len(df_loans[(df_loans['party_id'] == party_to_edit) & (df_loans['status'] == 'Active')]) > 0
            
            if has_active_loans:
                st.error("❌ Cannot delete: This customer has active loans. Close the loans first.")
            else:
                confirm_delete_text = st.text_input("Type 'DELETE' to confirm action:")
                if st.button("Confirm Account Destruction"):
                    if confirm_delete_text == "DELETE":
                        if delete_party(party_to_edit):
                            st.success("✅ Customer profile deleted successfully.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete. Please try again.")
                    else:
                        st.error("Confirmation string does not match.")

# Continue with other modules...
# [Gold Loan Management, Pledge Management, etc. follow the same pattern]

# ==========================================
# 10. GOLD LOAN MANAGEMENT
# ==========================================

elif choice == "💰 Gold Loan Management":
    conn = None  # Not using SQLite anymore
    
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation (Disbursement = Principal)")
        
        df_parties = get_parties()
        df_verified = df_parties[df_parties['kyc_status'] == 'Verified']
        
        if df_verified.empty:
            st.warning("⚠️ No Verified Customers Available. Please verify a profile inside Party Management first.")
        else:
            party_options = {row['id']: row['name'] for _, row in df_verified.iterrows()}
            
            with st.form("disbursement_calculator_form"):
                selected_party = st.selectbox("Select Verified Borrower Profile", list(party_options.keys()), 
                                            format_func=lambda x: party_options[x])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💎 Gold Details")
                    gold_description = st.text_input("Description", placeholder="മാല, വളകൾ, മോതിരം")
                    items_count = st.number_input("Count", min_value=1, value=1, step=1)
                    gross_wt = st.number_input("Gross Weight (grams)", min_value=0.0, step=0.1)
                    net_wt = st.number_input("Net Weight (grams)", min_value=0.0, step=0.1)
                    purity = st.selectbox("Purity Karat", [24, 22, 20, 18], index=1)
                    appraised_val = st.number_input("Appraisal Value (₹)", min_value=0.0)
                    vault_id = st.text_input("Vault Storage ID Code")
                    
                    st.markdown("---")
                    st.markdown("📷 **Attach Gold Photo**")
                    gold_photo_data = st.file_uploader("Choose image", type=["jpg", "png", "jpeg"])
                    
                with col2:
                    st.markdown("#### 📊 Calculation Terms")
                    max_eligible = appraised_val * 0.75
                    st.info(f"Regulatory 75% LTV Cap Limit: **₹{max_eligible:,.2f}**")
                    
                    principal = st.number_input("Disbursement Amount (₹)", min_value=0.0, value=40375.0)
                    interest_rate = st.number_input("Interest Rate %", min_value=0.0, value=12.0)
                    duration = st.number_input("Tenure (Months)", min_value=1, max_value=36, value=12)
                    
                    st.markdown("---")
                    st.markdown("#### 🏷️ Service Fees")
                    processing_fee = st.number_input("Processing Fee (₹)", min_value=0.0, value=500.0)
                    admin_fee = st.number_input("Admin Fee (₹)", min_value=0.0, value=200.0)
                    doc_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, value=200.0)
                    
                    interest_amount = principal * (interest_rate / 100)
                    total_payable = principal + interest_amount
                    calculated_emi = total_payable / duration if duration > 0 else 0.0
                    
                    st.markdown("---")
                    st.write(f"**Disbursement Amount:** ₹{principal:,.2f}")
                    st.write(f"**Interest Amount:** ₹{interest_amount:,.2f}")
                    st.write(f"**Total Payable:** ₹{total_payable:,.2f}")
                    st.write(f"**EMI:** ₹{calculated_emi:,.2f}")
                    
                if st.form_submit_button("Finalize and Disburse"):
                    if principal > max_eligible:
                        st.error("Requested capital allocation exceeds the 75% LTV limit.")
                    elif principal <= 0 or net_wt <= 0:
                        st.error("Invalid entry constraints.")
                    else:
                        base64_image_str = ""
                        if gold_photo_data is not None:
                            bytes_data = gold_photo_data.read()
                            base64_image_str = base64.b64encode(bytes_data).decode("utf-8")
                        
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
                            'gross_weight': gross_wt,
                            'net_weight': net_wt,
                            'purity_karat': purity,
                            'appraised_value': appraised_val,
                            'vault_id': vault_id,
                            'gold_image_base64': base64_image_str
                        }
                        
                        new_loan_id = add_loan(loan_data)
                        if new_loan_id:
                            st.success(f"✅ Loan Account #{new_loan_id} successfully created.")
                            st.session_state['active_contract_loan_id'] = new_loan_id
                            st.rerun()
                        else:
                            st.error("❌ Failed to create loan. Please try again.")
            
            if 'active_contract_loan_id' in st.session_state:
                l_id = st.session_state['active_contract_loan_id']
                df_loans = get_loans()
                loan_row = df_loans[df_loans['id'] == l_id]
                
                if not loan_row.empty:
                    loan_row = loan_row.iloc[0]
                    df_parties = get_parties()
                    party_row = df_parties[df_parties['id'] == loan_row['party_id']].iloc[0]
                    
                    tab_voucher, tab_fee_receipt = st.tabs(["📄 Agreement Form", "🖨️ Fee Receipt"])
                    
                    with tab_voucher:
                        instant_html = generate_agreement_html(loan_row, party_row)
                        st.download_button(label="📥 Download Agreement", data=instant_html, 
                                         file_name=f"Agreement_Loan_{l_id}.html", mime="text/html")
                    
                    with tab_fee_receipt:
                        fee_html = generate_fee_receipt_html(loan_row, party_row)
                        st.download_button(label="📥 Download Fee Receipt", data=fee_html, 
                                         file_name=f"Fee_Receipt_Loan_{l_id}.html", mime="text/html")
    
    elif sub_choice == "📊 Party Ledger":
        st.header("📊 Customer Ledger Statements")
        
        df_loans = get_loans()
        df_active = df_loans[df_loans['status'] == 'Active']
        
        if df_active.empty:
            st.info("No active loan records open currently.")
        else:
            df_parties = get_parties()
            df_active = df_active.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
            
            loan_options = {row['id_x']: f"Loan #{row['id_x']} - Holder: {row['name']} (₹{row['principal']})" 
                          for _, row in df_active.iterrows()}
            selected_loan = st.selectbox("Select Target Portfolio File", list(loan_options.keys()), 
                                       format_func=lambda x: loan_options[x])
            
            loan_row = df_loans[df_loans['id'] == selected_loan].iloc[0]
            total_liability = float(loan_row['total_payable'] or 0.0)
            
            df_ledger = get_ledger()
            df_loan_ledger = df_ledger[df_ledger['loan_id'] == selected_loan]
            total_repaid_credits = df_loan_ledger[df_loan_ledger['transaction_type'].isin(['Repayment', 'Interest Settlement'])]['amount'].sum()
            total_repaid_credits = float(total_repaid_credits or 0.0)
            live_outstanding_balance = max(0.0, total_liability - total_repaid_credits)
            
            tab_post, tab_view, tab_print = st.tabs(["💳 Collection Repayment", "📑 View Ledger", "🖨️ Printable Sheet"])
            
            with tab_post:
                if live_outstanding_balance <= 0.0:
                    st.success("🎉 Already Repaid / Bill completely paid in full.")
                else:
                    with st.form("repayment_ledger_post_form"):
                        repay_amt = st.number_input("Repayment Collected (₹)", min_value=0.0, 
                                                   max_value=live_outstanding_balance, step=100.0)
                        repay_date = st.date_input("Settlement Date")
                        type_tx = st.selectbox("Allocation Type", ["Repayment", "Interest Settlement"])
                        
                        if st.form_submit_button("Post Entry"):
                            if repay_amt > 0:
                                add_ledger_entry({
                                    'loan_id': selected_loan,
                                    'transaction_type': type_tx,
                                    'amount': repay_amt,
                                    'transaction_date': str(repay_date)
                                })
                                
                                if repay_amt >= live_outstanding_balance:
                                    update_loan_status(selected_loan, 'Closed')
                                
                                st.success("✅ Repayment entry saved!")
                                st.rerun()
            
            with tab_view:
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Disbursement Amount", f"₹{loan_row['principal']:,.2f}")
                col_m2.metric("Total Payable", f"₹{total_liability:,.2f}")
                col_m3.metric("Outstanding Balance", f"₹{live_outstanding_balance:,.2f}")
                
                if not df_loan_ledger.empty:
                    st.table(df_loan_ledger[['transaction_type', 'amount', 'transaction_date']])
                else:
                    st.info("No transactions yet.")

# ==========================================
# 11. OTHER MODULES (Placeholders)
# ==========================================

elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory Vault Details")
    
    df_loans = get_loans()
    df_active = df_loans[df_loans['status'] == 'Active']
    
    if df_active.empty:
        st.info("No vaulted items found.")
    else:
        df_parties = get_parties()
        df_display = df_active.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
        
        for _, row in df_display.iterrows():
            with st.container():
                col_text, col_img = st.columns([2, 1])
                with col_text:
                    st.markdown(f"### 📦 Loan #{row['id_x']}")
                    st.write(f"👤 **Owner:** {row['name']}")
                    st.write(f"📝 **Description:** {row.get('gold_description', 'N/A')}")
                    st.write(f"🔢 **Count:** {row.get('items_count', 0)} Nos | ⚖️ **Weight:** {row.get('net_weight', 0)}g")
                    st.write(f"🔒 **Vault ID:** `{row.get('vault_id', 'N/A')}`")
                with col_img:
                    if row.get('gold_image_base64') and pd.notna(row['gold_image_base64']):
                        img_bytes = base64.b64decode(row['gold_image_base64'])
                        st.image(img_bytes, caption="Pledged Gold Asset", width=180)
                st.markdown("---")

elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement Console")
    
    df_loans = get_loans()
    if df_loans.empty:
        st.info("No loan files available.")
    else:
        df_parties = get_parties()
        df_merged = df_loans.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
        
        contract_options = {row['id_x']: f"Loan #{row['id_x']} - {row['name']}" for _, row in df_merged.iterrows()}
        target_contract = st.selectbox("Select Target Portfolio File", list(contract_options.keys()), 
                                     format_func=lambda x: contract_options[x])
        
        loan_row = df_loans[df_loans['id'] == target_contract].iloc[0]
        party_row = df_parties[df_parties['id'] == loan_row['party_id']].iloc[0]
        
        tab_contract_view, tab_receipt_view = st.tabs(["📜 Agreement Form", "🧾 Fee Receipt"])
        
        with tab_contract_view:
            agreement_html = generate_agreement_html(loan_row, party_row)
            st.download_button(label="📥 Download Agreement HTML", data=agreement_html, 
                             file_name=f"Agreement_Loan_{loan_row['id']}.html", mime="text/html")
        
        with tab_receipt_view:
            fee_html = generate_fee_receipt_html(loan_row, party_row)
            st.download_button(label="📥 Download Fee Receipt HTML", data=fee_html, 
                             file_name=f"Fee_Receipt_Loan_{loan_row['id']}.html", mime="text/html")

elif choice == "📅 EMI Schedule":
    st.header("📅 Monthly Recovery Projection Mapping (EMI Schedule)")
    
    df_loans = get_loans()
    df_active = df_loans[df_loans['status'] == 'Active']
    
    if df_active.empty:
        st.info("No active loan tracking matrices found.")
    else:
        df_parties = get_parties()
        df_active = df_active.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
        
        loan_options = {row['id_x']: f"Loan #{row['id_x']} - {row['name']} (EMI: ₹{row['emi']:,.2f})" 
                       for _, row in df_active.iterrows()}
        selected_sched = st.selectbox("Select Target Loan ID Schedule Map", list(loan_options.keys()), 
                                     format_func=lambda x: loan_options[x])
        
        loan_row = df_loans[df_loans['id'] == selected_sched].iloc[0]
        party_row = df_parties[df_parties['id'] == loan_row['party_id']].iloc[0]
        
        schedule_list = []
        remaining = loan_row['total_payable']
        
        for month in range(1, loan_row['duration_months'] + 1):
            remaining -= loan_row['emi']
            current_rem = max(0.0, remaining)
            display_rem = "Already Repaid" if current_rem < 0.01 else f"₹{current_rem:,.2f}"
            
            schedule_list.append({
                "Installment": f"Month {month}",
                "Payment Amount (₹)": f"₹{loan_row['emi']:,.2f}",
                "Outstanding Balance": display_rem
            })
        
        st.table(pd.DataFrame(schedule_list))








