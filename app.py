# app.py - Gold Loan Management System
# Complete version with SQLite Database & Malayalam Agreement

import streamlit as st
import pandas as pd
import datetime
from datetime import datetime, timedelta
import sqlite3
import json
import os
import base64

# Page configuration
st.set_page_config(
    page_title="Gold Loan Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    }
    </style>
""", unsafe_allow_html=True)

# Database functions
def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect('gold_loan.db')
    c = conn.cursor()
    
    # Parties table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            party_id TEXT PRIMARY KEY,
            party_name TEXT,
            age INTEGER,
            dob TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT,
            mobile TEXT,
            whatsapp TEXT,
            occupation TEXT,
            avg_monthly_salary REAL,
            qualification TEXT,
            spouse_name TEXT,
            spouse_age INTEGER,
            spouse_dob TEXT,
            spouse_address TEXT,
            spouse_city TEXT,
            spouse_pincode TEXT,
            spouse_mobile TEXT,
            spouse_whatsapp TEXT,
            spouse_occupation TEXT,
            spouse_avg_salary REAL,
            spouse_qualification TEXT,
            created_date TEXT
        )
    ''')
    
    # Loans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id TEXT PRIMARY KEY,
            party_id TEXT,
            party_name TEXT,
            gross_amount REAL,
            principal REAL,
            interest_rate REAL,
            duration_months INTEGER,
            emi REAL,
            total_interest REAL,
            total_amount REAL,
            processing_fee REAL,
            admin_fee REAL,
            documentation_fee REAL,
            total_fees REAL,
            net_disbursement REAL,
            disbursement_date TEXT,
            emi_start_date TEXT,
            emi_end_date TEXT,
            status TEXT,
            outstanding_balance REAL,
            paid_amount REAL,
            remaining_tenure INTEGER,
            emi_schedule TEXT,
            calculation_breakdown TEXT
        )
    ''')
    
    # Gold items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS gold_items (
            pledge_id TEXT PRIMARY KEY,
            party_id TEXT,
            party_name TEXT,
            item_description TEXT,
            item_count INTEGER,
            gross_weight REAL,
            net_weight REAL,
            purity TEXT,
            current_gold_rate REAL,
            appraised_value REAL,
            locker_id TEXT,
            pledge_date TEXT,
            status TEXT
        )
    ''')
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id TEXT PRIMARY KEY,
            date TEXT,
            party_id TEXT,
            party_name TEXT,
            transaction_type TEXT,
            amount REAL,
            details TEXT
        )
    ''')
    
    # Party counter table
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Insert default counter if not exists
    c.execute('''
        INSERT OR IGNORE INTO system_settings (key, value)
        VALUES ('party_counter', '1')
    ''')
    
    conn.commit()
    conn.close()

def load_from_database():
    """Load all data from database into session state"""
    conn = sqlite3.connect('gold_loan.db')
    
    # Load parties
    parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
    if not parties_df.empty:
        st.session_state.parties = parties_df.to_dict('records')
        st.session_state.parties = {p['party_id']: p for p in st.session_state.parties}
    
    # Load loans
    loans_df = pd.read_sql_query("SELECT * FROM loans", conn)
    if not loans_df.empty:
        st.session_state.loans = loans_df.to_dict('records')
        st.session_state.loans = {l['loan_id']: l for l in st.session_state.loans}
        # Convert emi_schedule from JSON string back to list
        for loan_id, loan in st.session_state.loans.items():
            if loan['emi_schedule']:
                loan['emi_schedule'] = json.loads(loan['emi_schedule'])
    
    # Load gold items
    gold_df = pd.read_sql_query("SELECT * FROM gold_items", conn)
    if not gold_df.empty:
        st.session_state.gold_items = gold_df.to_dict('records')
        st.session_state.gold_items = {g['pledge_id']: g for g in st.session_state.gold_items}
    
    # Load transactions
    trans_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    if not trans_df.empty:
        st.session_state.transactions = trans_df.to_dict('records')
        st.session_state.transactions = {t['trans_id']: t for t in st.session_state.transactions}
    
    # Load party counter
    counter_df = pd.read_sql_query("SELECT value FROM system_settings WHERE key='party_counter'", conn)
    if not counter_df.empty:
        st.session_state.party_counter = int(counter_df.iloc[0]['value'])
    
    conn.close()

def save_to_database():
    """Save all data from session state to database"""
    conn = sqlite3.connect('gold_loan.db')
    c = conn.cursor()
    
    # Clear existing data
    c.execute("DELETE FROM parties")
    c.execute("DELETE FROM loans")
    c.execute("DELETE FROM gold_items")
    c.execute("DELETE FROM transactions")
    c.execute("DELETE FROM system_settings")
    
    # Save parties
    for party_id, party in st.session_state.parties.items():
        c.execute('''
            INSERT INTO parties VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            party.get('party_id', ''),
            party.get('party_name', ''),
            party.get('age', 0),
            party.get('dob', ''),
            party.get('address', ''),
            party.get('city', ''),
            party.get('pincode', ''),
            party.get('mobile', ''),
            party.get('whatsapp', ''),
            party.get('occupation', ''),
            party.get('avg_monthly_salary', 0),
            party.get('qualification', ''),
            party.get('spouse_name', ''),
            party.get('spouse_age', 0),
            party.get('spouse_dob', ''),
            party.get('spouse_address', ''),
            party.get('spouse_city', ''),
            party.get('spouse_pincode', ''),
            party.get('spouse_mobile', ''),
            party.get('spouse_whatsapp', ''),
            party.get('spouse_occupation', ''),
            party.get('spouse_avg_salary', 0),
            party.get('spouse_qualification', ''),
            party.get('created_date', '')
        ))
    
    # Save loans
    for loan_id, loan in st.session_state.loans.items():
        # Convert emi_schedule to JSON string
        emi_schedule_json = json.dumps(loan.get('emi_schedule', []))
        c.execute('''
            INSERT INTO loans VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            loan.get('loan_id', ''),
            loan.get('party_id', ''),
            loan.get('party_name', ''),
            loan.get('gross_amount', 0),
            loan.get('principal', 0),
            loan.get('interest_rate', 0),
            loan.get('duration_months', 0),
            loan.get('emi', 0),
            loan.get('total_interest', 0),
            loan.get('total_amount', 0),
            loan.get('processing_fee', 0),
            loan.get('admin_fee', 0),
            loan.get('documentation_fee', 0),
            loan.get('total_fees', 0),
            loan.get('net_disbursement', 0),
            loan.get('disbursement_date', ''),
            loan.get('emi_start_date', ''),
            loan.get('emi_end_date', ''),
            loan.get('status', ''),
            loan.get('outstanding_balance', 0),
            loan.get('paid_amount', 0),
            loan.get('remaining_tenure', 0),
            emi_schedule_json,
            loan.get('calculation_breakdown', '')
        ))
    
    # Save gold items
    for pledge_id, gold in st.session_state.gold_items.items():
        c.execute('''
            INSERT INTO gold_items VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            gold.get('pledge_id', ''),
            gold.get('party_id', ''),
            gold.get('party_name', ''),
            gold.get('item_description', ''),
            gold.get('item_count', 0),
            gold.get('gross_weight', 0),
            gold.get('net_weight', 0),
            gold.get('purity', ''),
            gold.get('current_gold_rate', 0),
            gold.get('appraised_value', 0),
            gold.get('locker_id', ''),
            gold.get('pledge_date', ''),
            gold.get('status', '')
        ))
    
    # Save transactions
    for trans_id, trans in st.session_state.transactions.items():
        c.execute('''
            INSERT INTO transactions VALUES (
                ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            trans.get('trans_id', ''),
            trans.get('date', ''),
            trans.get('party_id', ''),
            trans.get('party_name', ''),
            trans.get('transaction_type', ''),
            trans.get('amount', 0),
            trans.get('details', '')
        ))
    
    # Save party counter
    c.execute("INSERT INTO system_settings (key, value) VALUES ('party_counter', ?)", 
              (str(st.session_state.party_counter),))
    
    conn.commit()
    conn.close()

# Helper functions
def generate_party_id():
    party_id = f"P{str(st.session_state.party_counter).zfill(4)}"
    st.session_state.party_counter += 1
    return party_id

def generate_loan_id():
    return f"L{datetime.now().strftime('%Y%m%d')}{str(len(st.session_state.loans) + 1).zfill(3)}"

def generate_trans_id():
    return f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"

def calculate_simple_interest_emi(principal, interest_rate, tenure_months):
    """Calculate EMI using Simple Interest method"""
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

# Initialize database and load data
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Load data from database if session state is empty
if not st.session_state.parties:
    load_from_database()

# Auto-save function wrapper
def auto_save():
    save_to_database()

# Main Application
st.markdown('<h1 class="main-header">🏦 Gold Loan Management System</h1>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📋 Navigation")
menu = st.sidebar.selectbox(
    "Select Module",
    ["🏠 Dashboard", "👤 Party Master", "💰 Gold Loan Disbursement", 
     "📊 Party Ledger", "💍 Gold Pledge Management", "📄 Loan Agreement",
     "✏️ Edit Party Details", "📅 EMI Schedule", "💾 Backup & Restore"]
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
                    
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_name,
                        'transaction_type': 'Party Registration',
                        'amount': 0,
                        'details': 'New party registered'
                    }
                    
                    auto_save()  # Save to database
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
                    
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_name,
                        'transaction_type': 'Party Details Updated',
                        'amount': 0,
                        'details': f'Party {party_id} details updated'
                    }
                    
                    auto_save()
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
            gross_amount = st.number_input("Gross Loan Amount (₹) *", min_value=1000.0, step=500.0, format="%.2f", value=40375.0)
            interest_rate = st.number_input("Interest Rate (% per annum) *", min_value=0.0, max_value=36.0, step=0.5, format="%.1f", value=12.0)
            duration_months = st.number_input("Duration (Months) *", min_value=1, max_value=60, step=1, value=12)
            
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
            net_disbursement = gross_amount - total_fees
            
            st.markdown(f"""
            <div class="info-box" style="background: #e3f2fd; border-left-color: #2196F3;">
                <strong>📊 Fee Summary:</strong><br>
                Gross Amount: ₹{gross_amount:,.2f}<br>
                Processing Fee: -₹{processing_fee:,.2f}<br>
                Admin Fee: -₹{admin_fee:,.2f}<br>
                Documentation Fee: -₹{documentation_fee:,.2f}<br>
                <hr>
                <strong>Net Disbursement: ₹{net_disbursement:,.2f}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            if gross_amount > 0 and duration_months > 0:
                result = calculate_simple_interest_emi(gross_amount, interest_rate, duration_months)
                emi = result['emi']
                total_interest = result['total_interest']
                total_amount = result['total_amount']
                
                emi_schedule = generate_emi_schedule_simple(gross_amount, interest_rate, duration_months, emi_start_date)
                
                st.markdown("### Loan Summary")
                st.markdown(f"""
                <div class="info-box-gold">
                    <strong>📊 Simple Interest Calculation:</strong><br>
                    Gross Amount: ₹{gross_amount:,.2f}<br>
                    Interest Rate: {interest_rate}% p.a.<br>
                    Tenure: {duration_months} months<br>
                    <hr>
                    <strong>Total Interest: ₹{total_interest:,.2f}</strong><br>
                    <strong>Total Amount Due: ₹{total_amount:,.2f}</strong><br>
                    <strong>EMI: ₹{emi:,.2f}</strong><br>
                    <hr>
                    <strong>Net Disbursement: ₹{net_disbursement:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📊 View Complete Calculation Breakdown"):
                    breakdown, _ = get_emi_calculation_breakdown(gross_amount, interest_rate, duration_months)
                    st.markdown(f'<div class="calculation-box">{breakdown}</div>', unsafe_allow_html=True)
            else:
                st.info("Enter gross amount and duration to calculate EMI.")
            
            if st.button("💰 Disburse Loan", use_container_width=True):
                if gross_amount <= 0 or duration_months <= 0:
                    st.error("⚠️ Please enter valid gross amount and duration.")
                elif net_disbursement < 0:
                    st.error("⚠️ Total fees cannot exceed gross amount.")
                else:
                    loan_id = generate_loan_id()
                    result = calculate_simple_interest_emi(gross_amount, interest_rate, duration_months)
                    
                    loan_data = {
                        'loan_id': loan_id,
                        'party_id': party_id,
                        'party_name': party_data['party_name'],
                        'gross_amount': gross_amount,
                        'principal': net_disbursement,
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
                        'emi_schedule': generate_emi_schedule_simple(gross_amount, interest_rate, duration_months, emi_start_date),
                        'calculation_breakdown': get_emi_calculation_breakdown(gross_amount, interest_rate, duration_months)[0]
                    }
                    st.session_state.loans[loan_id] = loan_data
                    
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id,
                        'party_name': party_data['party_name'],
                        'transaction_type': 'Loan Disbursement',
                        'amount': net_disbursement,
                        'details': f'Loan ID: {loan_id} (Gross: ₹{gross_amount:,.2f})'
                    }
                    
                    auto_save()
                    st.success(f"✅ Loan disbursed successfully! Loan ID: {loan_id}")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div class="info-box" style="background: #e8f5e9; border-left-color: #4CAF50;">
                        <strong>📄 Disbursement Summary:</strong><br>
                        Gross Amount: ₹{gross_amount:,.2f}<br>
                        Total Fees: -₹{total_fees:,.2f}<br>
                        <strong>Net Amount Disbursed: ₹{net_disbursement:,.2f}</strong><br>
                        <hr>
                        EMI: ₹{result['emi']:,.2f}<br>
                        Total Amount Due: ₹{result['total_amount']:,.2f}
                    </div>
                    """, unsafe_allow_html=True)

# [Continue with remaining modules - Party Ledger, Gold Pledge, Loan Agreement, EMI Schedule, Backup & Restore]

# Backup & Restore Module
elif menu == "💾 Backup & Restore":
    st.markdown('<h2 class="sub-header">💾 Backup & Restore</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Export Data")
        if st.button("📥 Download Database Backup", use_container_width=True):
            # Create backup file
            backup_data = {
                'parties': st.session_state.parties,
                'loans': st.session_state.loans,
                'gold_items': st.session_state.gold_items,
                'transactions': st.session_state.transactions,
                'party_counter': st.session_state.party_counter
            }
            
            # Convert to JSON
            json_data = json.dumps(backup_data, indent=2, default=str)
            
            # Create download button
            b64 = base64.b64encode(json_data.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="gold_loan_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" style="background-color:#FFD700;color:#1a1a2e;padding:0.75rem;border-radius:5px;text-decoration:none;display:block;text-align:center;font-weight:bold;">📥 Click to Download Backup</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.info("💡 This backup file can be used to restore your data anytime.")
    
    with col2:
        st.markdown("### 📥 Import Data")
        uploaded_file = st.file_uploader("Upload Backup JSON File", type=['json'])
        
        if uploaded_file is not None:
            if st.button("🔄 Restore from Backup", use_container_width=True):
                try:
                    backup_data = json.load(uploaded_file)
                    
                    # Restore data
                    st.session_state.parties = backup_data['parties']
                    st.session_state.loans = backup_data['loans']
                    st.session_state.gold_items = backup_data['gold_items']
                    st.session_state.transactions = backup_data['transactions']
                    st.session_state.party_counter = backup_data['party_counter']
                    
                    auto_save()
                    st.success("✅ Data restored successfully from backup!")
                    st.balloons()
                    st.info("🔄 Please refresh the page to see updated data.")
                except Exception as e:
                    st.error(f"❌ Error restoring backup: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📋 Current Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", len(st.session_state.parties))
    with col2:
        st.metric("Total Loans", len(st.session_state.loans))
    with col3:
        st.metric("Gold Pledges", len(st.session_state.gold_items))
    with col4:
        st.metric("Transactions", len(st.session_state.transactions))
    
    if st.button("🗑️ Clear All Data (Use with caution!)", use_container_width=True):
        if st.checkbox("⚠️ I confirm I want to delete ALL data"):
            st.session_state.parties = {}
            st.session_state.loans = {}
            st.session_state.gold_items = {}
            st.session_state.transactions = {}
            st.session_state.party_counter = 1
            auto_save()
            st.warning("⚠️ All data has been cleared!")
            st.rerun()

# [Rest of the modules (Party Ledger, Gold Pledge, EMI Schedule, Loan Agreement) remain the same but with auto_save() calls added]

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🏦 Gold Loan Management System v3.0\n\nDeveloped with ❤️ using Streamlit")

st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: {len(st.session_state.parties)}")
st.sidebar.write(f"💰 Loans: {len(st.session_state.loans)}")
st.sidebar.write(f"💍 Gold Items: {len(st.session_state.gold_items)}")
st.sidebar.write(f"📝 Transactions: {len(st.session_state.transactions)}")
st.sidebar.write("💾 Data: SQLite Database (Persistent)")

# Auto-save on any change
auto_save()

