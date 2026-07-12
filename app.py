import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64

# ==========================================
# 1. SECURE GOOGLE SHEETS STORAGE CONFIGURATION
# ==========================================
SPREADSHEET_ID = "1F5u2D9AgvPOB6vS6BLABF4wwq0yj5XPQYddyKIcFSSU"

# Secure Service Account Credentials Mapping
CREDENTIALS_DICT = {
    "type": "service_account",
    "project_id": "goldloan-502122",
    "private_key_id": "9e9fa7bf45e3e09f45174081c9f31b4250c0f8d6",
    # Automatically convert the text string escaping \n into proper system breaks
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDDlKK0EiZYTpLq\nNJ3+EIlB63dADeFLvE2CXRc/zF/d6QE9BR1JdVbt79uT7rW6qHZuBF/z/v6/IDBL\nYjJybwvjM2vTC6Hr2ILBeV9hiSoJsC0zGUUaud/sTVoCgeUcs34I/M7b52aKZjmv\nw0OWGwgMmtGlE7xykZJPOjIfYQ03Qh8Qd/m7UPxplFgJ+8pQztbM6yWpw+Eqv8YF\nq/ixj26o0Z6p3bHoOgALJCb5LOlZF7i8LgE5jRTVAhVJDLplbJ8IpHgkVPUoJvpr\nS01KpgKQfoPnplr37CfGwKop/oD231jp99lsEOLSB8vwBnazTEbmnAeCxZC8ot89\ngMkb2W2ZAgMBAAECggEAUGAkIWaYFZBs9g0bpM686bdP8aYCobJIFDwXkuN1vmfE\nV4Rjjc3IJM5+6aOfUY9r5DiuCkMQBBHBZyl62+Zg90UpmbjdGWSID+TGWvoYqZSa\nbraC3MHokV8Uj5U8R/hH4n+qr1rAnD34lQ/lFaoUO8HgSDv9JQRIIYEkGhszaDJv\nUOcqNmgwplZLh43BFX3ZXwmnI+j4KKGlYo5LZxlRoMBfDXUzbmzs0hHWdNAZ5yyV\n6GKUj6wP094OM10Tg/PE4/4zg+BnPRncCoqb+DmTmfojZAnZDoEWrMumt0FnE6Id\jskrZuj0f5pWZh6Lc9oyuSDZQIL1amKJWdzKu8cgxQKBgQDg2IvvCFuLyeUvRzDr\nVfYp3dk+N/G2PshcspEpc+E+mPIDnb3Z42FI5MPdalGZkYX67yS3ZZXG8py/Cd+u\nSIXMRe3jYAcuanQHqu8ahCscNkEn3XGqAMTrPZK6eulepcRoWZYyf9rB9mWgyepb\nbzZmq38JUZGgMQP8gWkdOLTDHwKBgQDergcGjKZFjSF/OG8aX+yF/iAwQfFhtAfu\nWwtkiIamNZbuiDEO/YPGmu42RovciZni8AAzue9rdv1cPZEldm/K9Y4Q0RRTnF+R\nhS9WzRS2ZOgnEQJZ/Z/1aRjDfHn4XHFlX2n3mdi8t3y80bb+47n02CQbznszJ1VH\n7AGTdC6wRwKBgQCiaIgbLmRBwqGC1t9k/YCDmTVUFcDILO0419q2oHcwafVV21jI\ny873ghZgFm2+iTjHmnlg50WaoJ/L9evVzZinhlNgi3pkcoxBBZ0UACfLhvzlOLTj\nYQ7cBGu5uxJaRU5rOVqeO2/d7oZV78MSLHCVFIb8SijwFreUaj1s2ArpbQKBgHg1\ntD854Gy9gm6+VWQEkpfHFzNV9evLl1h6N80+0omZdnAwf2NbQi8N5jjQnqIgej2D\nWGiUIIaABsgryFZT+Ie1RcsYQ4Pbb9AL+QE/1sWb9aNZUE6qVxbRdHfbk7CanvCd\nsIPkvpcp6qG4CLTS1MkzgVKthd6YhjY8VqF2X9nzAoGADHYa8Pn0ND8N9w65o3Ji\nEhuevmqIdXkiuRXeCjPz7a1WzVeRn1r+Hy77ZjBXRusNFH6WCA6vN6i7Kf1PbM1S\ntTzrFx3BjY5K160tkpffDTHf71g1O88j0Uc9eZsZLwRpsgpey4ORjVhDFpu4Pnld\n7Q5HshnMj5ZUzSY5dqPIMjE=\n-----END PRIVATE KEY-----\n".replace('\\n', '\n'),
    "client_email": "goldloan@goldloan-502122.iam.gserviceaccount.com",
    "client_id": "118054610595093839439",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/goldloan%40goldloan-502122.iam.gserviceaccount.com"
}

def get_sheet_client():
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS_DICT, scopes)
    return gspread.authorize(creds)

def get_worksheet_df(sheet_name, fallback_headers):
    client = get_sheet_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols=str(len(fallback_headers)))
        worksheet.append_row(fallback_headers)
    
    data = worksheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=fallback_headers), worksheet
    return pd.DataFrame(data), worksheet

# Table Structures
PARTIES_HEADERS = ["id", "name", "guardian_name", "dob", "mobile", "whatsapp", "address", "pincode", "pan_masked", "occupation", "qualification", "kyc_status", "created_at"]
LOANS_HEADERS = ["id", "party_id", "principal", "interest_rate", "duration_months", "emi", "processing_fee", "admin_fee", "documentation_fee", "net_disbursed", "interest_amount", "total_payable", "gold_description", "items_count", "gross_weight", "net_weight", "purity_karat", "appraised_value", "vault_id", "gold_image_base64", "status", "disbursed_date"]
LEDGER_HEADERS = ["id", "loan_id", "transaction_type", "amount", "transaction_date"]

# Fetch Sheets
parties_df, parties_ws = get_worksheet_df("parties", PARTIES_HEADERS)
loans_df, loans_ws = get_worksheet_df("loans", LOANS_HEADERS)
ledger_df, ledger_ws = get_worksheet_df("ledger", LEDGER_HEADERS)

# ==========================================
# 2. STREAMLIT UI & STYLE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan System", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background-color: #FAF6EE !important; }
    .gold-header { color: #8B6508; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .stMetric { 
        background-color: #FFFDF7 !important; padding: 15px; border-radius: 8px; 
        border: 1px solid #E3C16F !important; box-shadow: 0px 2px 4px rgba(227, 193, 111, 0.1);
    }
    div[data-testid="stForm"] { background-color: #FFFDF9 !important; border: 1px solid #E3C16F !important; border-radius: 10px; }
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

# Metrics
count_parties = len(parties_df)
count_loans = len(loans_df)
count_gold = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
count_tx = len(ledger_df)

# ==========================================
# 3. HTML DOCUMENT GENERATORS
# ==========================================
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
        <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}</p>
        <hr style="border-top: 1px solid #b8860b;">
        <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
        <ul>
            <li><b>പേര് (Name):</b> {party_row['name']}</li>
            <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര്:</b> {party_row['guardian_name'] or 'N/A'}</li>
            <li><b>വിലാസം (Address):</b> {party_row['address'] or 'N/A'}, {party_row['pincode'] or ''}</li>
            <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
        </ul>
        <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
        <table class="agreement-table">
            <tr><th>വിവരണം</th><th>തുക / നിരക്ക്</th></tr>
            <tr><td>അനുവദിച്ച വായ്പ തുക</td><td><b>₹{float(loan_row['principal']):,.2f}</b></td></tr>
            <tr><td>പ്രതിവർഷ പലിശ നിരക്ക്</td><td>{loan_row['interest_rate']}%</td></tr>
            <tr><td>കാലാവധി</td><td>{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
            <tr><td>പ്രതിമാസ തവണ (EMI)</td><td><b>₹{float(loan_row['emi']):,.2f}</b></td></tr>
            <tr style="font-weight:bold; background-color: #f6ffed;"><td>ആകെ തിരിച്ചടയ്ക്കാനുള്ളത്</td><td>₹{float(loan_row['total_payable']):,.2f}</td></tr>
        </table>
        <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
        <ul>
            <li><b>വിവരണം:</b> {loan_row['gold_description'] or 'N/A'}</li>
            <li><b>ആകെ എണ്ണം:</b> {loan_row['items_count']} Nos</li>
            <li><b>ഭാരം:</b> {loan_row['net_weight']} ഗ്രാം</li>
            <li><b>മൂല്യം:</b> ₹{float(loan_row['appraised_value']):,.2f}</li>
            <li><b>വോൾട്ട് സൂചിക (Vault ID):</b> `{loan_row['vault_id']}`</li>
        </ul>
        {image_html_tag}
    </div>
    """

def generate_fee_receipt_html(loan_row, party_row):
    total_fees = float(loan_row['processing_fee']) + float(loan_row['admin_fee']) + float(loan_row['documentation_fee'])
    return f"""
    <div class="printable-ledger receipt-box">
        <h2 style="text-align:center;color:#b8860b;">📋 ഫീസ് അടച്ച വൗച്ചർ / FEES RECEIPT</h2>
        <table style="width:100%; font-size:14px;">
            <tr><td><b>കസ്റ്റമർ പേര്:</b> {party_row['name']}</td><td><b>രസീത് നമ്പർ:</b> #FEE-{loan_row['id']}</td></tr>
            <tr><td><b>ലോൺ ലിങ്ക് ഐഡി:</b> #{loan_row['id']}</td><td><b>തീയതി:</b> {loan_row['disbursed_date']}</td></tr>
        </table>
        <table class="printable-table">
            <tr><th>ഫീസ് വിവരണം</th><th>ഈടാക്കിയ തുക</th></tr>
            <tr><td>പ്രോസസ്സിംഗ് ഫീസ്</td><td>₹{float(loan_row['processing_fee']):,.2f}</td></tr>
            <tr><td>അഡ്മിൻ ഫീസ്</td><td>₹{float(loan_row['admin_fee']):,.2f}</td></tr>
            <tr><td>ഡോക്യുമെന്റേഷൻ ഫീസ്</td><td>₹{float(loan_row['documentation_fee']):,.2f}</td></tr>
            <tr style="font-weight:bold;"><td style="text-align:right;">ആകെ ഫീസ്:</td><td>₹{total_fees:,.2f}</td></tr>
        </table>
    </div>
    """

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("### 📋 Navigation")
main_menu = ["🏠 Dashboard", "👤 Party Master", "✏️ Edit/Delete Party Profile", "💰 Gold Loan Management", "💍 Gold Pledge Management", "📄 Loan Agreement (Malayalam)", "📅 EMI Schedule", "💾 Backup, Restore & Upload"]
choice = st.sidebar.selectbox("Select Module", main_menu)

if choice == "💰 Gold Loan Management":
    sub_choice = st.sidebar.radio("Sub Navigation", ["💸 Loan Disbursement", "📊 Party Ledger"])
else:
    sub_choice = None

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: **{count_parties}**")
st.sidebar.write(f"💰 Loans: **{count_loans}**")
st.sidebar.write(f"💍 Active Gold: **{count_gold}**")
st.sidebar.write(f"📝 Transactions: **{count_tx}**")

st.title("🏆 AuraLoan - Secure Cloud Framework")
st.markdown("---")

# ==========================================
# MODULE: DASHBOARD
# ==========================================
if choice == "🏠 Dashboard":
    st.header("📊 Executive Portfolio Dashboard")
    
    if not loans_df.empty:
        active_loans_pool = loans_df[loans_df['status'] == 'Active']
        total_active_loans = len(active_loans_pool)
        total_disbursed = pd.to_numeric(loans_df['principal']).sum()
        total_gold_wt = pd.to_numeric(active_loans_pool['net_weight']).sum()
    else:
        total_active_loans, total_disbursed, total_gold_wt = 0, 0.0, 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Loan Accounts", total_active_loans)
    col2.metric("Total Disbursement (Principal)", f"₹{total_disbursed:,.2f}")
    col3.metric("Total Gold Vaulted (Net)", f"{total_gold_wt:.2f} g")
    
    st.subheader("📈 Live Master Monitoring Stream")
    if not loans_df.empty and not parties_df.empty:
        merged = loans_df.merge(parties_df, left_on='party_id', right_on='id', suffixes=('_loan', '_party'))
        display_df = merged[['id_loan', 'name', 'principal', 'interest_amount', 'total_payable', 'emi', 'status']].rename(columns={'id_loan': 'Loan ID', 'name': 'Customer Name'})
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No logs present yet.")

# ==========================================
# MODULE: PARTY MASTER
# ==========================================
elif choice == "👤 Party Master":
    st.header("👤 Customer Registration (Party Master)")
    with st.form("party_master_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("പേര് (Name) *")
            guardian_name = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര്")
            dob = st.date_input("Date of Birth")
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
                next_id = int(parties_df['id'].max() + 1) if not parties_df.empty else 1
                row_to_append = [next_id, name, guardian_name, str(dob), mobile, whatsapp, address, pincode, pan, occupation, qualification, kyc_status, str(datetime.now().date())]
                parties_ws.append_row(row_to_append)
                st.success(f"Successfully registered: {name}")
                st.rerun()
            else:
                st.error("Name and Mobile are required.")

# ==========================================
# MODULE: EDIT & DELETE PARTY DETAILS
# ==========================================
elif choice == "✏️ Edit/Delete Party Profile":
    st.header("✏️ Profile Management Core")
    if parties_df.empty:
        st.info("No customer data available.")
    else:
        party_options = {row['id']: f"ID: {row['id']} | {row['name']}" for _, row in parties_df.iterrows()}
        party_to_edit = st.selectbox("Select Party Profile to Manage", list(party_options.keys()), format_func=lambda x: party_options[x])
        
        selected_idx = parties_df[parties_df['id'] == party_to_edit].index[0]
        selected_row = parties_df.iloc[selected_idx]
        
        tab_edit, tab_delete = st.tabs(["✏️ Edit Details", "❌ Delete Profile"])
        
        with tab_edit:
            with st.form("edit_party_form"):
                edit_name = st.text_input("പേര് (Name)", value=str(selected_row['name']))
                edit_guardian = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര്", value=str(selected_row['guardian_name']))
                edit_mobile = st.text_input("മൊബൈൽ നമ്പർ", value=str(selected_row['mobile']))
                edit_address = st.text_area("വിലാസം", value=str(selected_row['address']))
                edit_kyc = st.selectbox("KYC Status", ["Pending", "Verified", "Suspended"], index=["Pending", "Verified", "Suspended"].index(selected_row['kyc_status']))
                
                if st.form_submit_button("Save Updates"):
                    sheet_row_num = int(selected_idx) + 2
                    parties_ws.update_cell(sheet_row_num, 2, edit_name)
                    parties_ws.update_cell(sheet_row_num, 3, edit_guardian)
                    parties_ws.update_cell(sheet_row_num, 5, edit_mobile)
                    parties_ws.update_cell(sheet_row_num, 7, edit_address)
                    parties_ws.update_cell(sheet_row_num, 12, edit_kyc)
                    st.success("Updates successfully written to Google Sheets!")
                    st.rerun()
                    
        with tab_delete:
            st.error("⚠️ Permanent Destruction Safety Boundary Triggered.")
            confirm_text = st.text_input("Type 'DELETE' to confirm:")
            if st.button("Confirm Account Destruction"):
                if confirm_text == "DELETE":
                    active_loans_count = 0
                    if not loans_df.empty:
                        active_loans_count = len(loans_df[(loans_df['party_id'] == party_to_edit) & (loans_df['status'] == 'Active')])
                    
                    if active_loans_count > 0:
                        st.error("Cannot delete profile: This user profile possesses active non-repaid loans linked to it.")
                    else:
                        sheet_row_num = int(selected_idx) + 2
                        parties_ws.delete_rows(sheet_row_num)
                        st.success("Profile deleted successfully from cloud dataset.")
                        st.rerun()

# ==========================================
# MODULE: GOLD LOAN MANAGEMENT
# ==========================================
elif choice == "💰 Gold Loan Management":
    if sub_choice == "💸 Loan Disbursement":
        st.header("💸 Gold Loan Formulation")
        verified_parties = parties_df[parties_df['kyc_status'] == 'Verified']
        
        if verified_parties.empty:
            st.warning("⚠️ No Verified Customers Available.")
        else:
            party_opts = {row['id']: row['name'] for _, row in verified_parties.iterrows()}
            with st.form("disbursement_calculator_form"):
                selected_party = st.selectbox("Select Borrower Profile", list(party_opts.keys()), format_func=lambda x: party_opts[x])
                gold_description = st.text_input("ആഭരണ വിവരണം (Description)", placeholder="വളകൾ, മോതിരം")
                items_count = st.number_input("എണ്ണം (Count)", min_value=1, value=1)
                net_wt = st.number_input("Net Weight (grams)", min_value=0.0, step=0.1)
                appraised_val = st.number_input("മൂല്യം (Gold Appraisal Value - ₹)", min_value=0.0)
                vault_id = st.text_input("Vault Storage ID Code")
                
                principal = st.number_input("Principal Amount (₹)", min_value=0.0)
                interest_rate = st.number_input("Interest Rate %", min_value=0.0, value=12.0)
                duration = st.number_input("Tenure Duration (Months)", min_value=1, value=12)
                
                processing_fee = st.number_input("Processing Fee (₹)", min_value=0.0, value=500.0)
                admin_fee = st.number_input("Admin Fee (₹)", min_value=0.0, value=200.0)
                doc_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, value=200.0)
                
                interest_amount = principal * (interest_rate / 100)
                total_payable = principal + interest_amount
                calculated_emi = total_payable / duration
                
                if st.form_submit_button("Disburse Capital"):
                    if principal > (appraised_val * 0.75):
                        st.error("Requested capital allocation exceeds the LTV loan limit.")
                    else:
                        next_loan_id = int(loans_df['id'].max() + 1) if not loans_df.empty else 1
                        today_str = str(datetime.now().date())
                        
                        loan_row = [next_loan_id, selected_party, principal, interest_rate, duration, calculated_emi, processing_fee, admin_fee, doc_fee, principal, interest_amount, total_payable, gold_description, items_count, net_wt, net_wt, 22, appraised_val, vault_id, "", "Active", today_str]
                        loans_ws.append_row(loan_row)
                        
                        next_ledger_id = int(ledger_df['id'].max() + 1) if not ledger_df.empty else 1
                        ledger_ws.append_row([next_ledger_id, next_loan_id, "Disbursement", principal, today_str])
                        
                        st.success(f"Loan File #{next_loan_id} saved to Cloud Spreadsheet.")
                        st.rerun()

    elif sub_choice == "📊 Party Ledger":
        st.header("📊 Customer Ledger Statements")
        if loans_df.empty:
            st.info("No active loan records open currently.")
        else:
            active_loans = loans_df[loans_df['status'] == 'Active']
            if active_loans.empty:
                st.info("No active loan records open currently.")
            else:
                loan_opts = {}
                for _, l_row in active_loans.iterrows():
                    p_name = parties_df[parties_df['id'] == l_row['party_id']]['name'].values[0] if l_row['party_id'] in parties_df['id'].values else "Unknown"
                    loan_opts[l_row['id']] = f"Loan #{l_row['id']} - Holder: {p_name} (₹{l_row['principal']})"
                
                selected_loan = st.selectbox("Select Target Portfolio File", list(loan_opts.keys()), format_func=lambda x: loan_opts[x])
                
                target_loan_idx = loans_df[loans_df['id'] == selected_loan].index[0]
                target_loan_row = loans_df.iloc[target_loan_idx]
                
                total_liability = float(target_loan_row['total_payable'])
                
                repayments_pool = ledger_df[(ledger_df['loan_id'] == selected_loan) & (ledger_df['transaction_type'].isin(['Repayment', 'Interest Settlement']))]
                total_repaid = pd.to_numeric(repayments_pool['amount']).sum() if not repayments_pool.empty else 0.0
                
                live_outstanding_balance = max(0.0, total_liability - total_repaid)
                
                tab_post, tab_view = st.tabs(["💳 Collection Repayment Entry", "📑 View Balancing Ledger Statement"])
                
                with tab_post:
                    if live_outstanding_balance <= 0.0:
                        st.success("🎉 Paid in full.")
                    else:
                        with st.form("repayment_form"):
                            repay_amt = st.number_input("Repayment Amount (₹)", min_value=0.0, max_value=live_outstanding_balance)
                            repay_date = st.date_input("Settlement Date")
                            if st.form_submit_button("Post Repayment Entry"):
                                next_tx_id = int(ledger_df['id'].max() + 1) if not ledger_df.empty else 1
                                ledger_ws.append_row([next_tx_id, selected_loan, "Repayment", repay_amt, str(repay_date)])
                                
                                if repay_amt >= live_outstanding_balance:
                                    sheet_row_num = int(target_loan_idx) + 2
                                    loans_ws.update_cell(sheet_row_num, 21, "Closed")
                                
                                st.success("Repayment posted successfully to Google Sheets!")
                                st.rerun()
                                
                with tab_view:
                    st.metric("Current Outstanding Balance", f"₹{live_outstanding_balance:,.2f}")
                    st.dataframe(ledger_df[ledger_df['loan_id'] == selected_loan], use_container_width=True)

# ==========================================
# MODULE: GOLD PLEDGE MANAGEMENT
# ==========================================
elif choice == "💍 Gold Pledge Management":
    st.header("💍 Gold Pledge Inventory Vault Details")
    active_items = loans_df[loans_df['status'] == 'Active'] if not loans_df.empty else pd.DataFrame()
    
    if active_items.empty:
        st.info("No vaulted items found inside database logs.")
    else:
        for _, row in active_items.iterrows():
            p_name = parties_df[parties_df['id'] == row['party_id']]['name'].values[0] if row['party_id'] in parties_df['id'].values else "Unknown"
            st.markdown(f"### 📦 Loan Account Portfolio Reference #{row['id']}")
            st.write(f"👤 **ഉടമസ്ഥൻ:** {p_name} | 📝 **ആഭരണ വിവരണം:** {row['gold_description']}")
            st.write(f"🔢 **എണ്ണം:** {row['items_count']} Nos | ⚖️ **തൂക്കം:** {row['net_weight']} ഗ്രാം | 🔒 **വോൾട്ട് സൂചിക:** `{row['vault_id']}`")
            st.markdown("---")

# ==========================================
# MODULE: LOAN AGREEMENT MALAYALAM
# ==========================================
elif choice == "📄 Loan Agreement (Malayalam)":
    st.header("📄 Malayalam Legal Agreement Console")
    if loans_df.empty:
        st.info("No loan records found.")
    else:
        loan_opts = {row['id']: f"Loan #{row['id']}" for _, row in loans_df.iterrows()}
        target_contract = st.selectbox("Select Target File", list(loan_opts.keys()), format_func=lambda x: loan_opts[x])
        
        loan_row = loans_df[loans_df['id'] == target_contract].iloc[0]
        party_row = parties_df[parties_df['id'] == loan_row['party_id']].iloc[0]
        
        agreement_html = generate_agreement_html(loan_row, party_row)
        st.download_button(label="📥 ഡൗൺലോഡ് കരാർ പത്രം", data=agreement_html, file_name=f"Agreement_{target_contract}.html", mime="text/html")

# ==========================================
# MODULE: EMI SCHEDULE MATRIX
# ==========================================
elif choice == "📅 EMI Schedule":
    st.header("📅 Monthly Recovery Projection Mapping (EMI Schedule)")
    if loans_df.empty:
        st.info("No loan records found.")
    else:
        active_loans = loans_df[loans_df['status'] == 'Active']
        if active_loans.empty:
            st.info("No active loan tracking matrices found.")
        else:
            loan_opts = {row['id']: f"Loan #{row['id']} (EMI: ₹{float(row['emi']):,.2f})" for _, row in active_loans.iterrows()}
            selected_sched = st.selectbox("Select Target Loan ID", list(loan_opts.keys()), format_func=lambda x: loan_opts[x])
            
            target_l = loans_df[loans_df['id'] == selected_sched].iloc[0]
            
            schedule_list = []
            rem_pool = float(target_l['total_payable'])
            for index in range(1, int(target_l['duration_months']) + 1):
                rem_pool -= float(target_l['emi'])
                schedule_list.append({
                    "Installment": f"Month No. {index}",
                    "Payment Amount (₹)": f"₹{float(target_l['emi']):,.2f}",
                    "Outstanding Balance": f"₹{max(0.0, rem_pool):,.2f}"
                })
            st.table(pd.DataFrame(schedule_list))

# ==========================================
# MODULE: BACKUP & EXPORTS
# ==========================================
elif choice == "💾 Backup, Restore & Upload":
    st.header("💾 Storage Engine Exports")
    
    st.download_button("Download Customers Dataset (CSV)", data=parties_df.to_csv(index=False).encode('utf-8'), file_name="parties_export.csv", mime="text/csv")
    st.download_button("Download Loans Dataset (CSV)", data=loans_df.to_csv(index=False).encode('utf-8'), file_name="loans_export.csv", mime="text/csv")
    st.info("💡 Storage backend is dynamically handled on Google Sheets cloud architecture.")


