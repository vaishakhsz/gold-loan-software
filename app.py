# app.py - Gold Loan Management System
# Complete application code - Copy this entire file

import streamlit as st
import pandas as pd
import datetime
import uuid
import json
import os
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Gold Loan Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FFD700;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1a1a2e, #16213e);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #f0e6d3;
        padding: 0.5rem;
        background: #2c3e50;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #FFD700;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #FFD700;
        color: #1a1a2e;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #f0c000;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'parties' not in st.session_state:
    st.session_state.parties = {}
if 'loans' not in st.session_state:
    st.session_state.loans = {}
if 'gold_items' not in st.session_state:
    st.session_state.gold_items = {}
if 'transactions' not in st.session_state:
    st.session_state.transactions = {}
if 'party_counter' not in st.session_state:
    st.session_state.party_counter = 1

# Helper functions
def generate_party_id():
    party_id = f"P{str(st.session_state.party_counter).zfill(4)}"
    st.session_state.party_counter += 1
    return party_id

def generate_loan_id():
    return f"L{datetime.now().strftime('%Y%m%d')}{str(len(st.session_state.loans) + 1).zfill(3)}"

def calculate_emi(principal, interest_rate, tenure_months):
    """Calculate EMI using formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
    if interest_rate == 0:
        return principal / tenure_months
    monthly_rate = interest_rate / 12 / 100
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)

def calculate_total_payment(emi, tenure_months):
    return emi * tenure_months

def calculate_total_interest(principal, emi, tenure_months):
    return calculate_total_payment(emi, tenure_months) - principal

# Main Application
st.markdown('<h1 class="main-header">🏦 Gold Loan Management System</h1>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📋 Navigation")
menu = st.sidebar.selectbox(
    "Select Module",
    ["🏠 Dashboard", "👤 Party Master", "💰 Gold Loan Disbursement", 
     "📊 Party Ledger", "💍 Gold Pledge Management", "📄 Loan Agreement"]
)

# Dashboard Module
if menu == "🏠 Dashboard":
    st.markdown('<h2 class="sub-header">📊 Dashboard Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(st.session_state.parties))
    with col2:
        total_loans = len(st.session_state.loans)
        st.metric("Total Loans", total_loans)
    with col3:
        total_principal = sum([loan['principal'] for loan in st.session_state.loans.values()]) if st.session_state.loans else 0
        st.metric("Total Disbursed (₹)", f"₹{total_principal:,.2f}")
    with col4:
        total_gold_weight = sum([item['net_weight'] for item in st.session_state.gold_items.values()]) if st.session_state.gold_items else 0
        st.metric("Total Gold Pledged (g)", f"{total_gold_weight:.2f}g")
    
    # Recent Transactions
    st.markdown('<h3 class="sub-header">📈 Recent Activity</h3>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        recent_trans = list(st.session_state.transactions.values())[-5:]
        df_recent = pd.DataFrame(recent_trans)
        st.dataframe(df_recent[['date', 'party_id', 'party_name', 'transaction_type', 'amount']], use_container_width=True)
    else:
        st.info("No recent transactions available.")

# Party Master Module
elif menu == "👤 Party Master":
    st.markdown('<h2 class="sub-header">👤 Party Master Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Party", "📋 View All Parties", "🔍 Search Party"])
    
    with tab1:
        with st.form("party_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Personal Details")
                party_name = st.text_input("Full Name *", placeholder="Enter full name")
                age = st.number_input("Age", min_value=18, max_value=100, step=1)
                dob = st.date_input("Date of Birth", max_value=datetime.now())
                occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"])
                avg_monthly_salary = st.number_input("Average Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f")
                qualification = st.text_input("Qualification")
                
                st.markdown("### Contact Details")
                address = st.text_area("Address", placeholder="Enter complete address")
                city = st.text_input("City")
                pincode = st.text_input("Pincode")
                mobile = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
                whatsapp = st.text_input("WhatsApp Number", placeholder="10-digit number")
            
            with col2:
                st.markdown("### Spouse Details")
                spouse_name = st.text_input("Spouse's Full Name")
                spouse_age = st.number_input("Spouse's Age", min_value=18, max_value=100, step=1)
                spouse_dob = st.date_input("Spouse's Date of Birth", max_value=datetime.now())
                spouse_occupation = st.selectbox("Spouse's Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"])
                spouse_avg_salary = st.number_input("Spouse's Avg Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f")
                spouse_qualification = st.text_input("Spouse's Qualification")
                
                st.markdown("### Spouse's Contact Details")
                spouse_address = st.text_area("Spouse's Address", placeholder="If different from above")
                spouse_city = st.text_input("Spouse's City")
                spouse_pincode = st.text_input("Spouse's Pincode")
                spouse_mobile = st.text_input("Spouse's Mobile Number")
                spouse_whatsapp = st.text_input("Spouse's WhatsApp Number")
            
            submitted = st.form_submit_button("💾 Save Party Details")
            
            if submitted:
                if not party_name or not mobile:
                    st.error("⚠️ Please fill in all required fields (Name and Mobile Number).")
                else:
                    party_id = generate_party_id()
                    party_data = {
                        'party_id': party_id,
                        'party_name': party_name,
                        'age': age,
                        'dob': dob.strftime("%Y-%m-%d"),
                        'address': address,
                        'city': city,
                        'pincode': pincode,
                        'mobile': mobile,
                        'whatsapp': whatsapp if whatsapp else mobile,
                        'occupation': occupation,
                        'avg_monthly_salary': avg_monthly_salary,
                        'qualification': qualification,
                        'spouse_name': spouse_name,
                        'spouse_age': spouse_age,
                        'spouse_dob': spouse_dob.strftime("%Y-%m-%d") if spouse_dob else None,
                        'spouse_address': spouse_address if spouse_address else address,
                        'spouse_city': spouse_city if spouse_city else city,
                        'spouse_pincode': spouse_pincode if spouse_pincode else pincode,
                        'spouse_mobile': spouse_mobile if spouse_mobile else "",
                        'spouse_whatsapp': spouse_whatsapp if spouse_whatsapp else "",
                        'spouse_occupation': spouse_occupation,
                        'spouse_avg_salary': spouse_avg_salary,
                        'spouse_qualification': spouse_qualification,
                        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.parties[party_id] = party_data
                    
                    # Add to transactions
                    trans_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    st.session_state.transactions[trans_id] = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_name,
                        'transaction_type': 'Party Registration',
                        'amount': 0,
                        'details': 'New party registered'
                    }
                    
                    st.success(f"✅ Party {party_name} registered successfully with ID: {party_id}")
                    st.balloons()
    
    with tab2:
        if st.session_state.parties:
            df_parties = pd.DataFrame(st.session_state.parties.values())
            display_cols = ['party_id', 'party_name', 'age', 'mobile', 'city', 'occupation', 'avg_monthly_salary']
            st.dataframe(df_parties[display_cols], use_container_width=True)
        else:
            st.info("No parties registered yet.")
    
    with tab3:
        search_term = st.text_input("Search by Name or Party ID")
        if search_term:
            results = []
            for party_id, party_data in st.session_state.parties.items():
                if search_term.lower() in party_data['party_name'].lower() or search_term.lower() in party_id.lower():
                    results.append(party_data)
            if results:
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("No matching parties found.")

# Gold Loan Disbursement Module
elif menu == "💰 Gold Loan Disbursement":
    st.markdown('<h2 class="sub-header">💰 Gold Loan Disbursement</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ Please add at least one party before disbursing a loan.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Loan Application")
            
            # Party Selection
            party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                           for pid, data in st.session_state.parties.items()}
            selected_party_display = st.selectbox("Select Party *", list(party_options.keys()))
            party_id = party_options[selected_party_display]
            party_data = st.session_state.parties[party_id]
            
            # Display party info
            st.markdown(f"""
            <div class="info-box">
                <strong>Party Details:</strong><br>
                Name: {party_data['party_name']}<br>
                Mobile: {party_data['mobile']}<br>
                City: {party_data['city']}<br>
                Occupation: {party_data['occupation']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Loan Details")
            principal = st.number_input("Principal Amount (₹) *", min_value=1000.0, step=500.0, format="%.2f")
            interest_rate = st.number_input("Interest Rate (% per annum) *", min_value=0.0, max_value=36.0, step=0.5, format="%.1f")
            duration_months = st.number_input("Duration (Months) *", min_value=1, max_value=60, step=1)
        
        with col2:
            st.markdown("### Fee Structure")
            processing_fee = st.number_input("Processing Fee (₹)", min_value=0.0, step=50.0, format="%.2f")
            admin_fee = st.number_input("Admin Fee (₹)", min_value=0.0, step=50.0, format="%.2f")
            documentation_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, step=50.0, format="%.2f")
            
            total_fees = processing_fee + admin_fee + documentation_fee
            net_disbursement = principal - total_fees
            
            # Calculate EMI
            if principal > 0 and duration_months > 0:
                emi = calculate_emi(principal, interest_rate, duration_months)
                total_interest = calculate_total_interest(principal, emi, duration_months)
                total_payment = calculate_total_payment(emi, duration_months)
                
                st.markdown("### Loan Summary")
                st.markdown(f"""
                <div class="info-box">
                    <strong>Calculations:</strong><br>
                    EMI: ₹{emi:,.2f}<br>
                    Total Interest: ₹{total_interest:,.2f}<br>
                    Total Payment: ₹{total_payment:,.2f}<br>
                    Total Fees: ₹{total_fees:,.2f}<br>
                    <strong>Net Disbursement: ₹{net_disbursement:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Enter principal and duration to calculate EMI.")
            
            # Submit Loan
            if st.button("💰 Disburse Loan", use_container_width=True):
                if principal <= 0 or duration_months <= 0:
                    st.error("⚠️ Please enter valid principal amount and duration.")
                elif net_disbursement < 0:
                    st.error("⚠️ Total fees cannot exceed principal amount.")
                else:
                    loan_id = generate_loan_id()
                    loan_data = {
                        'loan_id': loan_id,
                        'party_id': party_id,
                        'party_name': party_data['party_name'],
                        'principal': principal,
                        'interest_rate': interest_rate,
                        'duration_months': duration_months,
                        'emi': emi,
                        'total_interest': total_interest,
                        'total_payment': total_payment,
                        'processing_fee': processing_fee,
                        'admin_fee': admin_fee,
                        'documentation_fee': documentation_fee,
                        'total_fees': total_fees,
                        'net_disbursement': net_disbursement,
                        'disbursement_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'status': 'Active',
                        'outstanding_balance': total_payment,
                        'paid_amount': 0,
                        'remaining_tenure': duration_months
                    }
                    st.session_state.loans[loan_id] = loan_data
                    
                    # Add to transactions
                    trans_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    st.session_state.transactions[trans_id] = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_data['party_name'],
                        'transaction_type': 'Loan Disbursement',
                        'amount': net_disbursement,
                        'details': f'Loan ID: {loan_id}'
                    }
                    
                    st.success(f"✅ Loan disbursed successfully! Loan ID: {loan_id}")
                    st.balloons()
                    
                    # Display agreement option
                    st.info(f"📄 Net amount disbursed: ₹{net_disbursement:,.2f}")

# Party Ledger Module
elif menu == "📊 Party Ledger":
    st.markdown('<h2 class="sub-header">📊 Party Ledger</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ No parties available. Please add a party first.")
    else:
        # Party Selection
        party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                       for pid, data in st.session_state.parties.items()}
        selected_party = st.selectbox("Select Party for Ledger", list(party_options.keys()))
        party_id = party_options[selected_party]
        party_data = st.session_state.parties[party_id]
        
        # Get all transactions for this party
        party_transactions = []
        for trans_id, trans_data in st.session_state.transactions.items():
            if trans_data['party_id'] == party_id:
                party_transactions.append(trans_data)
        
        # Get all loans for this party
        party_loans = []
        for loan_id, loan_data in st.session_state.loans.items():
            if loan_data['party_id'] == party_id:
                party_loans.append(loan_data)
        
        if party_transactions or party_loans:
            st.markdown(f"### Ledger for: {party_data['party_name']} ({party_id})")
            
            # Summary cards
            col1, col2, col3 = st.columns(3)
            with col1:
                total_loan = sum([loan['net_disbursement'] for loan in party_loans])
                st.metric("Total Loans Disbursed", f"₹{total_loan:,.2f}")
            with col2:
                total_paid = sum([loan['paid_amount'] for loan in party_loans])
                st.metric("Total Amount Paid", f"₹{total_paid:,.2f}")
            with col3:
                total_balance = sum([loan['outstanding_balance'] for loan in party_loans])
                st.metric("Total Outstanding", f"₹{total_balance:,.2f}")
            
            # Display loans
            if party_loans:
                st.markdown("### Active Loans")
                df_loans = pd.DataFrame(party_loans)
                display_cols = ['loan_id', 'principal', 'emi', 'duration_months', 'outstanding_balance', 'status']
                st.dataframe(df_loans[display_cols], use_container_width=True)
                
                # Repayment Section
                st.markdown("### Make a Repayment")
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_loan_id = st.selectbox("Select Loan for Repayment", 
                                                  [loan['loan_id'] for loan in party_loans if loan['status'] == 'Active'])
                    if selected_loan_id:
                        loan_data = st.session_state.loans[selected_loan_id]
                        repayment_amount = st.number_input("Repayment Amount (₹)", 
                                                          min_value=0.0, 
                                                          max_value=float(loan_data['outstanding_balance']),
                                                          step=100.0,
                                                          format="%.2f")
                        
                        if st.button("💳 Make Payment", use_container_width=True):
                            if repayment_amount > 0:
                                # Update loan
                                loan_data['outstanding_balance'] -= repayment_amount
                                loan_data['paid_amount'] += repayment_amount
                                
                                if loan_data['outstanding_balance'] <= 0:
                                    loan_data['status'] = 'Closed'
                                    loan_data['outstanding_balance'] = 0
                                    st.success("✅ Loan fully repaid and closed!")
                                else:
                                    st.success(f"✅ Payment of ₹{repayment_amount:,.2f} recorded successfully!")
                                
                                # Add transaction
                                trans_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                st.session_state.transactions[trans_id] = {
                                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'party_id': party_id,
                                    'party_name': party_data['party_name'],
                                    'transaction_type': 'Loan Repayment',
                                    'amount': repayment_amount,
                                    'details': f'Loan ID: {selected_loan_id}'
                                }
                                st.rerun()
                            else:
                                st.warning("Please enter a valid repayment amount.")
                
                with col2:
                    if selected_loan_id:
                        loan_data = st.session_state.loans[selected_loan_id]
                        st.markdown(f"""
                        <div class="info-box">
                            <strong>Loan Summary:</strong><br>
                            Principal: ₹{loan_data['principal']:,.2f}<br>
                            EMI: ₹{loan_data['emi']:,.2f}<br>
                            Paid: ₹{loan_data['paid_amount']:,.2f}<br>
                            <strong>Outstanding: ₹{loan_data['outstanding_balance']:,.2f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display transaction history
            if party_transactions:
                st.markdown("### Transaction History")
                df_trans = pd.DataFrame(party_transactions)
                st.dataframe(df_trans[['date', 'transaction_type', 'amount', 'details']], use_container_width=True)
        else:
            st.info(f"No loans or transactions found for {party_data['party_name']}.")

# Gold Pledge Management Module
elif menu == "💍 Gold Pledge Management":
    st.markdown('<h2 class="sub-header">💍 Gold Pledge Management</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ Please add a party first before pledging gold.")
    else:
        tab1, tab2 = st.tabs(["➕ Add Gold Pledge", "📋 View All Pledges"])
        
        with tab1:
            with st.form("gold_pledge_form"):
                # Party Selection
                party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                               for pid, data in st.session_state.parties.items()}
                selected_party = st.selectbox("Select Party *", list(party_options.keys()))
                party_id = party_options[selected_party]
                
                # Gold Details
                st.markdown("### Gold Item Details")
                item_description = st.text_area("Description of Ornaments *", 
                                              placeholder="e.g., Gold chain, Bangles, Rings")
                item_count = st.number_input("Number of Items", min_value=1, step=1)
                gross_weight = st.number_input("Gross Weight (grams) *", min_value=0.1, step=0.1, format="%.2f")
                net_weight = st.number_input("Net Weight (grams) *", min_value=0.1, step=0.1, format="%.2f")
                purity = st.selectbox("Purity (Karat)", ["24K", "22K", "18K", "14K"])
                
                # Valuation
                current_gold_rate = st.number_input("Current Gold Rate (per gram)", min_value=0.0, step=50.0, format="%.2f")
                appraised_value = net_weight * current_gold_rate if net_weight > 0 and current_gold_rate > 0 else 0
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>Appraised Value: ₹{appraised_value:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Locker Details
                locker_id = st.text_input("Locker/Vault ID")
                
                submitted = st.form_submit_button("💍 Register Pledge")
                
                if submitted:
                    if not item_description or net_weight <= 0 or current_gold_rate <= 0:
                        st.error("⚠️ Please fill in all required fields with valid values.")
                    else:
                        pledge_id = f"G{datetime.now().strftime('%Y%m%d')}{str(len(st.session_state.gold_items) + 1).zfill(3)}"
                        gold_data = {
                            'pledge_id': pledge_id,
                            'party_id': party_id,
                            'party_name': st.session_state.parties[party_id]['party_name'],
                            'item_description': item_description,
                            'item_count': item_count,
                            'gross_weight': gross_weight,
                            'net_weight': net_weight,
                            'purity': purity,
                            'current_gold_rate': current_gold_rate,
                            'appraised_value': appraised_value,
                            'locker_id': locker_id,
                            'pledge_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'status': 'Active'
                        }
                        st.session_state.gold_items[pledge_id] = gold_data
                        
                        # Add to transactions
                        trans_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        st.session_state.transactions[trans_id] = {
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'party_id': party_id,
                            'party_name': st.session_state.parties[party_id]['party_name'],
                            'transaction_type': 'Gold Pledge',
                            'amount': appraised_value,
                            'details': f'Pledge ID: {pledge_id}'
                        }
                        
                        st.success(f"✅ Gold pledge registered successfully! Pledge ID: {pledge_id}")
                        st.balloons()
        
        with tab2:
            if st.session_state.gold_items:
                df_gold = pd.DataFrame(st.session_state.gold_items.values())
                display_cols = ['pledge_id', 'party_name', 'item_description', 'net_weight', 'purity', 'appraised_value', 'status']
                st.dataframe(df_gold[display_cols], use_container_width=True)
            else:
                st.info("No gold pledges registered yet.")

# Loan Agreement Module
elif menu == "📄 Loan Agreement":
    st.markdown('<h2 class="sub-header">📄 Gold Loan Agreement (Malayalam)</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties or not st.session_state.loans:
        st.warning("⚠️ Please add a party and disburse a loan first.")
    else:
        # Select Party and Loan
        col1, col2 = st.columns(2)
        
        with col1:
            party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                           for pid, data in st.session_state.parties.items()}
            selected_party = st.selectbox("Select Party", list(party_options.keys()))
            party_id = party_options[selected_party]
            party_data = st.session_state.parties[party_id]
        
        with col2:
            # Get loans for selected party
            party_loans = {loan['loan_id']: loan for loan in st.session_state.loans.values() 
                          if loan['party_id'] == party_id}
            if party_loans:
                loan_options = {f"{lid} - ₹{data['principal']:,.2f}": lid 
                              for lid, data in party_loans.items()}
                selected_loan = st.selectbox("Select Loan", list(loan_options.keys()))
                loan_id = loan_options[selected_loan]
                loan_data = st.session_state.loans[loan_id]
                
                # Get gold pledge details
                gold_pledges = [gold for gold in st.session_state.gold_items.values() 
                              if gold['party_id'] == party_id]
                
                if st.button("📄 Generate Agreement", use_container_width=True):
                    st.markdown("---")
                    
                    # Agreement in Malayalam
                    agreement_text = f"""
                    <div style="background: white; padding: 2rem; border-radius: 10px; color: black; font-family: 'Noto Sans Malayalam', sans-serif;">
                        <h1 style="text-align: center; color: #FFD700; font-size: 2rem;">സ്വർണ്ണപ്പണയ ഉടമ്പടി</h1>
                        <p style="text-align: center;">(Gold Loan Agreement)</p>
                        <hr style="border: 2px solid #FFD700;">
                        
                        <h3>1. പാർട്ടി വിവരങ്ങൾ (Party Details):</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>പേര് (Name):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data['party_name']}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data.get('spouse_name', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>വിലാസം (Address):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data['address']}, {party_data['city']}, {party_data['pincode']}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>മൊബൈൽ നമ്പർ (Mobile):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data['mobile']}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>തൊഴിൽ (Occupation):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data['occupation']}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>യോഗ്യത (Qualification):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{party_data['qualification']}</td></tr>
                        </table>
                        
                        <h3>2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details):</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>തുക (Principal Amount):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">₹{loan_data['principal']:,.2f}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>പലിശ നിരക്ക് (Interest Rate):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{loan_data['interest_rate']}% പ്രതിവർഷം</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>കാലാവധി (Tenure):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{loan_data['duration_months']} മാസം</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>പ്രതിമാസ തവണ (EMI):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">₹{loan_data['emi']:,.2f}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">₹{loan_data['processing_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>അഡ്മിൻ ഫീസ് (Admin Fee):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">₹{loan_data['admin_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee):</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">₹{loan_data['documentation_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 8px; border: 1px solid #ddd; background: #FFD700; font-weight: bold;">നൽകിയ തുക (Net Disbursed Amount):</td>
                                <td style="padding: 8px; border: 1px solid #ddd; background: #FFD700; font-weight: bold;">₹{loan_data['net_disbursement']:,.2f}</td></tr>
                        </table>
                    """
                    
                    # Add Gold Details
                    if gold_pledges:
                        agreement_text += """
                        <h3>3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Pledge Details):</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr style="background: #f0f2f6;">
                                <th style="padding: 8px; border: 1px solid #ddd;">വിവരണം (Description)</th>
                                <th style="padding: 8px; border: 1px solid #ddd;">എണ്ണം (Count)</th>
                                <th style="padding: 8px; border: 1px solid #ddd;">ഭാരം (g)</th>
                                <th style="padding: 8px; border: 1px solid #ddd;">പ്യൂരിറ്റി (Purity)</th>
                                <th style="padding: 8px; border: 1px solid #ddd;">മൂല്യം (Value)</th>
                            </tr>
                        """
                        for gold in gold_pledges:
                            agreement_text += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;">{gold['item_description']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{gold['item_count']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{gold['net_weight']:.2f}g</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{gold['purity']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{gold['appraised_value']:,.2f}</td>
                            </tr>
                            """
                        agreement_text += "</table>"
                    
                    # Terms and Conditions
                    agreement_text += """
                        <h3>4. നിബന്ധനകളും വ്യവസ്ഥകളും (Terms and Conditions):</h3>
                        <ol>
                            <li>മുകളിൽ പറഞ്ഞ സ്വർണ്ണാഭരണങ്ങൾ എന്റെ സ്വന്തമാണെന്നും, അതിൽ മറ്റാർക്കും അവകാശമില്ലെന്നും ഞാൻ സാക്ഷ്യപ്പെടുത്തുന്നു.</li>
                            <li>വായ്പ തുകയും പലിശയും നിശ്ചയിച്ച കാലാവധിക്കുള്ളിൽ അടച്ചുതീർക്കുന്നതിന് ഞാൻ ബാദ്ധ്യസ്ഥനാണ്.</li>
                            <li>വായ്പ തിരിച്ചടയ്ക്കുന്നതിൽ വീഴ്ച വരുത്തിയാൽ, ബാങ്കിന്/സ്ഥാപനത്തിന് പണയം വെച്ച സ്വർണ്ണം ലേലം ചെയ്യാനുള്ള അവകാശമുണ്ടായിരിക്കും.</li>
                            <li>പലിശ നിരക്കിലും മറ്റ് നിബന്ധനകളിലും മാറ്റം വരുത്താൻ സ്ഥാപനത്തിന് അധികാരമുണ്ട്.</li>
                            <li>വായ്പയുടെ ബാക്കി തുകയും പലിശയും പൂർണ്ണമായി അടച്ചതിന് ശേഷം മാത്രമേ സ്വർണ്ണം തിരികെ നൽകുകയുള്ളൂ.</li>
                            <li>ഈ ഉടമ്പടി പ്രകാരമുള്ള എല്ലാ തർക്കങ്ങളും സ്ഥാപനത്തിന്റെ ആധികാരിക പരിധിയിൽ പരിഹരിക്കുന്നതായിരിക്കും.</li>
                        </ol>
                        <hr style="border: 1px solid #ddd; margin: 2rem 0;">
                        
                        <table style="width: 100%; margin: 2rem 0;">
                            <tr>
                                <td style="padding: 20px;"><strong>ഒപ്പ് (Signature of Borrower):</strong> __________________</td>
                                <td style="padding: 20px;"><strong>തീയതി (Date):</strong> {datetime.now().strftime('%d-%m-%Y')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 20px;"><strong>സ്ഥലം (Place):</strong> __________________</td>
                                <td style="padding: 20px;"><strong>സാക്ഷി (Witness):</strong> __________________</td>
                            </tr>
                        </table>
                        
                        <div style="background: #f0f2f6; padding: 1rem; border-radius: 5px; margin-top: 2rem;">
                            <p style="text-align: center; color: #666; font-size: 0.9rem;">
                                <strong>Disclaimer:</strong> This is a system-generated agreement. Please verify all details before signing.
                            </p>
                        </div>
                    </div>
                    """
                    
                    st.markdown(agreement_text, unsafe_allow_html=True)
                    
                    # Download option
                    st.download_button(
                        label="📥 Download Agreement as HTML",
                        data=agreement_text,
                        file_name=f"Gold_Loan_Agreement_{party_data['party_name']}_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
            else:
                st.warning("No loans found for the selected party.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🏦 Gold Loan Management System v1.0\n\nDeveloped with ❤️ using Streamlit")

# Display system stats in sidebar
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: {len(st.session_state.parties)}")
st.sidebar.write(f"💰 Loans: {len(st.session_state.loans)}")
st.sidebar.write(f"💍 Gold Items: {len(st.session_state.gold_items)}")
st.sidebar.write(f"📝 Transactions: {len(st.session_state.transactions)}")
