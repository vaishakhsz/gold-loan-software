# app.py - Gold Loan Management System
# Updated with Simple Interest EMI Calculation & Malayalam Support

import streamlit as st
import pandas as pd
import datetime
from datetime import datetime, timedelta
import calendar
import base64

# Page configuration
st.set_page_config(
    page_title="Gold Loan Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI and Print
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
    .info-box-gold {
        background: #fff8e1;
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
    .print-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        color: black;
        border: 2px solid #FFD700;
        font-family: 'Noto Sans Malayalam', 'Malayalam', sans-serif;
    }
    .malayalam-text {
        font-family: 'Noto Sans Malayalam', 'Malayalam', 'Arial Unicode MS', sans-serif;
        font-size: 16px;
    }
    .calculation-box {
        background: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
    }
    .edit-highlight {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    @media print {
        .no-print { display: none; }
        .print-box { border: none; }
        .stApp { background: white; }
    }
    /* Malayalam font support */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam:wght@400;700&display=swap');
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

def calculate_simple_interest_emi(principal, interest_rate, tenure_months):
    """
    Calculate EMI using Simple Interest method
    Formula: 
    Total Interest = Principal × Rate × Time (in years)
    Total Amount = Principal + Total Interest
    EMI = Total Amount / Number of Months
    """
    tenure_years = tenure_months / 12
    total_interest = principal * (interest_rate / 100) * tenure_years
    total_amount = principal + total_interest
    emi = total_amount / tenure_months
    
    return {
        'emi': round(emi, 2),
        'total_interest': round(total_interest, 2),
        'total_amount': round(total_amount, 2),
        'tenure_years': round(tenure_years, 2)
    }

def generate_emi_schedule_simple(principal, interest_rate, tenure_months, start_date):
    """Generate EMI schedule with Simple Interest calculation"""
    result = calculate_simple_interest_emi(principal, interest_rate, tenure_months)
    emi = result['emi']
    total_interest = result['total_interest']
    total_amount = result['total_amount']
    
    schedule = []
    monthly_interest = total_interest / tenure_months
    monthly_principal = emi - monthly_interest
    remaining_balance = total_amount
    
    for i in range(1, tenure_months + 1):
        remaining_balance -= emi
        
        if start_date:
            current_date = start_date + timedelta(days=30 * i)
        else:
            current_date = datetime.now() + timedelta(days=30 * i)
        
        schedule.append({
            'Month': i,
            'Date': current_date.strftime('%d-%m-%Y'),
            'EMI': round(emi, 2),
            'Interest': round(monthly_interest, 2),
            'Principal': round(monthly_principal, 2),
            'Balance': round(max(0, remaining_balance), 2)
        })
    return schedule

def get_emi_calculation_breakdown(principal, interest_rate, tenure_months):
    """Get detailed breakdown of EMI calculation"""
    result = calculate_simple_interest_emi(principal, interest_rate, tenure_months)
    
    breakdown = f"""
    📊 **Simple Interest Calculation Breakdown:**
    
    Principal Amount (P) = ₹{principal:,.2f}
    Interest Rate (R) = {interest_rate}% per annum
    Tenure (T) = {tenure_months} months = {tenure_months/12:.1f} years
    
    ──────────────────────────────────────────────
    
    **Step 1: Calculate Total Interest**
    Total Interest = P × R × T
    = ₹{principal:,.2f} × {interest_rate}% × {tenure_months/12:.1f}
    = **₹{result['total_interest']:,.2f}**
    
    **Step 2: Calculate Total Amount Due**
    Total Amount = Principal + Total Interest
    = ₹{principal:,.2f} + ₹{result['total_interest']:,.2f}
    = **₹{result['total_amount']:,.2f}**
    
    **Step 3: Calculate Monthly EMI**
    EMI = Total Amount / Number of Months
    = ₹{result['total_amount']:,.2f} / {tenure_months}
    = **₹{result['emi']:,.2f}**
    
    ──────────────────────────────────────────────
    
    **Summary:**
    • Monthly Interest Component: ₹{result['total_interest']/tenure_months:,.2f}
    • Monthly Principal Component: ₹{(result['total_amount']/tenure_months) - (result['total_interest']/tenure_months):,.2f}
    • Total Interest Payable: ₹{result['total_interest']:,.2f}
    • Total Amount Payable: ₹{result['total_amount']:,.2f}
    • Monthly EMI: ₹{result['emi']:,.2f}
    """
    return breakdown, result

# Main Application
st.markdown('<h1 class="main-header">🏦 Gold Loan Management System</h1>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📋 Navigation")
menu = st.sidebar.selectbox(
    "Select Module",
    ["🏠 Dashboard", "👤 Party Master", "💰 Gold Loan Disbursement", 
     "📊 Party Ledger", "💍 Gold Pledge Management", "📄 Loan Agreement",
     "✏️ Edit Party Details", "📅 EMI Schedule"]
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
                age = st.number_input("Age", min_value=18, max_value=100, step=1, value=25)
                dob = st.date_input("Date of Birth", max_value=datetime.now())
                occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"])
                avg_monthly_salary = st.number_input("Average Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=0.0)
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
                spouse_age = st.number_input("Spouse's Age", min_value=18, max_value=100, step=1, value=25)
                spouse_dob = st.date_input("Spouse's Date of Birth", max_value=datetime.now())
                spouse_occupation = st.selectbox("Spouse's Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"])
                spouse_avg_salary = st.number_input("Spouse's Avg Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=0.0)
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

# Edit Party Details Module
elif menu == "✏️ Edit Party Details":
    st.markdown('<h2 class="sub-header">✏️ Edit Party Details</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ No parties available to edit.")
    else:
        party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                       for pid, data in st.session_state.parties.items()}
        selected_party = st.selectbox("Select Party to Edit", list(party_options.keys()))
        party_id = party_options[selected_party]
        party_data = st.session_state.parties[party_id]
        
        st.markdown(f'<div class="edit-highlight">Editing: {party_data["party_name"]} ({party_id})</div>', unsafe_allow_html=True)
        
        with st.form("edit_party_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Personal Details")
                party_name = st.text_input("Full Name *", value=party_data['party_name'])
                age = st.number_input("Age", min_value=18, max_value=100, step=1, value=int(party_data['age']))
                dob = st.date_input("Date of Birth", value=datetime.strptime(party_data['dob'], "%Y-%m-%d") if party_data['dob'] else datetime.now())
                occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"], 
                                        index=["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"].index(party_data['occupation']))
                avg_monthly_salary = st.number_input("Average Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(party_data['avg_monthly_salary']))
                qualification = st.text_input("Qualification", value=party_data['qualification'])
                
                st.markdown("### Contact Details")
                address = st.text_area("Address", value=party_data['address'])
                city = st.text_input("City", value=party_data['city'])
                pincode = st.text_input("Pincode", value=party_data['pincode'])
                mobile = st.text_input("Mobile Number *", value=party_data['mobile'])
                whatsapp = st.text_input("WhatsApp Number", value=party_data['whatsapp'])
            
            with col2:
                st.markdown("### Spouse Details")
                spouse_name = st.text_input("Spouse's Full Name", value=party_data.get('spouse_name', ''))
                spouse_age = st.number_input("Spouse's Age", min_value=18, max_value=100, step=1, value=int(party_data.get('spouse_age', 25)))
                spouse_dob = st.date_input("Spouse's Date of Birth", 
                                         value=datetime.strptime(party_data['spouse_dob'], "%Y-%m-%d") if party_data.get('spouse_dob') else datetime.now())
                spouse_occupation = st.selectbox("Spouse's Occupation", 
                                               ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"],
                                               index=["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"].index(party_data.get('spouse_occupation', 'Homemaker')))
                spouse_avg_salary = st.number_input("Spouse's Avg Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(party_data.get('spouse_avg_salary', 0)))
                spouse_qualification = st.text_input("Spouse's Qualification", value=party_data.get('spouse_qualification', ''))
                
                st.markdown("### Spouse's Contact Details")
                spouse_address = st.text_area("Spouse's Address", value=party_data.get('spouse_address', ''))
                spouse_city = st.text_input("Spouse's City", value=party_data.get('spouse_city', ''))
                spouse_pincode = st.text_input("Spouse's Pincode", value=party_data.get('spouse_pincode', ''))
                spouse_mobile = st.text_input("Spouse's Mobile Number", value=party_data.get('spouse_mobile', ''))
                spouse_whatsapp = st.text_input("Spouse's WhatsApp Number", value=party_data.get('spouse_whatsapp', ''))
            
            submitted = st.form_submit_button("💾 Update Party Details")
            
            if submitted:
                if not party_name or not mobile:
                    st.error("⚠️ Please fill in all required fields (Name and Mobile Number).")
                else:
                    party_data['party_name'] = party_name
                    party_data['age'] = age
                    party_data['dob'] = dob.strftime("%Y-%m-%d")
                    party_data['address'] = address
                    party_data['city'] = city
                    party_data['pincode'] = pincode
                    party_data['mobile'] = mobile
                    party_data['whatsapp'] = whatsapp if whatsapp else mobile
                    party_data['occupation'] = occupation
                    party_data['avg_monthly_salary'] = avg_monthly_salary
                    party_data['qualification'] = qualification
                    party_data['spouse_name'] = spouse_name
                    party_data['spouse_age'] = spouse_age
                    party_data['spouse_dob'] = spouse_dob.strftime("%Y-%m-%d") if spouse_dob else None
                    party_data['spouse_address'] = spouse_address if spouse_address else address
                    party_data['spouse_city'] = spouse_city if spouse_city else city
                    party_data['spouse_pincode'] = spouse_pincode if spouse_pincode else pincode
                    party_data['spouse_mobile'] = spouse_mobile if spouse_mobile else ""
                    party_data['spouse_whatsapp'] = spouse_whatsapp if spouse_whatsapp else ""
                    party_data['spouse_occupation'] = spouse_occupation
                    party_data['spouse_avg_salary'] = spouse_avg_salary
                    party_data['spouse_qualification'] = spouse_qualification
                    
                    st.session_state.parties[party_id] = party_data
                    
                    trans_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    st.session_state.transactions[trans_id] = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_name,
                        'transaction_type': 'Party Details Updated',
                        'amount': 0,
                        'details': f'Party {party_id} details updated'
                    }
                    
                    st.success(f"✅ Party {party_name} details updated successfully!")
                    st.balloons()

# Gold Loan Disbursement Module
elif menu == "💰 Gold Loan Disbursement":
    st.markdown('<h2 class="sub-header">💰 Gold Loan Disbursement</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ Please add at least one party before disbursing a loan.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Loan Application")
            
            party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                           for pid, data in st.session_state.parties.items()}
            selected_party_display = st.selectbox("Select Party *", list(party_options.keys()))
            party_id = party_options[selected_party_display]
            party_data = st.session_state.parties[party_id]
            
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
            principal = st.number_input("Principal Amount (₹) *", min_value=1000.0, step=500.0, format="%.2f", value=39475.0)
            interest_rate = st.number_input("Interest Rate (% per annum) *", min_value=0.0, max_value=36.0, step=0.5, format="%.1f", value=12.0)
            duration_months = st.number_input("Duration (Months) *", min_value=1, max_value=60, step=1, value=12)
            
            # EMI Start Date
            st.markdown("### EMI Schedule Dates")
            emi_start_date = st.date_input("EMI Start Date", value=datetime.now() + timedelta(days=30))
            emi_end_date = emi_start_date + timedelta(days=30 * duration_months)
            st.info(f"📅 EMI End Date: **{emi_end_date.strftime('%d-%m-%Y')}**")
        
        with col2:
            st.markdown("### Fee Structure")
            processing_fee = st.number_input("Processing Fee (₹)", min_value=0.0, step=50.0, format="%.2f", value=900.0)
            admin_fee = st.number_input("Admin Fee (₹)", min_value=0.0, step=50.0, format="%.2f", value=0.0)
            documentation_fee = st.number_input("Documentation Fee (₹)", min_value=0.0, step=50.0, format="%.2f", value=0.0)
            
            total_fees = processing_fee + admin_fee + documentation_fee
            net_disbursement = principal - total_fees
            
            if principal > 0 and duration_months > 0:
                # Calculate using Simple Interest method
                result = calculate_simple_interest_emi(principal, interest_rate, duration_months)
                emi = result['emi']
                total_interest = result['total_interest']
                total_amount = result['total_amount']
                
                # Generate EMI Schedule Preview
                emi_schedule = generate_emi_schedule_simple(principal, interest_rate, duration_months, emi_start_date)
                
                st.markdown("### Loan Summary")
                st.markdown(f"""
                <div class="info-box-gold">
                    <strong>📊 Simple Interest Calculation:</strong><br>
                    Principal Amount: ₹{principal:,.2f}<br>
                    Interest Rate: {interest_rate}% p.a.<br>
                    Tenure: {duration_months} months ({duration_months/12:.1f} years)<br>
                    <hr>
                    <strong>Total Interest: ₹{total_interest:,.2f}</strong><br>
                    <strong>Total Amount Due: ₹{total_amount:,.2f}</strong><br>
                    <strong>EMI: ₹{emi:,.2f}</strong><br>
                    <hr>
                    Processing Fee: ₹{processing_fee:,.2f}<br>
                    Total Fees: ₹{total_fees:,.2f}<br>
                    <strong>Net Disbursement: ₹{net_disbursement:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Show calculation breakdown
                with st.expander("📊 View Complete Calculation Breakdown"):
                    breakdown, _ = get_emi_calculation_breakdown(principal, interest_rate, duration_months)
                    st.markdown(f'<div class="calculation-box">{breakdown}</div>', unsafe_allow_html=True)
            else:
                st.info("Enter principal and duration to calculate EMI.")
            
            if st.button("💰 Disburse Loan", use_container_width=True):
                if principal <= 0 or duration_months <= 0:
                    st.error("⚠️ Please enter valid principal amount and duration.")
                elif net_disbursement < 0:
                    st.error("⚠️ Total fees cannot exceed principal amount.")
                else:
                    loan_id = generate_loan_id()
                    result = calculate_simple_interest_emi(principal, interest_rate, duration_months)
                    
                    loan_data = {
                        'loan_id': loan_id,
                        'party_id': party_id,
                        'party_name': party_data['party_name'],
                        'principal': principal,
                        'interest_rate': interest_rate,
                        'duration_months': duration_months,
                        'emi': result['emi'],
                        'total_interest': result['total_interest'],
                        'total_amount': result['total_amount'],
                        'processing_fee': processing_fee,
                        'admin_fee': admin_fee,
                        'documentation_fee': documentation_fee,
                        'total_fees': total_fees,
                        'net_disbursement': net_disbursement,
                        'disbursement_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'emi_start_date': emi_start_date.strftime("%Y-%m-%d"),
                        'emi_end_date': emi_end_date.strftime("%Y-%m-%d"),
                        'status': 'Active',
                        'outstanding_balance': result['total_amount'],
                        'paid_amount': 0,
                        'remaining_tenure': duration_months,
                        'emi_schedule': generate_emi_schedule_simple(principal, interest_rate, duration_months, emi_start_date),
                        'calculation_breakdown': get_emi_calculation_breakdown(principal, interest_rate, duration_months)[0]
                    }
                    st.session_state.loans[loan_id] = loan_data
                    
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
                    st.info(f"📄 Net amount disbursed: ₹{net_disbursement:,.2f}")

# EMI Schedule Module
elif menu == "📅 EMI Schedule":
    st.markdown('<h2 class="sub-header">📅 EMI Schedule</h2>', unsafe_allow_html=True)
    
    if not st.session_state.loans:
        st.warning("⚠️ No loans available.")
    else:
        # Select Loan
        loan_options = {f"{loan['loan_id']} - {loan['party_name']} (₹{loan['principal']:,.2f})": loan_id 
                       for loan_id, loan in st.session_state.loans.items()}
        selected_loan = st.selectbox("Select Loan", list(loan_options.keys()))
        loan_id = loan_options[selected_loan]
        loan_data = st.session_state.loans[loan_id]
        
        st.markdown(f"""
        <div class="info-box-gold">
            <strong>Loan Details:</strong><br>
            Party: {loan_data['party_name']}<br>
            Principal: ₹{loan_data['principal']:,.2f}<br>
            Interest Rate: {loan_data['interest_rate']}% p.a.<br>
            Tenure: {loan_data['duration_months']} months<br>
            <strong>Total Interest: ₹{loan_data['total_interest']:,.2f}</strong><br>
            <strong>Total Amount Due: ₹{loan_data['total_amount']:,.2f}</strong><br>
            <strong>EMI: ₹{loan_data['emi']:,.2f}</strong><br>
            EMI Start Date: {datetime.strptime(loan_data['emi_start_date'], '%Y-%m-%d').strftime('%d-%m-%Y')}<br>
            EMI End Date: {datetime.strptime(loan_data['emi_end_date'], '%Y-%m-%d').strftime('%d-%m-%Y')}
        </div>
        """, unsafe_allow_html=True)
        
        # Show calculation breakdown
        if 'calculation_breakdown' in loan_data:
            with st.expander("📊 Calculation Breakdown"):
                st.markdown(f'<div class="calculation-box">{loan_data["calculation_breakdown"]}</div>', unsafe_allow_html=True)
        
        # Display EMI Schedule
        if 'emi_schedule' in loan_data:
            df_schedule = pd.DataFrame(loan_data['emi_schedule'])
            st.markdown("### 📊 Complete EMI Schedule")
            st.dataframe(df_schedule, use_container_width=True)
            
            # Download Schedule
            csv = df_schedule.to_csv(index=False)
            st.download_button(
                label="📥 Download EMI Schedule as CSV",
                data=csv,
                file_name=f"EMI_Schedule_{loan_data['loan_id']}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Print Schedule
            if st.button("🖨️ Print EMI Schedule", use_container_width=True):
                st.markdown("---")
                st.markdown(f"""
                <div class="print-box">
                    <h2 style="text-align: center;">📊 EMI Schedule</h2>
                    <p><strong>Loan ID:</strong> {loan_data['loan_id']}</p>
                    <p><strong>Party:</strong> {loan_data['party_name']}</p>
                    <p><strong>Principal:</strong> ₹{loan_data['principal']:,.2f}</p>
                    <p><strong>Interest Rate:</strong> {loan_data['interest_rate']}% p.a.</p>
                    <p><strong>Total Interest:</strong> ₹{loan_data['total_interest']:,.2f}</p>
                    <p><strong>Total Amount Due:</strong> ₹{loan_data['total_amount']:,.2f}</p>
                    <p><strong>EMI:</strong> ₹{loan_data['emi']:,.2f}</p>
                    <hr>
                    {df_schedule.to_html(index=False)}
                </div>
                """, unsafe_allow_html=True)

# Party Ledger Module
elif menu == "📊 Party Ledger":
    st.markdown('<h2 class="sub-header">📊 Party Ledger</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.warning("⚠️ No parties available. Please add a party first.")
    else:
        party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                       for pid, data in st.session_state.parties.items()}
        selected_party = st.selectbox("Select Party for Ledger", list(party_options.keys()))
        party_id = party_options[selected_party]
        party_data = st.session_state.parties[party_id]
        
        party_transactions = []
        for trans_id, trans_data in st.session_state.transactions.items():
            if trans_data['party_id'] == party_id:
                party_transactions.append(trans_data)
        
        party_loans = []
        for loan_id, loan_data in st.session_state.loans.items():
            if loan_data['party_id'] == party_id:
                party_loans.append(loan_data)
        
        if party_transactions or party_loans:
            st.markdown(f"### Ledger for: {party_data['party_name']} ({party_id})")
            
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
            
            if party_loans:
                st.markdown("### Active Loans")
                df_loans = pd.DataFrame(party_loans)
                display_cols = ['loan_id', 'principal', 'emi', 'duration_months', 'outstanding_balance', 'status']
                st.dataframe(df_loans[display_cols], use_container_width=True)
                
                st.markdown("### Make a Repayment")
                col1, col2 = st.columns([2, 1])
                with col1:
                    active_loans = [loan for loan in party_loans if loan['status'] == 'Active']
                    if active_loans:
                        selected_loan_id = st.selectbox("Select Loan for Repayment", 
                                                      [loan['loan_id'] for loan in active_loans])
                        if selected_loan_id:
                            loan_data = st.session_state.loans[selected_loan_id]
                            repayment_amount = st.number_input("Repayment Amount (₹)", 
                                                              min_value=0.0, 
                                                              max_value=float(loan_data['outstanding_balance']),
                                                              step=100.0,
                                                              format="%.2f")
                            
                            if st.button("💳 Make Payment", use_container_width=True):
                                if repayment_amount > 0:
                                    loan_data['outstanding_balance'] -= repayment_amount
                                    loan_data['paid_amount'] += repayment_amount
                                    
                                    if loan_data['outstanding_balance'] <= 0:
                                        loan_data['status'] = 'Closed'
                                        loan_data['outstanding_balance'] = 0
                                        st.success("✅ Loan fully repaid and closed!")
                                    else:
                                        st.success(f"✅ Payment of ₹{repayment_amount:,.2f} recorded successfully!")
                                    
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
                    else:
                        st.info("No active loans for this party.")
                
                with col2:
                    if 'selected_loan_id' in locals() and selected_loan_id:
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
                party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                               for pid, data in st.session_state.parties.items()}
                selected_party = st.selectbox("Select Party *", list(party_options.keys()))
                party_id = party_options[selected_party]
                
                st.markdown("### Gold Item Details")
                item_description = st.text_area("Description of Ornaments *", 
                                              placeholder="e.g., Gold chain, Bangles, Rings")
                item_count = st.number_input("Number of Items", min_value=1, step=1, value=1)
                gross_weight = st.number_input("Gross Weight (grams) *", min_value=0.1, step=0.1, format="%.2f", value=10.0)
                net_weight = st.number_input("Net Weight (grams) *", min_value=0.1, step=0.1, format="%.2f", value=9.5)
                purity = st.selectbox("Purity (Karat)", ["24K", "22K", "18K", "14K"])
                
                current_gold_rate = st.number_input("Current Gold Rate (per gram)", min_value=0.0, step=50.0, format="%.2f", value=5000.0)
                appraised_value = net_weight * current_gold_rate if net_weight > 0 and current_gold_rate > 0 else 0
                
                st.markdown(f"""
                <div class="info-box-gold">
                    <strong>Appraised Value: ₹{appraised_value:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                
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

# Loan Agreement Module - Complete Malayalam
elif menu == "📄 Loan Agreement":
    st.markdown('<h2 class="sub-header">📄 Gold Loan Agreement (Malayalam)</h2>', unsafe_allow_html=True)
    
    if not st.session_state.parties or not st.session_state.loans:
        st.warning("⚠️ Please add a party and disburse a loan first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            party_options = {f"{data['party_id']} - {data['party_name']}": pid 
                           for pid, data in st.session_state.parties.items()}
            selected_party = st.selectbox("Select Party", list(party_options.keys()))
            party_id = party_options[selected_party]
            party_data = st.session_state.parties[party_id]
        
        with col2:
            party_loans = {loan['loan_id']: loan for loan in st.session_state.loans.values() 
                          if loan['party_id'] == party_id}
            if party_loans:
                loan_options = {f"{lid} - ₹{data['principal']:,.2f}": lid 
                              for lid, data in party_loans.items()}
                selected_loan = st.selectbox("Select Loan", list(loan_options.keys()))
                loan_id = loan_options[selected_loan]
                loan_data = st.session_state.loans[loan_id]
                
                gold_pledges = [gold for gold in st.session_state.gold_items.values() 
                              if gold['party_id'] == party_id]
                
                if st.button("📄 Generate Agreement", use_container_width=True):
                    st.markdown("---")
                    
                    emi_start = datetime.strptime(loan_data['emi_start_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
                    emi_end = datetime.strptime(loan_data['emi_end_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
                    
                    # Malayalam Agreement with proper Unicode support
                    agreement_text = f"""
                    <div class="print-box" style="background: white; padding: 2rem; border-radius: 10px; color: black; font-family: 'Noto Sans Malayalam', 'Malayalam', 'Arial Unicode MS', sans-serif;">
                        <h1 style="text-align: center; color: #FFD700; font-size: 2rem;">സ്വർണ്ണപ്പണയ ഉടമ്പടി</h1>
                        <p style="text-align: center; font-size: 1.1rem;">(Gold Loan Agreement)</p>
                        <hr style="border: 2px solid #FFD700;">
                        
                        <h3 style="color: #2c3e50;">1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">പേര് (Name):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data['party_name']}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data.get('spouse_name', 'N/A')}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">വിലാസം (Address):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data['address']}, {party_data['city']}, {party_data['pincode']}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">മൊബൈൽ നമ്പർ (Mobile):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data['mobile']}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">തൊഴിൽ (Occupation):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data['occupation']}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">യോഗ്യത (Qualification):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{party_data['qualification']}</td></tr>
                        </table>
                        
                        <h3 style="color: #2c3e50;">2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">തുക (Principal):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">₹{loan_data['principal']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">പലിശ നിരക്ക് (Interest Rate):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{loan_data['interest_rate']}% പ്രതിവർഷം</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">കാലാവധി (Tenure):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{loan_data['duration_months']} മാസം</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">മൊത്തം പലിശ (Total Interest):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">₹{loan_data['total_interest']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">മൊത്തം തുക (Total Amount Due):</td>
                                <td style="padding: 10px; border: 1px solid #ddd; background: #fff8e1; font-weight: bold;">₹{loan_data['total_amount']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">പ്രതിമാസ തവണ (EMI):</td>
                                <td style="padding: 10px; border: 1px solid #ddd; background: #fff8e1; font-weight: bold;">₹{loan_data['emi']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">EMI ആരംഭ തീയതി (Start Date):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{emi_start}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">EMI അവസാന തീയതി (End Date):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{emi_end}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">₹{loan_data['processing_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">അഡ്മിൻ ഫീസ് (Admin Fee):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">₹{loan_data['admin_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9; font-weight: bold;">ഡോക്യുമെന്റേഷൻ ഫീസ് (Doc Fee):</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">₹{loan_data['documentation_fee']:,.2f}</td></tr>
                            <tr><td style="padding: 10px; border: 1px solid #ddd; background: #FFD700; font-weight: bold; font-size: 1.1rem;">നൽകിയ തുക (Net Disbursed):</td>
                                <td style="padding: 10px; border: 1px solid #ddd; background: #FFD700; font-weight: bold; font-size: 1.1rem;">₹{loan_data['net_disbursement']:,.2f}</td></tr>
                        </table>
                    """
                    
                    # Add Gold Details if available
                    if gold_pledges:
                        agreement_text += """
                        <h3 style="color: #2c3e50;">3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <tr style="background: #FFD700;">
                                <th style="padding: 10px; border: 1px solid #ddd;">വിവരണം</th>
                                <th style="padding: 10px; border: 1px solid #ddd;">എണ്ണം</th>
                                <th style="padding: 10px; border: 1px solid #ddd;">ഭാരം (g)</th>
                                <th style="padding: 10px; border: 1px solid #ddd;">പ്യൂരിറ്റി</th>
                                <th style="padding: 10px; border: 1px solid #ddd;">മൂല്യം</th>
                            </tr>
                        """
                        for gold in gold_pledges:
                            agreement_text += f"""
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;">{gold['item_description']}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{gold['item_count']}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{gold['net_weight']:.2f}g</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{gold['purity']}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">₹{gold['appraised_value']:,.2f}</td>
                            </tr>
                            """
                        agreement_text += "</table>"
                    
                    # Terms and Conditions in Malayalam
                    agreement_text += """
                        <h3 style="color: #2c3e50;">4. നിബന്ധനകളും വ്യവസ്ഥകളും (Terms and Conditions)</h3>
                        <ol style="line-height: 1.8;">
                            <li>മുകളിൽ പറഞ്ഞ സ്വർണ്ണാഭരണങ്ങൾ എന്റെ സ്വന്തമാണെന്നും, അതിൽ മറ്റാർക്കും അവകാശമില്ലെന്നും ഞാൻ സാക്ഷ്യപ്പെടുത്തുന്നു.</li>
                            <li>വായ്പ തുകയും പലിശയും നിശ്ചയിച്ച കാലാവധിക്കുള്ളിൽ അടച്ചുതീർക്കുന്നതിന് ഞാൻ ബാദ്ധ്യസ്ഥനാണ്.</li>
                            <li>വായ്പ തിരിച്ചടയ്ക്കുന്നതിൽ വീഴ്ച വരുത്തിയാൽ, സ്ഥാപനത്തിന് പണയം വെച്ച സ്വർണ്ണം ലേലം ചെയ്യാനുള്ള അവകാശമുണ്ടായിരിക്കും.</li>
                            <li>പലിശ നിരക്കിലും മറ്റ് നിബന്ധനകളിലും മാറ്റം വരുത്താൻ സ്ഥാപനത്തിന് അധികാരമുണ്ട്.</li>
                            <li>വായ്പയുടെ ബാക്കി തുകയും പലിശയും പൂർണ്ണമായി അടച്ചതിന് ശേഷം മാത്രമേ സ്വർണ്ണം തിരികെ നൽകുകയുള്ളൂ.</li>
                            <li>ഈ ഉടമ്പടിയിലെ എല്ലാ നിബന്ധനകളും ഞാൻ വായിച്ചു മനസ്സിലാക്കി സമ്മതിക്കുന്നു.</li>
                        </ol>
                        <hr style="border: 1px solid #ddd; margin: 2rem 0;">
                        
                        <table style="width: 100%; margin: 2rem 0;">
                            <tr>
                                <td style="padding: 20px; width: 50%;">
                                    <strong>ഒപ്പ് (Signature):</strong> __________________<br>
                                    <span style="font-size: 0.9rem; color: #666;">(വായ്പക്കാരൻ / Borrower)</span>
                                </td>
                                <td style="padding: 20px; width: 50%;">
                                    <strong>തീയതി (Date):</strong> """ + datetime.now().strftime('%d-%m-%Y') + """
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 20px;">
                                    <strong>സ്ഥലം (Place):</strong> __________________
                                </td>
                                <td style="padding: 20px;">
                                    <strong>സാക്ഷി (Witness):</strong> __________________<br>
                                    <span style="font-size: 0.9rem; color: #666;">(പേരും ഒപ്പും / Name & Signature)</span>
                                </td>
                            </tr>
                        </table>
                        
                        <div style="background: #f0f2f6; padding: 1rem; border-radius: 5px; margin-top: 2rem; text-align: center;">
                            <p style="color: #666; font-size: 0.9rem;">
                                <strong>⚠️ Disclaimer:</strong> This is a system-generated agreement. Please verify all details before signing.
                                <br>ഈ ഉടമ്പടി സിസ്റ്റം ജനറേറ്റ് ചെയ്തതാണ്. ഒപ്പ് വയ്ക്കുന്നതിന് മുമ്പ് എല്ലാ വിശദാംശങ്ങളും പരിശോധിക്കുക.
                            </p>
                        </div>
                    </div>
                    """
                    
                    st.markdown(agreement_text, unsafe_allow_html=True)
                    
                    # Download and Print buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Agreement as HTML",
                            data=agreement_text,
                            file_name=f"Gold_Loan_Agreement_{party_data['party_name']}_{datetime.now().strftime('%Y%m%d')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    with col2:
                        st.markdown("""
                        <button onclick="window.print()" style="width:100%; padding:0.75rem; background:#FFD700; color:#1a1a2e; border:none; border-radius:5px; font-weight:bold; cursor:pointer; font-size:1rem;">
                            🖨️ Print Agreement
                        </button>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No loans found for the selected party.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🏦 Gold Loan Management System v2.0\n\nDeveloped with ❤️ using Streamlit")

st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: {len(st.session_state.parties)}")
st.sidebar.write(f"💰 Loans: {len(st.session_state.loans)}")
st.sidebar.write(f"💍 Gold Items: {len(st.session_state.gold_items)}")
st.sidebar.write(f"📝 Transactions: {len(st.session_state.transactions)}")

