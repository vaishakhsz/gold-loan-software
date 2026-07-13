import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from supabase import create_client, Client

# ==========================================
# 1. SUPABASE CONNECTION
# ==========================================
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        # Get Supabase credentials from secrets
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        return None

def get_table_data(table_name):
    """Get all data from a Supabase table"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
    
    try:
        response = supabase.table(table_name).select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading from {table_name}: {str(e)}")
        return pd.DataFrame()

def insert_record(table_name, record):
    """Insert a record into Supabase table"""
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        response = supabase.table(table_name).insert(record).execute()
        return True
    except Exception as e:
        st.error(f"Error inserting into {table_name}: {str(e)}")
        return False

def update_record(table_name, record_id, updates, id_column='id'):
    """Update a record in Supabase table"""
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        response = supabase.table(table_name).update(updates).eq(id_column, record_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating {table_name}: {str(e)}")
        return False

def delete_record(table_name, record_id, id_column='id'):
    """Delete a record from Supabase table"""
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        response = supabase.table(table_name).delete().eq(id_column, record_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting from {table_name}: {str(e)}")
        return False

# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

# Custom Styles
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF6EE !important;
    }
    .gold-header { color: #8B6508; font-weight: bold; text-align: center; margin-bottom: 20px; }
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
    .agreement-box { border: 2px solid #b8860b; padding: 30px; background-color: #fcfcf4; border-radius: 10px; font-family: 'Inter', sans-serif; color: #333; line-height: 1.7; }
    .agreement-table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }
    .agreement-table th, .agreement-table td { border: 1px solid #b8860b; padding: 10px; text-align: left; }
    .agreement-table th { background-color: #f5f0db; color: #b8860b; }
    .printable-ledger { font-family: Arial, sans-serif; padding: 25px; border: 1px solid #ccc; background-color: white; color: black; border-radius: 5px; }
    .printable-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .printable-table th, .printable-table td { border: 1px solid #000; padding: 8px; text-align: left; }
    .printable-table th { background-color: #f2f2f2; }
    .receipt-box { border: 2px dashed #333; padding: 20px; margin-top: 15px; background-color: #fff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FETCH DATA FROM SUPABASE
# ==========================================
parties_df = get_table_data('parties')
loans_df = get_table_data('loans')
ledger_df = get_table_data('ledger')

# Get counts
count_parties = len(parties_df)
count_loans = len(loans_df)
count_gold = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
count_tx = len(ledger_df)

# Helper function for agreement HTML
def generate_agreement_html(loan_row, party_row):
    image_html_tag = ""
    if loan_row.get('gold_image_base64'):
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
        <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row.get('id', 'N/A')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row.get('disbursed_date', 'N/A')}</p>
        <hr style="border-top: 1px solid #b8860b;">
        
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row.get('name', 'N/A')}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</b> {party_row.get('guardian_name', 'N/A')}</li>
            <li><b>വിലാസം (Address):</b> {party_row.get('address', 'N/A')}, {party_row.get('pincode', '')}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row.get('mobile', 'N/A')}</li>
            <li><b>തൊഴിൽ (Occupation):</b> {party_row.get('occupation', 'N/A')}</li>
            <li><b>യോഗ്യത (Qualification):</b> {party_row.get('qualification', 'N/A')}</li>
        </ul>

        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table class="agreement-table">
            <tr><th>വിവരണം (Description)</th><th>തുക / നിരക്ക് (Amount / Rate)</th></tr>
            <tr><td>അനുവദിച്ച വായ്പ തുക (Principal / Disbursement)</td><td><b>₹{float(loan_row.get('principal', 0)):,.2f}</b></td></tr>
            <tr><td>പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td>{loan_row.get('interest_rate', 0)}%</td></tr>
            <tr><td>കാലാവധി (Tenure)</td><td>{loan_row.get('duration_months', 0)} മാസങ്ങൾ</td></tr>
            <tr><td>പ്രതിമാസ തവണ (EMI)</td><td><b>₹{float(loan_row.get('emi', 0)):,.2f}</b></td></tr>
            <tr style="font-weight:bold; background-color: #fff0f6;"><td>ആകെ പലിശ തുക (Interest Amount)</td><td>₹{float(loan_row.get('interest_amount', 0)):,.2f}</td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത് (Total Payable)</td><td>₹{float(loan_row.get('total_payable', 0)):,.2f}</td></tr>
        </table>

        <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം (Description):</b> {loan_row.get('gold_description', 'N/A')}</li>
            <li><b>ആകെ എണ്ണം (Count):</b> {loan_row.get('items_count', 0)} Nos</li>
            <li><b>ഭാരം (Weight):</b> {loan_row.get('net_weight', 0)} ഗ്രാം</li>
            <li><b>പ്യൂരിറ്റി (Purity):</b> {loan_row.get('purity_karat', 0)} Karat</li>
            <li><b>മൂല്യം (Value):</b> ₹{float(loan_row.get('appraised_value', 0)):,.2f}</li>
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
    <div class="printable-ledger receipt-box">
        <h2 style="text-align:center;margin-bottom:2px;color:#b8860b;">AURA LOAN MANAGEMENT SYSTEM</h2>
        <h4 style="text-align:center;margin-top:0px;color:#555;">📋 ഫീസ് അടച്ച വൗച്ചർ / FEES RECEIPT</h4>
        <hr style="border-top: 1px dashed #000;">
        <table style="width:100%; margin-bottom:15px; font-size:14px;">
            <tr><td><b>കസ്റ്റമർ പേര് (Name):</b> {party_row.get('name', 'N/A')}</td><td><b>രസീത് നമ്പർ (Receipt No):</b> #FEE-{loan_row.get('id', 'N/A')}</td></tr>
            <tr><td><b>ലോൺ ലിങ്ക് ഐഡി (Loan Ref ID):</b> #{loan_row.get('id', 'N/A')}</td><td><b>തീയതി (Date):</b> {loan_row.get('disbursed_date', 'N/A')}</td></tr>
            <tr><td><b>മൊബൈൽ (Mobile):</b> {party_row.get('mobile', 'N/A')}</td><td><b>സ്റ്റാറ്റസ് (Status):</b> <span style="color:green;font-weight:bold;">Paid</span></td></tr>
        </table>
        
        <table class="printable-table">
            <thead>
                <tr style="background-color: #f9f9f9;"><th>ക്രമ നമ്പർ (Sl No)</th><th>ഫീസ് വിവരണം (Fee Description)</th><th>ഈടാക്കിയ തുക (Amount Collected)</th></tr>
            </thead>
            <tbody>
                <tr><td style="text-align:center;">1</td><td>പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td>₹{float(loan_row.get('processing_fee', 0)):,.2f}</td></tr>
                <tr><td style="text-align:center;">2</td><td>അഡ്മിൻ ഫീസ് (Admin Fee)</td><td>₹{float(loan_row.get('admin_fee', 0)):,.2f}</td></tr>
                <tr><td style="text-align:center;">3</td><td>ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td>₹{float(loan_row.get('documentation_fee', 0)):,.2f}</td></tr>
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
    "💾 Backup & Export"
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

st.title("🏆 AuraLoan - Premium Gold Loan System")
st.markdown("---")

# ==========================================
# 5. MODULES
# ==========================================

# DASHBOARD
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    total_active_loans = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
    total_disbursed = loans_df['principal'].astype(float).sum() if not loans_df.empty and 'principal' in loans_df.columns else 0.0
    total_gold_wt = loans_df['net_weight'].astype(float).sum() if not loans_df.empty and 'net_weight' in loans_df.columns else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Loan Accounts", total_active_loans)
    col2.metric("Total Disbursement (Principal Amount)", f"₹{total_disbursed:,.2f}")
    col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
    
    st.subheader("📈 Live Master Monitoring Stream")
    if not loans_df.empty and not parties_df.empty:
        dashboard_df = loans_df.merge(parties_df, left_on='party_id', right_on='id', how='left', suffixes=('', '_party'))
        dashboard_display = dashboard_df[['id', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']].copy()
        dashboard_display.columns = ['Loan ID', 'Customer Name', 'Principal/Disbursement Amount (₹)', 
                                    'Interest Amount (₹)', 'Total Payable (₹)', 'Monthly EMI (₹)', 'Status']
        for col in ['Principal/Disbursement Amount (₹)', 'Interest Amount (₹)', 'Total Payable (₹)', 'Monthly EMI (₹)']:
            if col in dashboard_display.columns:
                dashboard_display[col] = dashboard_display[col].astype(float).round(2)
        st.dataframe(dashboard_display, use_container_width=True)

# PARTY MASTER
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
                record = {
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
                    'kyc_status': kyc_status,
                    'created_at': str(datetime.now())
                }
                if insert_record('parties', record):
                    st.success(f"Successfully registered: {name}")
                    st.rerun()
            else:
                st.error("Name and Mobile fields are required.")

# EDIT/DELETE PARTY
elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core (Edit / Delete Customer Accounts)")
    
    if parties_df.empty:
        st.info("No customer data available.")
    else:
        party_to_edit = st.selectbox("Select Party Profile to Manage", parties_df['id'].tolist(), 
                                    format_func=lambda x: f"ID: {x} | {parties_df[parties_df['id']==x]['name'].values[0]} ({parties_df[parties_df['id']==x]['kyc_status'].values[0]})")
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
                    edit_kyc = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"], 
                                           index=["Pending", "Verified", "Suspended"].index(selected_row['kyc_status']))
                
                if st.form_submit_button("Save All Updates"):
                    updates = {
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
                    if update_record('parties', party_to_edit, updates):
                        st.success("All updates saved successfully.")
                        st.rerun()
        
        with tab_delete:
            st.warning(f"⚠️ Warning: You are about to permanently delete the profile of **{selected_row['name']}**.")
            
            # Check for active loans
            has_active_loans = not loans_df.empty and 'status' in loans_df.columns and len(loans_df[(loans_df['party_id'] == party_to_edit) & (loans_df['status'] == 'Active')]) > 0
            
            if has_active_loans:
                st.error("Cannot delete: This customer has active loans.")
            else:
                confirm_delete_text = st.text_input("Type 'DELETE' to confirm action:")
                if st.button("Confirm Account Destruction"):
                    if confirm_delete_text == "DELETE":
                        if delete_record('parties', party_to_edit):
                            st.success("Customer profile deleted successfully.")
                            st.rerun()
                    else:
                        st.error("Confirmation string does not match.")

# GOLD LOAN MANAGEMENT
elif choice == "💰 Gold Loan Management":
    
    # LOAN DISBURSEMENT
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation (Disbursement = Principal)")
        
        verified_parties = parties_df[parties_df['kyc_status'] == 'Verified'] if not parties_df.empty else pd.DataFrame()
        
        if verified_parties.empty:
            st.warning("⚠️ No Verified Customers Available.")
        else:
            party_options = {row['id']: row['name'] for _, row in verified_parties.iterrows()}
            
            with st.form("disbursement_calculator_form"):
                selected_party = st.selectbox("Select Verified Borrower Profile", list(party_options.keys()), format_func=lambda x: party_options[x])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💎 Gold Details")
                    gold_description = st.text_input("Description", placeholder="മാല, വളകൾ, മോതിരം")
                    items_count = st.number_input("Count", min_value=1, value=1, step=1)
                    gross_wt = st.number_input("Gross Weight (grams)", min_value=0.0, step=0.1)
                    net_wt = st.number_input("Net Weight (grams)", min_value=0.0, step=0.1)
                    purity = st.selectbox("Purity Karat", [24, 22, 20, 18], index=1)
                    appraised_val = st.number_input("Gold Appraisal Value (₹)", min_value=0.0)
                    vault_id = st.text_input("Vault Storage ID")
                    
                    st.markdown("---")
                    st.markdown("📷 **Attach Gold Photo**")
                    photo_source = st.radio("Photo Source", ["Upload File", "Use Camera"], horizontal=True)
                    
                    gold_photo_data = None
                    if photo_source == "Upload File":
                        gold_photo_data = st.file_uploader("Choose Gold Photo", type=["jpg", "png", "jpeg"])
                    else:
                        gold_photo_data = st.camera_input("Take Photo")
                    
                with col2:
                    st.markdown("#### 📊 Calculation Terms")
                    max_eligible = appraised_val * 0.75
                    st.info(f"75% LTV Limit: **₹{max_eligible:,.2f}**")
                    
                    principal = st.number_input("Disbursement Amount (₹)", min_value=0.0, value=40375.0)
                    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=12.0)
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
                    st.write(f"**Interest Charged:** ₹{interest_amount:,.2f}")
                    st.write(f"**Total Payable:** ₹{total_payable:,.2f}")
                    st.write(f"**Monthly EMI:** ₹{calculated_emi:,.2f}")
                    
                if st.form_submit_button("Disburse Loan"):
                    if principal > max_eligible:
                        st.error("Exceeds 75% LTV limit.")
                    elif principal <= 0 or net_wt <= 0:
                        st.error("Invalid entry constraints.")
                    else:
                        today_str = str(datetime.now().date())
                        created_at = str(datetime.now())
                        
                        base64_image_str = ""
                        if gold_photo_data is not None:
                            bytes_data = gold_photo_data.read()
                            base64_image_str = base64.b64encode(bytes_data).decode("utf-8")
                        
                        party_name = verified_parties[verified_parties['id'] == selected_party]['name'].values[0]
                        
                        loan_record = {
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
                            'status': 'Active',
                            'disbursed_date': today_str,
                            'created_at': created_at
                        }
                        
                        if insert_record('loans', loan_record):
                            # Get the loan ID
                            new_loan = get_table_data('loans')
                            new_loan_id = new_loan['id'].max() if not new_loan.empty else None
                            
                            # Add to ledger
                            if new_loan_id:
                                ledger_record = {
                                    'loan_id': new_loan_id,
                                    'transaction_type': 'Disbursement',
                                    'amount': principal,
                                    'transaction_date': today_str,
                                    'created_at': created_at
                                }
                                insert_record('ledger', ledger_record)
                                
                            st.success(f"Loan Account created successfully!")
                            st.rerun()
    
    # PARTY LEDGER
    elif sub_choice == "📊 Party Ledger":
        st.header("📊 Customer Ledger Statements")
        
        active_loans = loans_df[loans_df['status'] == 'Active'] if not loans_df.empty else pd.DataFrame()
        
        if active_loans.empty:
            st.info("No active loan records.")
        else:
            loan_options = {}
            for _, row in active_loans.iterrows():
                party_name = parties_df[parties_df['id'] == row['party_id']]['name'].values[0] if not parties_df.empty else 'Unknown'
                loan_options[row['id']] = f"Loan #{row['id']} - {party_name} (₹{float(row['principal']):,.2f})"
            
            selected_loan = st.selectbox("Select Loan", list(loan_options.keys()), format_func=lambda x: loan_options[x])
            
            loan_row = active_loans[active_loans['id'] == selected_loan].iloc[0]
            total_liability = float(loan_row['total_payable'])
            principal = float(loan_row['principal'])
            
            loan_ledger = ledger_df[ledger_df['loan_id'] == selected_loan] if not ledger_df.empty else pd.DataFrame()
            total_repaid = loan_ledger[loan_ledger['transaction_type'].isin(['Repayment', 'Interest Settlement'])]['amount'].astype(float).sum() if not loan_ledger.empty else 0.0
            outstanding = max(0.0, total_liability - total_repaid)
            
            tab_post, tab_view = st.tabs(["💳 Repayment", "📑 View Ledger"])
            
            with tab_post:
                if outstanding <= 0.0:
                    st.success("🎉 Loan fully repaid!")
                else:
                    with st.form("repayment_form"):
                        repay_amt = st.number_input("Repayment Amount (₹)", min_value=0.0, max_value=outstanding, step=100.0)
                        repay_date = st.date_input("Date")
                        type_tx = st.selectbox("Type", ["Repayment", "Interest Settlement"])
                        
                        if st.form_submit_button("Post Repayment"):
                            if repay_amt > 0:
                                ledger_record = {
                                    'loan_id': selected_loan,
                                    'transaction_type': type_tx,
                                    'amount': repay_amt,
                                    'transaction_date': str(repay_date),
                                    'created_at': str(datetime.now())
                                }
                                if insert_record('ledger', ledger_record):
                                    # Check if fully repaid
                                    new_outstanding = outstanding - repay_amt
                                    if new_outstanding <= 0.01:
                                        update_record('loans', selected_loan, {'status': 'Closed'})
                                    st.success("Repayment recorded!")
                                    st.rerun()
            
            with tab_view:
                col1, col2, col3 = st.columns(3)
                col1.metric("Principal", f"₹{principal:,.2f}")
                col2.metric("Total Payable", f"₹{total_liability:,.2f}")
                col3.metric("Outstanding", f"₹{outstanding:,.2f}")
                
                if not loan_ledger.empty:
                    display_df = loan_ledger[['transaction_type', 'amount', 'transaction_date']].copy()
                    display_df.columns = ['Type', 'Amount (₹)', 'Date']
                    display_df['Amount (₹)'] = display_df['Amount (₹)'].astype(float).round(2)
                    st.table(display_df)

# GOLD PLEDGE MANAGEMENT
elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory")
    
    active_loans = loans_df[loans_df['status'] == 'Active'] if not loans_df.empty else pd.DataFrame()
    
    if active_loans.empty:
        st.info("No vaulted items found.")
    else:
        for _, row in active_loans.iterrows():
            party_name = parties_df[parties_df['id'] == row['party_id']]['name'].values[0] if not parties_df.empty else 'Unknown'
            with st.container():
                col_text, col_img = st.columns([2, 1])
                with col_text:
                    st.markdown(f"### 📦 Loan #{row['id']}")
                    st.write(f"👤 **Owner:** {party_name}")
                    st.write(f"📝 **Item:** {row['gold_description']}")
                    st.write(f"🔢 **Count:** {row['items_count']} | ⚖️ **Weight:** {row['net_weight']}g")
                    st.write(f"🔒 **Vault:** `{row['vault_id']}`")
                with col_img:
                    if row['gold_image_base64']:
                        try:
                            img_bytes = base64.b64decode(row['gold_image_base64'])
                            st.image(img_bytes, caption="Gold Asset", width=180)
                        except:
                            pass
                st.markdown("---")

# LOAN AGREEMENT
elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement")
    
    if loans_df.empty:
        st.info("No loans found.")
    else:
        contract_options = {}
        for _, row in loans_df.iterrows():
            party_name = parties_df[parties_df['id'] == row['party_id']]['name'].values[0] if not parties_df.empty else 'Unknown'
            contract_options[row['id']] = f"Loan #{row['id']} - {party_name}"
        
        target = st.selectbox("Select Loan", list(contract_options.keys()), format_func=lambda x: contract_options[x])
        
        loan_row = loans_df[loans_df['id'] == target].iloc[0]
        party_row = parties_df[parties_df['id'] == loan_row['party_id']].iloc[0] if not parties_df.empty else None
        
        if party_row is not None:
            agreement_html = generate_agreement_html(loan_row.to_dict(), party_row.to_dict())
            st.download_button("📥 Download Agreement", data=agreement_html, file_name=f"Agreement_{target}.html", mime="text/html")
            
            fee_html = generate_fee_receipt_html(loan_row.to_dict(), party_row.to_dict())
            st.download_button("📥 Download Fee Receipt", data=fee_html, file_name=f"Fee_Receipt_{target}.html", mime="text/html")

# EMI SCHEDULE
elif choice == "📅 EMI Schedule":
    st.header("📅 EMI Schedule")
    
    active_loans = loans_df[loans_df['status'] == 'Active'] if not loans_df.empty else pd.DataFrame()
    
    if active_loans.empty:
        st.info("No active loans.")
    else:
        loan_options = {}
        for _, row in active_loans.iterrows():
            party_name = parties_df[parties_df['id'] == row['party_id']]['name'].values[0] if not parties_df.empty else 'Unknown'
            loan_options[row['id']] = f"Loan #{row['id']} - {party_name} (EMI: ₹{float(row['emi']):,.2f})"
        
        selected = st.selectbox("Select Loan", list(loan_options.keys()), format_func=lambda x: loan_options[x])
        loan_row = active_loans[active_loans['id'] == selected].iloc[0]
        
        schedule_list = []
        remaining = float(loan_row['total_payable'])
        
        for month in range(1, int(loan_row['duration_months']) + 1):
            remaining -= float(loan_row['emi'])
            current_rem = max(0.0, remaining)
            schedule_list.append({
                "Installment": f"Month {month}",
                "EMI Amount": f"₹{float(loan_row['emi']):,.2f}",
                "Balance": "₹0" if current_rem < 0.01 else f"₹{current_rem:,.2f}"
            })
        
        st.table(pd.DataFrame(schedule_list))

# BACKUP & EXPORT
elif choice == "💾 Backup & Export":
    st.header("💾 Backup & Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📤 Parties")
        if not parties_df.empty:
            st.download_button("Download Parties CSV", 
                             data=parties_df.to_csv(index=False).encode('utf-8'),
                             file_name="parties_export.csv",
                             mime="text/csv")
    
    with col2:
        st.subheader("📤 Loans")
        if not loans_df.empty:
            st.download_button("Download Loans CSV",
                             data=loans_df.to_csv(index=False).encode('utf-8'),
                             file_name="loans_export.csv",
                             mime="text/csv")
    
    with col3:
        st.subheader("📤 Ledger")
        if not ledger_df.empty:
            st.download_button("Download Ledger CSV",
                             data=ledger_df.to_csv(index=False).encode('utf-8'),
                             file_name="ledger_export.csv",
                             mime="text/csv")

