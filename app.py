import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from streamlit_gsheets import GSheetsConnection

# ==========================================
# GOOGLE SHEETS CONNECTION
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_data(sheet_name):
    """Read data from a sheet"""
    try:
        data = conn.read(worksheet=sheet_name)
        return data.dropna(how='all') if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def save_data(sheet_name, df):
    """Save data to a sheet"""
    conn.update(worksheet=sheet_name, data=df)

def get_next_id(df):
    """Get next ID"""
    if df.empty or 'id' not in df.columns:
        return 1
    ids = pd.to_numeric(df['id'], errors='coerce').dropna()
    return int(ids.max()) + 1 if not ids.empty else 1

# ==========================================
# LOAD DATA
# ==========================================
parties_df = get_data("Parties")
loans_df = get_data("Loans")
ledger_df = get_data("Ledger")

# ==========================================
# UI SETUP
# ==========================================
st.set_page_config(page_title="AuraLoan", layout="wide", page_icon="💎")

st.markdown("""
<style>
.stApp { background-color: #FAF6EE; }
.gold-header { color: #8B6508; font-weight: bold; text-align: center; }
.stMetric { background-color: #FFFDF7; padding: 15px; border-radius: 8px; border: 1px solid #E3C16F; }
.agreement-box { border: 2px solid #b8860b; padding: 30px; background-color: #fcfcf4; border-radius: 10px; }
.agreement-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
.agreement-table th, .agreement-table td { border: 1px solid #b8860b; padding: 10px; }
.agreement-table th { background-color: #f5f0db; color: #b8860b; }
</style>
""", unsafe_allow_html=True)

# Stats
active_loans_count = len(loans_df[loans_df['status'] == 'Active']) if not loans_df.empty else 0
total_disbursed = pd.to_numeric(loans_df['principal'], errors='coerce').sum() if not loans_df.empty else 0
total_gold = pd.to_numeric(loans_df[loans_df['status']=='Active']['net_weight'], errors='coerce').sum() if not loans_df.empty else 0

# Sidebar
st.sidebar.title("💎 AuraLoan")
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add Customer", "New Loan", "View Loans", "Repayments", "Agreements"])

st.sidebar.markdown("---")
st.sidebar.metric("Active Loans", active_loans_count)
st.sidebar.metric("Total Disbursed", f"₹{total_disbursed:,.0f}")
st.sidebar.metric("Gold in Vault", f"{total_gold:.1f}g")

# ==========================================
# DASHBOARD
# ==========================================
if menu == "Dashboard":
    st.title("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Loans", active_loans_count)
    col2.metric("Total Disbursed", f"₹{total_disbursed:,.0f}")
    col3.metric("Gold in Vault", f"{total_gold:.1f}g")
    
    if not loans_df.empty:
        st.subheader("All Loans")
        display = loans_df[['id', 'party_name', 'principal', 'status']].copy()
        display.columns = ['Loan ID', 'Customer', 'Amount', 'Status']
        st.dataframe(display, use_container_width=True)

# ==========================================
# ADD CUSTOMER
# ==========================================
elif menu == "Add Customer":
    st.title("👤 Register New Customer")
    
    with st.form("customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name *")
            guardian = st.text_input("Father/Husband Name")
            dob = st.date_input("Date of Birth")
            mobile = st.text_input("Mobile *")
        with col2:
            occupation = st.text_input("Occupation")
            address = st.text_area("Address")
            pincode = st.text_input("Pincode")
            kyc = st.selectbox("KYC Status", ["Pending", "Verified"])
        
        if st.form_submit_button("Register"):
            if name and mobile:
                new_id = get_next_id(parties_df)
                new_row = pd.DataFrame([{
                    'id': new_id, 'name': name, 'guardian_name': guardian,
                    'dob': str(dob), 'mobile': mobile, 'whatsapp': '',
                    'address': address, 'pincode': pincode, 'pan_masked': '',
                    'occupation': occupation, 'qualification': '',
                    'kyc_status': kyc, 'created_at': str(datetime.now().date())
                }])
                parties_df = pd.concat([parties_df, new_row], ignore_index=True) if not parties_df.empty else new_row
                save_data("Parties", parties_df)
                st.success(f"✅ {name} registered!")
                st.rerun()
            else:
                st.error("Name and Mobile required")

# ==========================================
# NEW LOAN
# ==========================================
elif menu == "New Loan":
    st.title("💰 New Gold Loan")
    
    if parties_df.empty:
        st.warning("Register a customer first!")
    else:
        verified = parties_df[parties_df['kyc_status'] == 'Verified']
        if verified.empty:
            st.warning("No verified customers!")
        else:
            with st.form("loan_form"):
                customer = st.selectbox("Select Customer", verified['id'].tolist(), 
                                       format_func=lambda x: f"{verified[verified['id']==x]['name'].values[0]} (ID:{x})")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Gold Details")
                    gold_desc = st.text_input("Description")
                    items = st.number_input("Number of Items", 1, 100, 1)
                    net_wt = st.number_input("Net Weight (grams)", 0.0, 10000.0, 10.0)
                    purity = st.selectbox("Purity", [24, 22, 20, 18])
                    appraised = st.number_input("Appraised Value (₹)", 0.0, 10000000.0, 50000.0)
                    vault = st.text_input("Vault ID")
                    photo = st.file_uploader("Gold Photo", type=['jpg', 'png', 'jpeg'])
                    
                with col2:
                    st.subheader("Loan Terms")
                    max_loan = appraised * 0.75
                    st.info(f"Max Loan: ₹{max_loan:,.0f}")
                    principal = st.number_input("Loan Amount (₹)", 0.0, max_loan, 40000.0)
                    rate = st.number_input("Interest Rate (%)", 0.0, 100.0, 12.0)
                    duration = st.number_input("Duration (months)", 1, 36, 12)
                    
                    st.subheader("Fees")
                    proc_fee = st.number_input("Processing Fee (₹)", 0.0, 10000.0, 500.0)
                    admin_fee = st.number_input("Admin Fee (₹)", 0.0, 5000.0, 200.0)
                    doc_fee = st.number_input("Documentation Fee (₹)", 0.0, 5000.0, 200.0)
                    
                    interest = principal * (rate/100)
                    total = principal + interest
                    emi = total / duration
                    
                    st.metric("Interest", f"₹{interest:,.0f}")
                    st.metric("Total Payable", f"₹{total:,.0f}")
                    st.metric("Monthly EMI", f"₹{emi:,.0f}")
                
                if st.form_submit_button("Disburse Loan"):
                    photo_b64 = base64.b64encode(photo.read()).decode() if photo else ""
                    cname = verified[verified['id']==customer]['name'].values[0]
                    today = str(datetime.now().date())
                    
                    new_id = get_next_id(loans_df)
                    new_loan = pd.DataFrame([{
                        'id': new_id, 'party_id': customer, 'party_name': cname,
                        'principal': principal, 'interest_rate': rate,
                        'duration_months': duration, 'emi': emi,
                        'processing_fee': proc_fee, 'admin_fee': admin_fee,
                        'documentation_fee': doc_fee, 'net_disbursed': principal,
                        'interest_amount': interest, 'total_payable': total,
                        'gold_description': gold_desc, 'items_count': items,
                        'gross_weight': 0, 'net_weight': net_wt,
                        'purity_karat': purity, 'appraised_value': appraised,
                        'vault_id': vault, 'gold_image_base64': photo_b64,
                        'status': 'Active', 'disbursed_date': today,
                        'created_at': today
                    }])
                    loans_df = pd.concat([loans_df, new_loan], ignore_index=True) if not loans_df.empty else new_loan
                    save_data("Loans", loans_df)
                    
                    # Add ledger entry
                    ledger_id = get_next_id(ledger_df)
                    new_ledger = pd.DataFrame([{
                        'id': ledger_id, 'loan_id': new_id,
                        'transaction_type': 'Disbursement',
                        'amount': principal, 'transaction_date': today,
                        'created_at': today
                    }])
                    ledger_df = pd.concat([ledger_df, new_ledger], ignore_index=True) if not ledger_df.empty else new_ledger
                    save_data("Ledger", ledger_df)
                    
                    st.success(f"✅ Loan #{new_id} created!")
                    st.rerun()

# ==========================================
# VIEW LOANS
# ==========================================
elif menu == "View Loans":
    st.title("📋 All Loans")
    
    if loans_df.empty:
        st.info("No loans yet")
    else:
        status_filter = st.selectbox("Filter", ["All", "Active", "Closed"])
        filtered = loans_df if status_filter == "All" else loans_df[loans_df['status'] == status_filter]
        
        for _, loan in filtered.iterrows():
            with st.expander(f"Loan #{loan['id']} - {loan['party_name']} - ₹{loan['principal']} ({loan['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Amount:** ₹{loan['principal']}")
                    st.write(f"**Interest:** {loan['interest_rate']}%")
                    st.write(f"**Duration:** {loan['duration_months']} months")
                    st.write(f"**EMI:** ₹{loan['emi']}")
                    st.write(f"**Total Payable:** ₹{loan['total_payable']}")
                with col2:
                    st.write(f"**Gold:** {loan['gold_description']}")
                    st.write(f"**Weight:** {loan['net_weight']}g")
                    st.write(f"**Purity:** {loan['purity_karat']}K")
                    st.write(f"**Vault:** {loan['vault_id']}")
                    st.write(f"**Date:** {loan['disbursed_date']}")

# ==========================================
# REPAYMENTS
# ==========================================
elif menu == "Repayments":
    st.title("💳 Repayments")
    
    if loans_df.empty:
        st.info("No loans")
    else:
        active = loans_df[loans_df['status'] == 'Active']
        if active.empty:
            st.info("No active loans")
        else:
            loan_sel = st.selectbox("Select Loan", active['id'].tolist(),
                                   format_func=lambda x: f"Loan #{x} - {active[active['id']==x]['party_name'].values[0]}")
            
            loan = active[active['id']==loan_sel].iloc[0]
            total_payable = float(loan['total_payable'])
            
            # Calculate paid
            if not ledger_df.empty:
                loan_ledger = ledger_df[ledger_df['loan_id'].astype(str) == str(loan_sel)]
                paid = pd.to_numeric(loan_ledger['amount'], errors='coerce').sum()
            else:
                paid = 0
                
            balance = total_payable - paid
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Payable", f"₹{total_payable:,.0f}")
            col2.metric("Paid", f"₹{paid:,.0f}")
            col3.metric("Balance", f"₹{balance:,.0f}")
            
            if balance > 0:
                with st.form("repay"):
                    amount = st.number_input("Amount (₹)", 0.0, balance, 1000.0)
                    date = st.date_input("Date")
                    
                    if st.form_submit_button("Record Payment"):
                        ledger_id = get_next_id(ledger_df)
                        new_entry = pd.DataFrame([{
                            'id': ledger_id, 'loan_id': loan_sel,
                            'transaction_type': 'Repayment',
                            'amount': amount,
                            'transaction_date': str(date),
                            'created_at': str(datetime.now().date())
                        }])
                        ledger_df = pd.concat([ledger_df, new_entry], ignore_index=True) if not ledger_df.empty else new_entry
                        save_data("Ledger", ledger_df)
                        
                        if amount >= balance:
                            loans_df.loc[loans_df['id'] == loan_sel, 'status'] = 'Closed'
                            save_data("Loans", loans_df)
                        
                        st.success("✅ Payment recorded!")
                        st.rerun()

# ==========================================
# AGREEMENTS
# ==========================================
elif menu == "Agreements":
    st.title("📄 Agreements")
    
    if loans_df.empty:
        st.info("No loans")
    else:
        loan_sel = st.selectbox("Select Loan", loans_df['id'].tolist(),
                               format_func=lambda x: f"Loan #{x} - {loans_df[loans_df['id']==x]['party_name'].values[0]}")
        
        loan = loans_df[loans_df['id']==loan_sel].iloc[0]
        party = parties_df[parties_df['id'].astype(str)==str(loan['party_id'])]
        party = party.iloc[0] if not party.empty else None
        
        if party is not None:
            agreement = f"""
            <div class="agreement-box">
                <h2 class="gold-header">GOLD LOAN AGREEMENT</h2>
                <p><b>Agreement No:</b> #{loan['id']} | <b>Date:</b> {loan['disbursed_date']}</p>
                <hr>
                <h3>Customer Details</h3>
                <p><b>Name:</b> {party['name']}<br>
                <b>Mobile:</b> {party['mobile']}<br>
                <b>Address:</b> {party.get('address', 'N/A')}</p>
                
                <h3>Loan Details</h3>
                <table class="agreement-table">
                    <tr><th>Item</th><th>Details</th></tr>
                    <tr><td>Loan Amount</td><td>₹{loan['principal']}</td></tr>
                    <tr><td>Interest Rate</td><td>{loan['interest_rate']}%</td></tr>
                    <tr><td>Duration</td><td>{loan['duration_months']} months</td></tr>
                    <tr><td>EMI</td><td>₹{loan['emi']}</td></tr>
                    <tr><td>Total Payable</td><td>₹{loan['total_payable']}</td></tr>
                </table>
                
                <h3>Gold Details</h3>
                <p><b>Description:</b> {loan['gold_description']}<br>
                <b>Weight:</b> {loan['net_weight']}g | <b>Purity:</b> {loan['purity_karat']}K<br>
                <b>Vault:</b> {loan['vault_id']}</p>
            </div>
            """
            
            st.markdown(agreement, unsafe_allow_html=True)
            st.download_button("Download Agreement", agreement, f"agreement_{loan['id']}.html", "text/html")

st.markdown("---")
st.markdown("<center style='color:#8B6508;'>© 2024 AuraLoan</center>", unsafe_allow_html=True)
