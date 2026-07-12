import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import json

# ==========================================
# 1. CONFIGURATION
# ==========================================

# Define all columns with proper data types
PARTIES_COLUMNS = {
    'id': 'int64',
    'name': 'object',
    'guardian_name': 'object',
    'dob': 'object',
    'mobile': 'object',  # Changed to object (string) to handle large numbers
    'whatsapp': 'object',  # Changed to object (string)
    'address': 'object',
    'pincode': 'object',  # Changed to object (string)
    'pan_masked': 'object',
    'occupation': 'object',
    'qualification': 'object',
    'kyc_status': 'object',
    'created_at': 'object'
}

LOANS_COLUMNS = {
    'id': 'int64',
    'party_id': 'int64',
    'principal': 'float64',
    'interest_rate': 'float64',
    'duration_months': 'int64',
    'emi': 'float64',
    'processing_fee': 'float64',
    'admin_fee': 'float64',
    'documentation_fee': 'float64',
    'net_disbursed': 'float64',
    'interest_amount': 'float64',
    'total_payable': 'float64',
    'gold_description': 'object',
    'items_count': 'int64',
    'gross_weight': 'float64',
    'net_weight': 'float64',
    'purity_karat': 'int64',
    'appraised_value': 'float64',
    'vault_id': 'object',
    'gold_image_base64': 'object',
    'status': 'object',
    'disbursed_date': 'object'
}

LEDGER_COLUMNS = {
    'id': 'int64',
    'loan_id': 'int64',
    'transaction_type': 'object',
    'amount': 'float64',
    'transaction_date': 'object'
}

def get_column_list(columns_dict):
    """Get list of column names from dictionary"""
    return list(columns_dict.keys())

# ==========================================
# 2. CSV FILE MANAGEMENT
# ==========================================

def ensure_csv_file(filename, columns_dict):
    """Create CSV file with headers if it doesn't exist"""
    try:
        if not os.path.exists(filename):
            df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns_dict.items()})
            df.to_csv(filename, index=False)
            print(f"✅ Created {filename}")
            return True
        
        # Check if file has proper headers
        df = pd.read_csv(filename)
        columns = list(columns_dict.keys())
        
        if df.empty:
            df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns_dict.items()})
            df.to_csv(filename, index=False)
            print(f"✅ Recreated {filename} with headers")
            return True
        
        # Check if all columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            for col in missing_cols:
                df[col] = None
            df.to_csv(filename, index=False)
            print(f"✅ Added missing columns to {filename}")
        
        return True
    except Exception as e:
        print(f"Error with {filename}: {e}")
        # Recreate the file
        try:
            df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns_dict.items()})
            df.to_csv(filename, index=False)
            return True
        except:
            return False

def load_data(filename, columns_dict):
    """Load data from CSV file"""
    try:
        ensure_csv_file(filename, columns_dict)
        df = pd.read_csv(filename)
        columns = list(columns_dict.keys())
        
        if df.empty:
            return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns_dict.items()})
        
        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # Convert data types properly
        for col, dtype in columns_dict.items():
            if col in df.columns:
                try:
                    if dtype == 'int64':
                        # Handle empty values
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
                    elif dtype == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype('float64')
                    else:
                        # For object type, convert to string and handle NaN
                        df[col] = df[col].fillna('').astype('object')
                except Exception as e:
                    print(f"Error converting {col} to {dtype}: {e}")
                    # If conversion fails, set to appropriate default
                    if dtype == 'int64':
                        df[col] = 0
                    elif dtype == 'float64':
                        df[col] = 0.0
                    else:
                        df[col] = ''
        
        return df
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns_dict.items()})

def save_data(filename, df, columns_dict):
    """Save data to CSV file"""
    try:
        # Create backups folder
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        # Ensure all columns exist
        for col in columns_dict.keys():
            if col not in df.columns:
                df[col] = None
        
        # Convert data types before saving
        for col, dtype in columns_dict.items():
            if col in df.columns:
                try:
                    if dtype == 'int64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
                    elif dtype == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype('float64')
                    else:
                        df[col] = df[col].fillna('').astype('object')
                except:
                    pass
        
        # Save main file
        df.to_csv(filename, index=False)
        
        # Save backup
        backup_name = f"backups/{filename.replace('.csv', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(backup_name, index=False)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

# ==========================================
# 3. DATA ACCESS FUNCTIONS
# ==========================================

def get_parties():
    """Get all parties"""
    if 'parties_cache' not in st.session_state:
        st.session_state['parties_cache'] = load_data("parties.csv", PARTIES_COLUMNS)
    return st.session_state['parties_cache']

def get_loans():
    """Get all loans"""
    if 'loans_cache' not in st.session_state:
        st.session_state['loans_cache'] = load_data("loans.csv", LOANS_COLUMNS)
    return st.session_state['loans_cache']

def get_ledger():
    """Get all ledger entries"""
    if 'ledger_cache' not in st.session_state:
        st.session_state['ledger_cache'] = load_data("ledger.csv", LEDGER_COLUMNS)
    return st.session_state['ledger_cache']

def get_next_id(df, id_column='id'):
    """Get next available ID"""
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
    try:
        df = get_parties()
        new_id = get_next_id(df)
        
        new_row = {
            'id': new_id,
            'name': str(data.get('name', '')),
            'guardian_name': str(data.get('guardian_name', '')),
            'dob': str(data.get('dob', '')),
            'mobile': str(data.get('mobile', '')),  # Convert to string
            'whatsapp': str(data.get('whatsapp', '')),  # Convert to string
            'address': str(data.get('address', '')),
            'pincode': str(data.get('pincode', '')),  # Convert to string
            'pan_masked': str(data.get('pan_masked', '')),
            'occupation': str(data.get('occupation', '')),
            'qualification': str(data.get('qualification', '')),
            'kyc_status': str(data.get('kyc_status', 'Pending')),
            'created_at': str(datetime.now().date())
        }
        
        # Create new row as DataFrame with proper types
        new_df = pd.DataFrame([new_row])
        for col, dtype in PARTIES_COLUMNS.items():
            if col in new_df.columns:
                try:
                    if dtype == 'int64':
                        new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0).astype('int64')
                    elif dtype == 'float64':
                        new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0.0).astype('float64')
                    else:
                        new_df[col] = new_df[col].fillna('').astype('object')
                except:
                    pass
        
        df = pd.concat([df, new_df], ignore_index=True)
        
        if save_data("parties.csv", df, PARTIES_COLUMNS):
            st.session_state['parties_cache'] = df
            return new_id
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def add_loan(data):
    """Add new loan"""
    try:
        df = get_loans()
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
            'gold_description': str(data.get('gold_description', '')),
            'items_count': int(data.get('items_count', 0)),
            'gross_weight': float(data.get('gross_weight', 0)),
            'net_weight': float(data.get('net_weight', 0)),
            'purity_karat': int(data.get('purity_karat', 22)),
            'appraised_value': float(data.get('appraised_value', 0)),
            'vault_id': str(data.get('vault_id', '')),
            'gold_image_base64': str(data.get('gold_image_base64', '')),
            'status': 'Active',
            'disbursed_date': str(datetime.now().date())
        }
        
        new_df = pd.DataFrame([new_row])
        for col, dtype in LOANS_COLUMNS.items():
            if col in new_df.columns:
                try:
                    if dtype == 'int64':
                        new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0).astype('int64')
                    elif dtype == 'float64':
                        new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0.0).astype('float64')
                    else:
                        new_df[col] = new_df[col].fillna('').astype('object')
                except:
                    pass
        
        df = pd.concat([df, new_df], ignore_index=True)
        
        if save_data("loans.csv", df, LOANS_COLUMNS):
            st.session_state['loans_cache'] = df
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
        st.error(f"Error: {e}")
        return None

def add_ledger_entry(data):
    """Add ledger entry"""
    try:
        df = get_ledger()
        new_id = get_next_id(df)
        
        new_row = {
            'id': new_id,
            'loan_id': int(data.get('loan_id', 0)),
            'transaction_type': str(data.get('transaction_type', '')),
            'amount': float(data.get('amount', 0)),
            'transaction_date': str(data.get('transaction_date', str(datetime.now().date())))
        }
        
        new_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_df], ignore_index=True)
        
        if save_data("ledger.csv", df, LEDGER_COLUMNS):
            st.session_state['ledger_cache'] = df
            return new_id
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def update_party(party_id, data):
    """Update party"""
    try:
        df = get_parties()
        mask = df['id'] == party_id
        if not mask.any():
            return False
        
        for key, value in data.items():
            if key in df.columns:
                # Convert all text fields to string
                if key in ['name', 'guardian_name', 'mobile', 'whatsapp', 'address', 'pincode', 'pan_masked', 'occupation', 'qualification', 'kyc_status']:
                    df.loc[mask, key] = str(value)
                else:
                    df.loc[mask, key] = value
        
        if save_data("parties.csv", df, PARTIES_COLUMNS):
            st.session_state['parties_cache'] = df
            return True
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_party(party_id):
    """Delete party"""
    try:
        df = get_parties()
        df = df[df['id'] != party_id]
        
        if save_data("parties.csv", df, PARTIES_COLUMNS):
            st.session_state['parties_cache'] = df
            return True
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def update_loan_status(loan_id, status):
    """Update loan status"""
    try:
        df = get_loans()
        mask = df['id'] == loan_id
        if not mask.any():
            return False
        
        df.loc[mask, 'status'] = str(status)
        
        if save_data("loans.csv", df, LOANS_COLUMNS):
            st.session_state['loans_cache'] = df
            return True
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def force_reload():
    """Force reload all data"""
    st.session_state['parties_cache'] = load_data("parties.csv", PARTIES_COLUMNS)
    st.session_state['loans_cache'] = load_data("loans.csv", LOANS_COLUMNS)
    st.session_state['ledger_cache'] = load_data("ledger.csv", LEDGER_COLUMNS)
    st.success("✅ All data reloaded!")
    st.rerun()

# ==========================================
# 4. HTML GENERATORS
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
# 5. INITIALIZE ALL CSV FILES
# ==========================================

# Create all CSV files with proper headers
ensure_csv_file("parties.csv", PARTIES_COLUMNS)
ensure_csv_file("loans.csv", LOANS_COLUMNS)
ensure_csv_file("ledger.csv", LEDGER_COLUMNS)

# Load data into cache
if 'parties_cache' not in st.session_state:
    st.session_state['parties_cache'] = load_data("parties.csv", PARTIES_COLUMNS)
if 'loans_cache' not in st.session_state:
    st.session_state['loans_cache'] = load_data("loans.csv", LOANS_COLUMNS)
if 'ledger_cache' not in st.session_state:
    st.session_state['ledger_cache'] = load_data("ledger.csv", LEDGER_COLUMNS)

# ==========================================
# 6. SYSTEM STATS
# ==========================================

def get_stats():
    parties = get_parties()
    loans = get_loans()
    ledger = get_ledger()
    
    return {
        'parties': len(parties),
        'loans': len(loans),
        'active_loans': len(loans[loans['status'] == 'Active']) if not loans.empty and 'status' in loans.columns else 0,
        'transactions': len(ledger)
    }

# ==========================================
# 7. STREAMLIT UI
# ==========================================

st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

# Custom CSS
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

stats = get_stats()

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
st.sidebar.write(f"👤 Parties: **{stats['parties']}**")
st.sidebar.write(f"💰 Loans: **{stats['loans']}**")
st.sidebar.write(f"💍 Active Loans: **{stats['active_loans']}**")
st.sidebar.write(f"📝 Transactions: **{stats['transactions']}**")

st.sidebar.info("📁 Data saved locally in CSV files")

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# 8. DASHBOARD
# ==========================================

if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    df_parties = get_parties()
    df_loans = get_loans()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(df_parties))
    col2.metric("Total Loans", len(df_loans))
    col3.metric("Active Loans", len(df_loans[df_loans['status'] == 'Active']) if not df_loans.empty and 'status' in df_loans.columns else 0)
    
    if not df_parties.empty:
        st.subheader("📋 Recent Customers")
        st.dataframe(df_parties[['id', 'name', 'mobile', 'kyc_status', 'created_at']].tail(5), use_container_width=True)
    else:
        st.info("No customers yet. Go to 'Party Master' to add your first customer!")

# ==========================================
# 9. PARTY MASTER
# ==========================================

elif choice == "👤 Party Master":
    st.header("👤 Customer Registration (Party Master)")
    
    with st.form("add_party_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            guardian_name = st.text_input("Father/Husband Name")
            dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now())
            mobile = st.text_input("Mobile Number *")
            whatsapp = st.text_input("WhatsApp Number")
        with col2:
            occupation = st.text_input("Occupation")
            qualification = st.text_input("Qualification")
            address = st.text_area("Address")
            pincode = st.text_input("Pincode")
            pan = st.text_input("PAN Card Number")
            kyc_status = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"])
        
        submitted = st.form_submit_button("Save Customer")
        if submitted:
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
                    st.success(f"✅ Customer '{name}' added successfully! (ID: {new_id})")
                    st.rerun()
                else:
                    st.error("❌ Failed to save customer. Please try again.")
            else:
                st.error("Name and Mobile are required!")
    
    st.markdown("---")
    st.subheader("📋 Existing Customers")
    df_parties = get_parties()
    if not df_parties.empty:
        st.dataframe(df_parties[['id', 'name', 'mobile', 'kyc_status', 'created_at']], use_container_width=True)
    else:
        st.info("No customers added yet.")

# ==========================================
# 10. EDIT/DELETE PARTY PROFILE
# ==========================================

elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Edit / Delete Customer Profile")
    
    df_parties = get_parties()
    
    if df_parties.empty:
        st.info("No customers to edit.")
    else:
        party_id = st.selectbox("Select Customer", df_parties['id'].tolist(), 
                               format_func=lambda x: f"ID: {x} - {df_parties[df_parties['id']==x]['name'].values[0]}")
        
        if party_id:
            row = df_parties[df_parties['id'] == party_id].iloc[0]
            
            tab1, tab2 = st.tabs(["✏️ Edit", "🗑️ Delete"])
            
            with tab1:
                with st.form("edit_party_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Name", value=row['name'])
                        edit_guardian = st.text_input("Father/Husband Name", value=row.get('guardian_name', ''))
                        edit_mobile = st.text_input("Mobile", value=str(row['mobile']))  # Convert to string
                        edit_whatsapp = st.text_input("WhatsApp", value=str(row.get('whatsapp', '')))  # Convert to string
                    with col2:
                        edit_occupation = st.text_input("Occupation", value=row.get('occupation', ''))
                        edit_qualification = st.text_input("Qualification", value=row.get('qualification', ''))
                        edit_address = st.text_area("Address", value=row.get('address', ''))
                        edit_pincode = st.text_input("Pincode", value=str(row.get('pincode', '')))  # Convert to string
                        edit_kyc = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"], 
                                               index=["Pending", "Verified", "Suspended"].index(row['kyc_status']))
                    
                    if st.form_submit_button("Update Customer"):
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
                        if update_party(party_id, data):
                            st.success("✅ Customer updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update customer.")
            
            with tab2:
                st.warning(f"⚠️ Delete customer: {row['name']}")
                
                # Check if customer has active loans
                df_loans = get_loans()
                has_active = False
                if not df_loans.empty:
                    has_active = len(df_loans[(df_loans['party_id'] == party_id) & (df_loans['status'] == 'Active')]) > 0
                
                if has_active:
                    st.error("❌ Cannot delete: Customer has active loans!")
                else:
                    confirm = st.text_input("Type 'DELETE' to confirm:")
                    if st.button("Delete Permanently"):
                        if confirm == "DELETE":
                            if delete_party(party_id):
                                st.success("✅ Customer deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete.")
                        else:
                            st.error("Type 'DELETE' to confirm.")

# ==========================================
# 11. GOLD LOAN MANAGEMENT - DISBURSEMENT
# ==========================================

elif choice == "💰 Gold Loan Management":
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Disbursement")
        
        df_parties = get_parties()
        df_verified = df_parties[df_parties['kyc_status'] == 'Verified'] if not df_parties.empty else pd.DataFrame()
        
        if df_verified.empty:
            st.warning("⚠️ No verified customers. Please verify a customer first in Party Master.")
        else:
            with st.form("disbursement_form"):
                party_id = st.selectbox("Select Customer", df_verified['id'].tolist(),
                                       format_func=lambda x: f"{df_verified[df_verified['id']==x]['name'].values[0]} (ID: {x})")
                
                col1, col2 = st.columns(2)
                with col1:
                    gold_desc = st.text_input("Gold Description", placeholder="Eg: Necklace, Rings")
                    items = st.number_input("Number of Items", min_value=1, value=1)
                    net_weight = st.number_input("Net Weight (grams)", min_value=0.0, step=0.1)
                    purity = st.selectbox("Purity (Karat)", [24, 22, 20, 18], index=1)
                    appraised = st.number_input("Appraised Value (₹)", min_value=0.0)
                with col2:
                    principal = st.number_input("Disbursement Amount (₹)", min_value=0.0, value=40375.0)
                    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=12.0)
                    duration = st.number_input("Tenure (Months)", min_value=1, max_value=36, value=12)
                    processing = st.number_input("Processing Fee (₹)", min_value=0.0, value=500.0)
                    admin = st.number_input("Admin Fee (₹)", min_value=0.0, value=200.0)
                    doc_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, value=200.0)
                
                # Calculations
                interest_amount = principal * (interest_rate / 100)
                total_payable = principal + interest_amount
                emi = total_payable / duration if duration > 0 else 0
                
                st.info(f"**EMI:** ₹{emi:,.2f} | **Total Payable:** ₹{total_payable:,.2f} | **Interest:** ₹{interest_amount:,.2f}")
                
                if st.form_submit_button("Disburse Loan"):
                    if principal <= 0 or net_weight <= 0:
                        st.error("Principal and Weight must be greater than 0!")
                    else:
                        loan_data = {
                            'party_id': party_id,
                            'principal': principal,
                            'interest_rate': interest_rate,
                            'duration_months': duration,
                            'emi': emi,
                            'processing_fee': processing,
                            'admin_fee': admin,
                            'documentation_fee': doc_fee,
                            'interest_amount': interest_amount,
                            'total_payable': total_payable,
                            'gold_description': gold_desc,
                            'items_count': items,
                            'net_weight': net_weight,
                            'purity_karat': purity,
                            'appraised_value': appraised,
                            'vault_id': '',
                            'gold_image_base64': ''
                        }
                        new_id = add_loan(loan_data)
                        if new_id:
                            st.success(f"✅ Loan #{new_id} disbursed successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to disburse loan.")

# ==========================================
# 12. OTHER MODULES (Short versions)
# ==========================================

elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory")
    df_loans = get_loans()
    df_active = df_loans[df_loans['status'] == 'Active'] if not df_loans.empty and 'status' in df_loans.columns else pd.DataFrame()
    
    if df_active.empty:
        st.info("No active pledges.")
    else:
        df_parties = get_parties()
        df_display = df_active.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
        for _, row in df_display.iterrows():
            st.write(f"**Loan #{row['id_x']}** - {row['name']} - {row.get('gold_description', 'N/A')} - {row.get('net_weight', 0)}g")

elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Loan Agreement")
    df_loans = get_loans()
    if df_loans.empty:
        st.info("No loans found.")
    else:
        df_parties = get_parties()
        df_merged = df_loans.merge(df_parties[['id', 'name']], left_on='party_id', right_on='id', how='left')
        loan_id = st.selectbox("Select Loan", df_merged['id_x'].tolist(),
                              format_func=lambda x: f"Loan #{x} - {df_merged[df_merged['id_x']==x]['name'].values[0]}")
        if loan_id:
            loan_row = df_loans[df_loans['id'] == loan_id].iloc[0]
            party_row = df_parties[df_parties['id'] == loan_row['party_id']].iloc[0]
            html = generate_agreement_html(loan_row, party_row)
            st.download_button("Download Agreement", html, f"Agreement_{loan_id}.html", "text/html")

elif choice == "📅 EMI Schedule":
    st.header("📅 EMI Schedule")
    df_loans = get_loans()
    df_active = df_loans[df_loans['status'] == 'Active'] if not df_loans.empty and 'status' in df_loans.columns else pd.DataFrame()
    
    if df_active.empty:
        st.info("No active loans.")
    else:
        loan_id = st.selectbox("Select Loan", df_active['id'].tolist())
        if loan_id:
            row = df_active[df_active['id'] == loan_id].iloc[0]
            schedule = []
            remaining = row['total_payable']
            for i in range(1, row['duration_months'] + 1):
                remaining -= row['emi']
                schedule.append({
                    "Month": i,
                    "EMI": f"₹{row['emi']:,.2f}",
                    "Balance": f"₹{max(0, remaining):,.2f}"
                })
            st.table(pd.DataFrame(schedule))

elif choice == "💾 Backup & Restore":
    st.header("💾 Backup & Restore")
    if st.button("📤 Create Backup"):
        df_p = get_parties()
        df_l = get_loans()
        df_led = get_ledger()
        save_data("backup_parties.csv", df_p, PARTIES_COLUMNS)
        save_data("backup_loans.csv", df_l, LOANS_COLUMNS)
        save_data("backup_ledger.csv", df_led, LEDGER_COLUMNS)
        st.success("✅ Backup created!")
    
    if st.button("📥 Restore from Backup"):
        if os.path.exists("backup_parties.csv"):
            df_p = load_data("backup_parties.csv", PARTIES_COLUMNS)
            df_l = load_data("backup_loans.csv", LOANS_COLUMNS)
            df_led = load_data("backup_ledger.csv", LEDGER_COLUMNS)
            save_data("parties.csv", df_p, PARTIES_COLUMNS)
            save_data("loans.csv", df_l, LOANS_COLUMNS)
            save_data("ledger.csv", df_led, LEDGER_COLUMNS)
            force_reload()
            st.success("✅ Restored from backup!")
        else:
            st.warning("No backup found!")

elif choice == "🔄 Force Reload":
    st.header("🔄 Force Reload")
    if st.button("Reload All Data"):
        force_reload()



