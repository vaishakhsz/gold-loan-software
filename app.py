# app.py - Gold Loan Management System
# Professional Multi-Page Version

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

# Custom CSS for Professional UI
st.markdown("""
    <style>
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        color: #FFD700;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        color: #f0e6d3;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #2c3e50, #34495e);
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        border-left: 5px solid #FFD700;
    }
    
    .sub-section-header {
        font-size: 1.3rem;
        color: #ecf0f1;
        padding: 0.5rem 1rem;
        background: #34495e;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #FFD700;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .info-box-gold {
        background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(255,215,0,0.2);
    }
    
    .info-box-blue {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(33,150,243,0.2);
    }
    
    .info-box-green {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(76,175,80,0.2);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FFD700, #f0c000);
        color: #1a1a2e;
        font-weight: bold;
        padding: 0.6rem;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(255,215,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255,215,0,0.4);
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border-bottom: 3px solid #FFD700;
    }
    .metric-card .number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FFD700;
    }
    .metric-card .label {
        font-size: 0.9rem;
        color: #b0b0b0;
        margin-top: 0.3rem;
    }
    
    /* Print Box */
    .print-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        color: black;
        border: 2px solid #FFD700;
        font-family: 'Noto Sans Malayalam', 'Malayalam', sans-serif;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Calculation Box */
    .calculation-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 0.8rem 0;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 8px rgba(76,175,80,0.2);
    }
    
    /* Edit Highlight */
    .edit-highlight {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    /* Agreement Page Styles */
    .agreement-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .agreement-title {
        text-align: center;
        color: #FFD700;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .agreement-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Print Styles */
    @media print {
        .no-print { display: none !important; }
        .print-box { border: none !important; box-shadow: none !important; }
        .stApp { background: white !important; }
        .main-header { background: white !important; color: #FFD700 !important; }
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #2c3e50;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        color: #b0b0b0;
    }
    .stTabs [aria-selected="true"] {
        background: #FFD700;
        color: #1a1a2e;
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, #d4edda, #b7eb8f);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        color: #155724;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #1a1a2e;
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
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'show_agreement' not in st.session_state:
    st.session_state.show_agreement = False
if 'agreement_data' not in st.session_state:
    st.session_state.agreement_data = None

# Database functions
def init_database():
    try:
        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS parties (
            party_id TEXT PRIMARY KEY, party_name TEXT, age INTEGER, dob TEXT,
            address TEXT, city TEXT, pincode TEXT, mobile TEXT, whatsapp TEXT,
            occupation TEXT, avg_monthly_salary REAL, qualification TEXT,
            spouse_name TEXT, spouse_age INTEGER, spouse_dob TEXT,
            spouse_address TEXT, spouse_city TEXT, spouse_pincode TEXT,
            spouse_mobile TEXT, spouse_whatsapp TEXT, spouse_occupation TEXT,
            spouse_avg_salary REAL, spouse_qualification TEXT, created_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS loans (
            loan_id TEXT PRIMARY KEY, party_id TEXT, party_name TEXT,
            gross_amount REAL, principal REAL, interest_rate REAL,
            duration_months INTEGER, emi REAL, total_interest REAL,
            total_amount REAL, processing_fee REAL, admin_fee REAL,
            documentation_fee REAL, total_fees REAL, net_disbursement REAL,
            disbursement_date TEXT, emi_start_date TEXT, emi_end_date TEXT,
            status TEXT, outstanding_balance REAL, paid_amount REAL,
            remaining_tenure INTEGER, emi_schedule TEXT, calculation_breakdown TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS gold_items (
            pledge_id TEXT PRIMARY KEY, party_id TEXT, party_name TEXT,
            item_description TEXT, item_count INTEGER, gross_weight REAL,
            net_weight REAL, purity TEXT, current_gold_rate REAL,
            appraised_value REAL, locker_id TEXT, pledge_date TEXT, status TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            trans_id TEXT PRIMARY KEY, date TEXT, party_id TEXT,
            party_name TEXT, transaction_type TEXT, amount REAL, details TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY, value TEXT
        )''')
        c.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('party_counter', '1')")
        conn.commit()
        conn.close()
        return True
    except:
        return False

def load_from_database():
    try:
        conn = sqlite3.connect('gold_loan.db')
        try:
            parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
            if not parties_df.empty:
                st.session_state.parties = parties_df.to_dict('records')
                st.session_state.parties = {p['party_id']: p for p in st.session_state.parties}
        except:
            pass
        try:
            loans_df = pd.read_sql_query("SELECT * FROM loans", conn)
            if not loans_df.empty:
                st.session_state.loans = loans_df.to_dict('records')
                st.session_state.loans = {l['loan_id']: l for l in st.session_state.loans}
                for loan_id, loan in st.session_state.loans.items():
                    if loan.get('emi_schedule'):
                        try:
                            loan['emi_schedule'] = json.loads(loan['emi_schedule'])
                        except:
                            loan['emi_schedule'] = []
        except:
            pass
        try:
            gold_df = pd.read_sql_query("SELECT * FROM gold_items", conn)
            if not gold_df.empty:
                st.session_state.gold_items = gold_df.to_dict('records')
                st.session_state.gold_items = {g['pledge_id']: g for g in st.session_state.gold_items}
        except:
            pass
        try:
            trans_df = pd.read_sql_query("SELECT * FROM transactions", conn)
            if not trans_df.empty:
                st.session_state.transactions = trans_df.to_dict('records')
                st.session_state.transactions = {t['trans_id']: t for t in st.session_state.transactions}
        except:
            pass
        try:
            counter_df = pd.read_sql_query("SELECT value FROM system_settings WHERE key='party_counter'", conn)
            if not counter_df.empty:
                st.session_state.party_counter = int(counter_df.iloc[0]['value'])
        except:
            pass
        conn.close()
        return True
    except:
        return False

def save_to_database():
    try:
        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute("DELETE FROM parties")
        c.execute("DELETE FROM loans")
        c.execute("DELETE FROM gold_items")
        c.execute("DELETE FROM transactions")
        c.execute("DELETE FROM system_settings")
        for party_id, party in st.session_state.parties.items():
            c.execute('''INSERT INTO parties VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                party.get('party_id',''), party.get('party_name',''), party.get('age',0),
                party.get('dob',''), party.get('address',''), party.get('city',''),
                party.get('pincode',''), party.get('mobile',''), party.get('whatsapp',''),
                party.get('occupation',''), party.get('avg_monthly_salary',0),
                party.get('qualification',''), party.get('spouse_name',''), party.get('spouse_age',0),
                party.get('spouse_dob',''), party.get('spouse_address',''), party.get('spouse_city',''),
                party.get('spouse_pincode',''), party.get('spouse_mobile',''), party.get('spouse_whatsapp',''),
                party.get('spouse_occupation',''), party.get('spouse_avg_salary',0),
                party.get('spouse_qualification',''), party.get('created_date','')
            ))
        for loan_id, loan in st.session_state.loans.items():
            emi_schedule_json = json.dumps(loan.get('emi_schedule', []))
            c.execute('''INSERT INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                loan.get('loan_id',''), loan.get('party_id',''), loan.get('party_name',''),
                loan.get('gross_amount',0), loan.get('principal',0), loan.get('interest_rate',0),
                loan.get('duration_months',0), loan.get('emi',0), loan.get('total_interest',0),
                loan.get('total_amount',0), loan.get('processing_fee',0), loan.get('admin_fee',0),
                loan.get('documentation_fee',0), loan.get('total_fees',0), loan.get('net_disbursement',0),
                loan.get('disbursement_date',''), loan.get('emi_start_date',''), loan.get('emi_end_date',''),
                loan.get('status',''), loan.get('outstanding_balance',0), loan.get('paid_amount',0),
                loan.get('remaining_tenure',0), emi_schedule_json, loan.get('calculation_breakdown','')
            ))
        for pledge_id, gold in st.session_state.gold_items.items():
            c.execute('''INSERT INTO gold_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                gold.get('pledge_id',''), gold.get('party_id',''), gold.get('party_name',''),
                gold.get('item_description',''), gold.get('item_count',0), gold.get('gross_weight',0),
                gold.get('net_weight',0), gold.get('purity',''), gold.get('current_gold_rate',0),
                gold.get('appraised_value',0), gold.get('locker_id',''), gold.get('pledge_date',''),
                gold.get('status','')
            ))
        for trans_id, trans in st.session_state.transactions.items():
            c.execute('''INSERT INTO transactions VALUES (?,?,?,?,?,?,?)''', (
                trans.get('trans_id',''), trans.get('date',''), trans.get('party_id',''),
                trans.get('party_name',''), trans.get('transaction_type',''), trans.get('amount',0),
                trans.get('details','')
            ))
        c.execute("INSERT INTO system_settings (key, value) VALUES ('party_counter', ?)", 
                  (str(st.session_state.party_counter),))
        conn.commit()
        conn.close()
        return True
    except:
        return False

if not st.session_state.db_initialized:
    if init_database():
        st.session_state.db_initialized = True

if not st.session_state.data_loaded:
    if load_from_database():
        st.session_state.data_loaded = True

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

def auto_save():
    try:
        save_to_database()
    except:
        pass

# ============ SIDEBAR NAVIGATION ============
st.sidebar.title("📋 Navigation")

main_menu = st.sidebar.selectbox(
    "Select Module",
    [
        "🏠 Dashboard",
        "👤 Party Master",
        "✏️ Edit Party Details",
        "💰 Gold Loan Management",
        "💍 Gold Pledge Management",
        "📄 Loan Agreement",
        "📅 EMI Schedule",
        "💾 Backup & Restore"
    ]
)

if main_menu == "💰 Gold Loan Management":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Sub-Modules")
    sub_menu = st.sidebar.radio(
        "Select Action",
        ["💸 Loan Disbursement", "📊 Party Ledger"],
        index=0
    )
    menu = sub_menu
else:
    menu = main_menu

# System Stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.write(f"👤 Parties: {len(st.session_state.parties)}")
st.sidebar.write(f"💰 Loans: {len(st.session_state.loans)}")
st.sidebar.write(f"💍 Gold: {len(st.session_state.gold_items)}")
st.sidebar.write(f"📝 Transactions: {len(st.session_state.transactions)}")

st.sidebar.markdown("---")
st.sidebar.info("🏦 Gold Loan System v3.0\n\n💾 Data: SQLite (Persistent)")

# Main Header
st.markdown('<div class="main-header">🏦 Gold Loan Management System</div>', unsafe_allow_html=True)

# ============ MODULE: DASHBOARD ============
if menu == "🏠 Dashboard":
    st.markdown('<div class="section-header">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="number">{len(st.session_state.parties)}</div>
            <div class="label">👤 Total Customers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="number">{len(st.session_state.loans)}</div>
            <div class="label">💰 Total Loans</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_principal = sum([loan.get('principal', 0) for loan in st.session_state.loans.values()]) if st.session_state.loans else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="number">₹{total_principal:,.0f}</div>
            <div class="label">💵 Total Disbursed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_gold = sum([item.get('net_weight', 0) for item in st.session_state.gold_items.values()]) if st.session_state.gold_items else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="number">{total_gold:.1f}g</div>
            <div class="label">💍 Gold Pledged</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-section-header">📈 Recent Activity</div>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        recent = list(st.session_state.transactions.values())[-10:][::-1]
        df = pd.DataFrame(recent)
        st.dataframe(df[['date', 'party_name', 'transaction_type', 'amount']], 
                    use_container_width=True, 
                    column_config={
                        'date': 'Date',
                        'party_name': 'Customer',
                        'transaction_type': 'Type',
                        'amount': st.column_config.NumberColumn('Amount', format='₹%.2f')
                    })
    else:
        st.info("No recent activity. Start by adding a party!")

# ============ MODULE: PARTY MASTER ============
elif menu == "👤 Party Master":
    st.markdown('<div class="section-header">👤 Party Master Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Party", "📋 View All Parties", "🔍 Search Party"])
    
    with tab1:
        with st.form("party_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Personal Details")
                party_name = st.text_input("Full Name *", placeholder="Enter full name")
                age = st.number_input("Age", min_value=18, max_value=100, step=1, value=25)
                dob = st.date_input("Date of Birth", max_value=datetime.now())
                occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"])
                avg_monthly_salary = st.number_input("Average Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=0.0)
                qualification = st.text_input("Qualification")
                
                st.markdown("#### Contact Details")
                address = st.text_area("Address", placeholder="Enter complete address")
                city = st.text_input("City")
                pincode = st.text_input("Pincode")
                mobile = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
                whatsapp = st.text_input("WhatsApp Number", placeholder="10-digit number")
            
            with col2:
                st.markdown("#### Spouse Details")
                spouse_name = st.text_input("Spouse's Full Name")
                spouse_age = st.number_input("Spouse's Age", min_value=18, max_value=100, step=1, value=25)
                spouse_dob = st.date_input("Spouse's Date of Birth", max_value=datetime.now())
                spouse_occupation = st.selectbox("Spouse's Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"])
                spouse_avg_salary = st.number_input("Spouse's Avg Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=0.0)
                spouse_qualification = st.text_input("Spouse's Qualification")
                
                st.markdown("#### Spouse's Contact Details")
                spouse_address = st.text_area("Spouse's Address", placeholder="If different from above")
                spouse_city = st.text_input("Spouse's City")
                spouse_pincode = st.text_input("Spouse's Pincode")
                spouse_mobile = st.text_input("Spouse's Mobile Number")
                spouse_whatsapp = st.text_input("Spouse's WhatsApp Number")
            
            submitted = st.form_submit_button("💾 Save Party")
            
            if submitted:
                if not party_name or not mobile:
                    st.error("⚠️ Please fill in Name and Mobile Number.")
                else:
                    party_id = generate_party_id()
                    st.session_state.parties[party_id] = {
                        'party_id': party_id, 'party_name': party_name, 'age': age,
                        'dob': dob.strftime("%Y-%m-%d"), 'address': address, 'city': city,
                        'pincode': pincode, 'mobile': mobile, 'whatsapp': whatsapp or mobile,
                        'occupation': occupation, 'avg_monthly_salary': avg_monthly_salary,
                        'qualification': qualification, 'spouse_name': spouse_name,
                        'spouse_age': spouse_age, 'spouse_dob': spouse_dob.strftime("%Y-%m-%d") if spouse_dob else None,
                        'spouse_address': spouse_address or address, 'spouse_city': spouse_city or city,
                        'spouse_pincode': spouse_pincode or pincode, 'spouse_mobile': spouse_mobile,
                        'spouse_whatsapp': spouse_whatsapp, 'spouse_occupation': spouse_occupation,
                        'spouse_avg_salary': spouse_avg_salary, 'spouse_qualification': spouse_qualification,
                        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id, 'party_name': party_name,
                        'transaction_type': 'Party Registration', 'amount': 0,
                        'details': 'New party registered'
                    }
                    auto_save()
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Party <strong>{party_name}</strong> registered successfully!<br>
                        <small>Party ID: {party_id}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
    
    with tab2:
        if st.session_state.parties:
            df = pd.DataFrame(st.session_state.parties.values())
            st.dataframe(df[['party_id', 'party_name', 'age', 'mobile', 'city', 'occupation', 'avg_monthly_salary']], 
                        use_container_width=True,
                        column_config={
                            'party_id': 'Party ID',
                            'party_name': 'Name',
                            'age': 'Age',
                            'mobile': 'Mobile',
                            'city': 'City',
                            'occupation': 'Occupation',
                            'avg_monthly_salary': st.column_config.NumberColumn('Salary', format='₹%.2f')
                        })
        else:
            st.info("📭 No parties registered yet. Use the 'Add New Party' tab to get started.")
    
    with tab3:
        search = st.text_input("🔍 Search by Name or Party ID", placeholder="Type to search...")
        if search:
            results = [p for p in st.session_state.parties.values() 
                      if search.lower() in p.get('party_name','').lower() or search.lower() in p.get('party_id','').lower()]
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df[['party_id', 'party_name', 'age', 'mobile', 'city', 'occupation']], 
                            use_container_width=True)
            else:
                st.warning("No matching parties found.")

# ============ MODULE: EDIT PARTY ============
elif menu == "✏️ Edit Party Details":
    st.markdown('<div class="section-header">✏️ Edit Party Details</div>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.info("📭 No parties available to edit.")
    else:
        party_options = {f"{p['party_id']} - {p['party_name']}": pid for pid, p in st.session_state.parties.items()}
        selected = st.selectbox("Select Party to Edit", list(party_options.keys()))
        party_id = party_options[selected]
        party = st.session_state.parties[party_id]
        
        st.markdown(f'<div class="edit-highlight">✏️ Editing: {party["party_name"]} ({party_id})</div>', unsafe_allow_html=True)
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Personal Details")
                name = st.text_input("Full Name *", value=party['party_name'])
                age = st.number_input("Age", min_value=18, max_value=100, step=1, value=int(party['age']))
                dob = st.date_input("Date of Birth", value=datetime.strptime(party['dob'], "%Y-%m-%d") if party['dob'] else datetime.now())
                occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"], 
                                        index=["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other"].index(party['occupation']))
                salary = st.number_input("Average Monthly Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(party['avg_monthly_salary']))
                qual = st.text_input("Qualification", value=party['qualification'])
                
                st.markdown("#### Contact Details")
                address = st.text_area("Address", value=party['address'])
                city = st.text_input("City", value=party['city'])
                pincode = st.text_input("Pincode", value=party['pincode'])
                mobile = st.text_input("Mobile Number *", value=party['mobile'])
                whatsapp = st.text_input("WhatsApp Number", value=party['whatsapp'])
            
            with col2:
                st.markdown("#### Spouse Details")
                spouse_name = st.text_input("Spouse's Full Name", value=party.get('spouse_name', ''))
                spouse_age = st.number_input("Spouse's Age", min_value=18, max_value=100, step=1, value=int(party.get('spouse_age', 25)))
                spouse_dob = st.date_input("Spouse's DOB", value=datetime.strptime(party['spouse_dob'], "%Y-%m-%d") if party.get('spouse_dob') else datetime.now())
                spouse_occupation = st.selectbox("Spouse's Occupation", ["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"],
                                               index=["Salaried", "Self-Employed", "Business", "Professional", "Retired", "Student", "Other", "Homemaker"].index(party.get('spouse_occupation', 'Homemaker')))
                spouse_salary = st.number_input("Spouse's Avg Salary (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(party.get('spouse_avg_salary', 0)))
                spouse_qual = st.text_input("Spouse's Qualification", value=party.get('spouse_qualification', ''))
                
                st.markdown("#### Spouse's Contact Details")
                spouse_address = st.text_area("Spouse's Address", value=party.get('spouse_address', ''))
                spouse_city = st.text_input("Spouse's City", value=party.get('spouse_city', ''))
                spouse_pincode = st.text_input("Spouse's Pincode", value=party.get('spouse_pincode', ''))
                spouse_mobile = st.text_input("Spouse's Mobile", value=party.get('spouse_mobile', ''))
                spouse_whatsapp = st.text_input("Spouse's WhatsApp", value=party.get('spouse_whatsapp', ''))
            
            if st.form_submit_button("💾 Update Party Details"):
                if not name or not mobile:
                    st.error("⚠️ Please fill in Name and Mobile Number.")
                else:
                    party['party_name'] = name
                    party['age'] = age
                    party['dob'] = dob.strftime("%Y-%m-%d")
                    party['address'] = address
                    party['city'] = city
                    party['pincode'] = pincode
                    party['mobile'] = mobile
                    party['whatsapp'] = whatsapp or mobile
                    party['occupation'] = occupation
                    party['avg_monthly_salary'] = salary
                    party['qualification'] = qual
                    party['spouse_name'] = spouse_name
                    party['spouse_age'] = spouse_age
                    party['spouse_dob'] = spouse_dob.strftime("%Y-%m-%d") if spouse_dob else None
                    party['spouse_address'] = spouse_address or address
                    party['spouse_city'] = spouse_city or city
                    party['spouse_pincode'] = spouse_pincode or pincode
                    party['spouse_mobile'] = spouse_mobile
                    party['spouse_whatsapp'] = spouse_whatsapp
                    party['spouse_occupation'] = spouse_occupation
                    party['spouse_avg_salary'] = spouse_salary
                    party['spouse_qualification'] = spouse_qual
                    st.session_state.parties[party_id] = party
                    
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id, 'party_name': name,
                        'transaction_type': 'Party Updated', 'amount': 0,
                        'details': f'Party {party_id} details updated'
                    }
                    auto_save()
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Party <strong>{name}</strong> details updated successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()

# ============ MODULE: LOAN DISBURSEMENT ============
elif menu == "💸 Loan Disbursement":
    st.markdown('<div class="section-header">💰 Loan Disbursement</div>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.info("📭 Please add a party first before disbursing a loan.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Select Customer")
            party_options = {f"{p['party_id']} - {p['party_name']}": pid for pid, p in st.session_state.parties.items()}
            selected = st.selectbox("Select Party", list(party_options.keys()))
            party_id = party_options[selected]
            party = st.session_state.parties[party_id]
            
            st.markdown(f"""
            <div class="info-box">
                <strong>👤 Customer:</strong> {party['party_name']}<br>
                <strong>📱 Mobile:</strong> {party['mobile']}<br>
                <strong>📍 City:</strong> {party['city']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Loan Details")
            gross = st.number_input("Gross Loan Amount (₹)", min_value=1000.0, value=40375.0, step=500.0, format="%.2f")
            rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, max_value=36.0, value=12.0, step=0.5)
            months = st.number_input("Duration (Months)", min_value=1, max_value=60, value=12, step=1)
            
            st.markdown("#### EMI Schedule")
            start_date = st.date_input("EMI Start Date", value=datetime.now() + timedelta(days=30))
            end_date = start_date + timedelta(days=30 * months)
            st.info(f"📅 EMI End Date: **{end_date.strftime('%d-%m-%Y')}**")
        
        with col2:
            st.markdown("#### Fee Structure")
            processing = st.number_input("Processing Fee (₹)", min_value=0.0, value=900.0, step=50.0, format="%.2f")
            admin = st.number_input("Admin Fee (₹)", min_value=0.0, value=0.0, step=50.0, format="%.2f")
            doc = st.number_input("Documentation Fee (₹)", min_value=0.0, value=0.0, step=50.0, format="%.2f")
            
            total_fees = processing + admin + doc
            net = gross - total_fees
            
            st.markdown(f"""
            <div class="info-box-blue">
                <strong>📊 Fee Summary</strong><br>
                Gross Amount: ₹{gross:,.2f}<br>
                Processing Fee: -₹{processing:,.2f}<br>
                Admin Fee: -₹{admin:,.2f}<br>
                Documentation: -₹{doc:,.2f}<br>
                <hr>
                <strong>Net Disbursement: ₹{net:,.2f}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            if gross > 0 and months > 0:
                result = calculate_simple_interest_emi(gross, rate, months)
                
                st.markdown(f"""
                <div class="info-box-gold">
                    <strong>📊 Loan Summary</strong><br>
                    Total Interest: ₹{result['total_interest']:,.2f}<br>
                    Total Amount Due: ₹{result['total_amount']:,.2f}<br>
                    <strong>EMI: ₹{result['emi']:,.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📊 View Calculation Breakdown"):
                    breakdown = f"""
                    <div class="calculation-box">
                    <strong>Simple Interest Calculation:</strong><br><br>
                    Principal = ₹{gross:,.2f}<br>
                    Rate = {rate}% p.a.<br>
                    Time = {months} months = {months/12:.1f} years<br><br>
                    <strong>Total Interest</strong> = ₹{gross:,.2f} × {rate}% × {months/12:.1f}<br>
                    = <strong>₹{result['total_interest']:,.2f}</strong><br><br>
                    <strong>Total Amount</strong> = ₹{gross:,.2f} + ₹{result['total_interest']:,.2f}<br>
                    = <strong>₹{result['total_amount']:,.2f}</strong><br><br>
                    <strong>EMI</strong> = ₹{result['total_amount']:,.2f} / {months}<br>
                    = <strong>₹{result['emi']:,.2f}</strong>
                    </div>
                    """
                    st.markdown(breakdown, unsafe_allow_html=True)
            
            if st.button("💰 Disburse Loan", use_container_width=True):
                if gross <= 0 or months <= 0:
                    st.error("⚠️ Please enter valid values.")
                elif net < 0:
                    st.error("⚠️ Total fees cannot exceed gross amount.")
                else:
                    loan_id = generate_loan_id()
                    result = calculate_simple_interest_emi(gross, rate, months)
                    schedule = generate_emi_schedule_simple(gross, rate, months, start_date)
                    
                    st.session_state.loans[loan_id] = {
                        'loan_id': loan_id, 'party_id': party_id, 'party_name': party['party_name'],
                        'gross_amount': gross, 'principal': net, 'interest_rate': rate,
                        'duration_months': months, 'emi': result['emi'],
                        'total_interest': result['total_interest'], 'total_amount': result['total_amount'],
                        'processing_fee': processing, 'admin_fee': admin, 'documentation_fee': doc,
                        'total_fees': total_fees, 'net_disbursement': net,
                        'disbursement_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'emi_start_date': start_date.strftime("%Y-%m-%d"),
                        'emi_end_date': end_date.strftime("%Y-%m-%d"),
                        'status': 'Active', 'outstanding_balance': result['total_amount'],
                        'paid_amount': 0, 'remaining_tenure': months,
                        'emi_schedule': schedule,
                        'calculation_breakdown': ''
                    }
                    trans_id = generate_trans_id()
                    st.session_state.transactions[trans_id] = {
                        'trans_id': trans_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'party_id': party_id, 'party_name': party['party_name'],
                        'transaction_type': 'Loan Disbursement', 'amount': net,
                        'details': f'Loan ID: {loan_id}'
                    }
                    auto_save()
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Loan <strong>{loan_id}</strong> disbursed successfully!<br>
                        <small>Net Amount: ₹{net:,.2f} | EMI: ₹{result['emi']:,.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()

# ============ MODULE: PARTY LEDGER ============
elif menu == "📊 Party Ledger":
    st.markdown('<div class="section-header">📊 Party Ledger</div>', unsafe_allow_html=True)
    
    if not st.session_state.parties:
        st.info("📭 No parties available.")
    else:
        party_options = {f"{p['party_id']} - {p['party_name']}": pid for pid, p in st.session_state.parties.items()}
        selected = st.selectbox("Select Party", list(party_options.keys()))
        party_id = party_options[selected]
        party = st.session_state.parties[party_id]
        
        party_loans = [l for l in st.session_state.loans.values() if l['party_id'] == party_id]
        party_trans = [t for t in st.session_state.transactions.values() if t['party_id'] == party_id]
        
        if party_loans or party_trans:
            col1, col2, col3 = st.columns(3)
            with col1:
                total_loan = sum([l.get('net_disbursement', 0) for l in party_loans])
                st.metric("💰 Total Loans", f"₹{total_loan:,.2f}")
            with col2:
                total_paid = sum([l.get('paid_amount', 0) for l in party_loans])
                st.metric("💳 Total Paid", f"₹{total_paid:,.2f}")
            with col3:
                total_balance = sum([l.get('outstanding_balance', 0) for l in party_loans])
                st.metric("📊 Outstanding", f"₹{total_balance:,.2f}")
            
            if party_loans:
                st.markdown("#### Active Loans")
                df = pd.DataFrame(party_loans)
                st.dataframe(df[['loan_id', 'principal', 'emi', 'duration_months', 'outstanding_balance', 'status']], 
                            use_container_width=True,
                            column_config={
                                'loan_id': 'Loan ID',
                                'principal': st.column_config.NumberColumn('Principal', format='₹%.2f'),
                                'emi': st.column_config.NumberColumn('EMI', format='₹%.2f'),
                                'duration_months': 'Months',
                                'outstanding_balance': st.column_config.NumberColumn('Outstanding', format='₹%.2f'),
                                'status': 'Status'
                            })
                
                st.markdown("#### Make a Repayment")
                active_loans = [l for l in party_loans if l['status'] == 'Active']
                if active_loans:
                    loan_options = {f"{l['loan_id']} - Outstanding: ₹{l['outstanding_balance']:,.2f}": l['loan_id'] for l in active_loans}
                    sel_loan = st.selectbox("Select Loan", list(loan_options.keys()))
                    loan_id = loan_options[sel_loan]
                    loan = st.session_state.loans[loan_id]
                    
                    amount = st.number_input("Repayment Amount (₹)", min_value=0.0, max_value=float(loan['outstanding_balance']), step=100.0, format="%.2f")
                    if st.button("💳 Make Payment", use_container_width=True):
                        if amount > 0:
                            loan['outstanding_balance'] -= amount
                            loan['paid_amount'] += amount
                            if loan['outstanding_balance'] <= 0:
                                loan['status'] = 'Closed'
                                loan['outstanding_balance'] = 0
                                st.success("✅ Loan fully repaid and closed!")
                            else:
                                st.success(f"✅ ₹{amount:,.2f} payment recorded successfully!")
                            trans_id = generate_trans_id()
                            st.session_state.transactions[trans_id] = {
                                'trans_id': trans_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'party_id': party_id, 'party_name': party['party_name'],
                                'transaction_type': 'Loan Repayment', 'amount': amount,
                                'details': f'Loan: {loan_id}'
                            }
                            auto_save()
                            st.rerun()
                        else:
                            st.warning("⚠️ Please enter a valid amount.")
                else:
                    st.info("✅ No active loans for this party.")
            
            if party_trans:
                st.markdown("#### Transaction History")
                df = pd.DataFrame(party_trans)
                st.dataframe(df[['date', 'transaction_type', 'amount', 'details']], 
                            use_container_width=True,
                            column_config={
                                'date': 'Date',
                                'transaction_type': 'Type',
                                'amount': st.column_config.NumberColumn('Amount', format='₹%.2f'),
                                'details': 'Details'
                            })
        else:
            st.info("📭 No loans or transactions for this party.")

# ============ MODULE: GOLD PLEDGE ============
elif menu == "💍 Gold Pledge Management":
    st.markdown('<div class="section-header">💍 Gold Pledge Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Gold Pledge", "📋 View All Pledges"])
    
    with tab1:
        if not st.session_state.parties:
            st.info("📭 Please add a party first.")
        else:
            with st.form("pledge_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    party_options = {f"{p['party_id']} - {p['party_name']}": pid for pid, p in st.session_state.parties.items()}
                    selected = st.selectbox("Select Party *", list(party_options.keys()))
                    party_id = party_options[selected]
                    
                    st.markdown("#### Gold Details")
                    desc = st.text_area("Item Description *", placeholder="e.g., Gold chain, Bangles, Rings")
                    count = st.number_input("Number of Items", min_value=1, value=1, step=1)
                
                with col2:
                    gross_w = st.number_input("Gross Weight (grams) *", min_value=0.1, value=10.0, step=0.1, format="%.2f")
                    net_w = st.number_input("Net Weight (grams) *", min_value=0.1, value=9.5, step=0.1, format="%.2f")
                    purity = st.selectbox("Purity", ["24K", "22K", "18K", "14K"])
                    rate = st.number_input("Current Gold Rate (per gram)", min_value=0.0, value=5000.0, step=50.0, format="%.2f")
                    value = net_w * rate if net_w > 0 and rate > 0 else 0
                    
                    st.markdown(f"""
                    <div class="info-box-gold">
                        <strong>Appraised Value: ₹{value:,.2f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    locker = st.text_input("Locker/Vault ID", placeholder="Enter locker number")
                
                if st.form_submit_button("💍 Register Pledge"):
                    if desc and net_w > 0 and rate > 0:
                        pledge_id = f"G{datetime.now().strftime('%Y%m%d')}{str(len(st.session_state.gold_items)+1).zfill(3)}"
                        st.session_state.gold_items[pledge_id] = {
                            'pledge_id': pledge_id, 'party_id': party_id,
                            'party_name': st.session_state.parties[party_id]['party_name'],
                            'item_description': desc, 'item_count': count,
                            'gross_weight': gross_w, 'net_weight': net_w,
                            'purity': purity, 'current_gold_rate': rate,
                            'appraised_value': value, 'locker_id': locker,
                            'pledge_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'status': 'Active'
                        }
                        trans_id = generate_trans_id()
                        st.session_state.transactions[trans_id] = {
                            'trans_id': trans_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'party_id': party_id, 'party_name': st.session_state.parties[party_id]['party_name'],
                            'transaction_type': 'Gold Pledge', 'amount': value,
                            'details': f'Pledge: {pledge_id}'
                        }
                        auto_save()
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ Gold pledge <strong>{pledge_id}</strong> registered successfully!<br>
                            <small>Appraised Value: ₹{value:,.2f}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.error("⚠️ Please fill in all required fields.")
    
    with tab2:
        if st.session_state.gold_items:
            df = pd.DataFrame(st.session_state.gold_items.values())
            st.dataframe(df[['pledge_id', 'party_name', 'item_description', 'net_weight', 'purity', 'appraised_value', 'status']], 
                        use_container_width=True,
                        column_config={
                            'pledge_id': 'Pledge ID',
                            'party_name': 'Customer',
                            'item_description': 'Description',
                            'net_weight': 'Weight (g)',
                            'purity': 'Purity',
                            'appraised_value': st.column_config.NumberColumn('Value', format='₹%.2f'),
                            'status': 'Status'
                        })
        else:
            st.info("📭 No gold pledges registered yet.")

# ============ MODULE: LOAN AGREEMENT ============
elif menu == "📄 Loan Agreement":
    st.markdown('<div class="section-header">📄 Loan Agreement (Malayalam)</div>', unsafe_allow_html=True)
    
    if not st.session_state.parties or not st.session_state.loans:
        st.info("📭 Please add a party and disburse a loan first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            party_options = {f"{p['party_id']} - {p['party_name']}": pid for pid, p in st.session_state.parties.items()}
            selected_party = st.selectbox("Select Party", list(party_options.keys()))
            party_id = party_options[selected_party]
            party = st.session_state.parties[party_id]
        
        with col2:
            party_loans = {l['loan_id']: l for l in st.session_state.loans.values() if l['party_id'] == party_id}
            if party_loans:
                loan_options = {f"{lid} - ₹{l['principal']:,.2f}": lid for lid, l in party_loans.items()}
                selected_loan = st.selectbox("Select Loan", list(loan_options.keys()))
                loan_id = loan_options[selected_loan]
                loan = st.session_state.loans[loan_id]
                golds = [g for g in st.session_state.gold_items.values() if g['party_id'] == party_id]
                
                st.markdown("---")
                
                if st.button("📄 View Agreement", use_container_width=True):
                    st.session_state.show_agreement = True
                    st.session_state.agreement_data = {
                        'party': party, 'loan': loan, 'golds': golds
                    }
                    st.rerun()
            else:
                st.warning("No loans found for this party.")
        
        # Show Agreement
        if st.session_state.show_agreement and st.session_state.agreement_data:
            data = st.session_state.agreement_data
            party = data['party']
            loan = data['loan']
            golds = data['golds']
            
            emi_start = datetime.strptime(loan['emi_start_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
            emi_end = datetime.strptime(loan['emi_end_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
            
            st.markdown("---")
            st.markdown('<div class="agreement-container">', unsafe_allow_html=True)
            
            # Agreement Content
            agreement_html = f"""
            <div style="font-family: 'Noto Sans Malayalam', 'Malayalam', 'Arial Unicode MS', sans-serif;">
                <h1 style="text-align:center;color:#FFD700;font-size:2.5rem;">സ്വർണ്ണപ്പണയ ഉടമ്പടി</h1>
                <p style="text-align:center;font-size:1.2rem;color:#666;margin-bottom:2rem;">(Gold Loan Agreement)</p>
                <hr style="border:2px solid #FFD700;margin-bottom:2rem;">
                
                <h3 style="color:#2c3e50;">1. പാർട്ടി വിവരങ്ങൾ</h3>
                <table style="width:100%;border-collapse:collapse;margin:1rem 0;">
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">പേര് (Name):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{party['party_name']}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">വിലാസം (Address):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{party['address']}, {party['city']}, {party['pincode']}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">മൊബൈൽ (Mobile):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{party['mobile']}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">തൊഴിൽ (Occupation):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{party['occupation']}</td></tr>
                </table>
                
                <h3 style="color:#2c3e50;">2. വായ്പ വിവരങ്ങൾ</h3>
                <table style="width:100%;border-collapse:collapse;margin:1rem 0;">
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">മൊത്തം തുക (Gross Amount):</td>
                        <td style="padding:10px;border:1px solid #ddd;">₹{loan['gross_amount']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">പലിശ നിരക്ക് (Interest Rate):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{loan['interest_rate']}% പ്രതിവർഷം</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">കാലാവധി (Tenure):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{loan['duration_months']} മാസം</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">മൊത്തം പലിശ (Total Interest):</td>
                        <td style="padding:10px;border:1px solid #ddd;">₹{loan['total_interest']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">മൊത്തം തുക (Total Amount Due):</td>
                        <td style="padding:10px;border:1px solid #ddd;background:#fff8e1;font-weight:bold;">₹{loan['total_amount']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">പ്രതിമാസ തവണ (EMI):</td>
                        <td style="padding:10px;border:1px solid #ddd;background:#FFD700;font-weight:bold;">₹{loan['emi']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">EMI ആരംഭം (Start Date):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{emi_start}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">EMI അവസാനം (End Date):</td>
                        <td style="padding:10px;border:1px solid #ddd;">{emi_end}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee):</td>
                        <td style="padding:10px;border:1px solid #ddd;">₹{loan['processing_fee']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">അഡ്മിൻ ഫീസ് (Admin Fee):</td>
                        <td style="padding:10px;border:1px solid #ddd;">₹{loan['admin_fee']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;font-weight:bold;">ഡോക്യുമെന്റേഷൻ ഫീസ് (Doc Fee):</td>
                        <td style="padding:10px;border:1px solid #ddd;">₹{loan['documentation_fee']:,.2f}</td></tr>
                    <tr><td style="padding:10px;border:1px solid #ddd;background:#FFD700;font-weight:bold;font-size:1.1rem;">നൽകിയ തുക (Net Disbursed):</td>
                        <td style="padding:10px;border:1px solid #ddd;background:#FFD700;font-weight:bold;font-size:1.1rem;">₹{loan['net_disbursement']:,.2f}</td></tr>
                </table>
            """
            
            if golds:
                agreement_html += """
                <h3 style="color:#2c3e50;">3. സ്വർണ്ണ വിവരങ്ങൾ</h3>
                <table style="width:100%;border-collapse:collapse;margin:1rem 0;">
                    <tr style="background:#FFD700;">
                        <th style="padding:10px;border:1px solid #ddd;">വിവരണം</th>
                        <th style="padding:10px;border:1px solid #ddd;">എണ്ണം</th>
                        <th style="padding:10px;border:1px solid #ddd;">ഭാരം (g)</th>
                        <th style="padding:10px;border:1px solid #ddd;">പ്യൂരിറ്റി</th>
                        <th style="padding:10px;border:1px solid #ddd;">മൂല്യം</th>
                    </tr>
                """
                for g in golds:
                    agreement_html += f"""
                    <tr>
                        <td style="padding:10px;border:1px solid #ddd;">{g['item_description']}</td>
                        <td style="padding:10px;border:1px solid #ddd;text-align:center;">{g['item_count']}</td>
                        <td style="padding:10px;border:1px solid #ddd;text-align:center;">{g['net_weight']:.2f}</td>
                        <td style="padding:10px;border:1px solid #ddd;text-align:center;">{g['purity']}</td>
                        <td style="padding:10px;border:1px solid #ddd;text-align:right;">₹{g['appraised_value']:,.2f}</td>
                    </tr>
                    """
                agreement_html += "</table>"
            
            agreement_html += """
                <h3 style="color:#2c3e50;">4. നിബന്ധനകളും വ്യവസ്ഥകളും</h3>
                <ol style="line-height:2;">
                    <li>മുകളിൽ പറഞ്ഞ സ്വർണ്ണാഭരണങ്ങൾ എന്റെ സ്വന്തമാണെന്നും, അതിൽ മറ്റാർക്കും അവകാശമില്ലെന്നും ഞാൻ സാക്ഷ്യപ്പെടുത്തുന്നു.</li>
                    <li>വായ്പ തുകയും പലിശയും നിശ്ചയിച്ച കാലാവധിക്കുള്ളിൽ അടച്ചുതീർക്കുന്നതിന് ഞാൻ ബാദ്ധ്യസ്ഥനാണ്.</li>
                    <li>വായ്പ തിരിച്ചടയ്ക്കുന്നതിൽ വീഴ്ച വരുത്തിയാൽ, സ്ഥാപനത്തിന് പണയം വെച്ച സ്വർണ്ണം ലേലം ചെയ്യാനുള്ള അവകാശമുണ്ടായിരിക്കും.</li>
                    <li>പലിശ നിരക്കിലും മറ്റ് നിബന്ധനകളിലും മാറ്റം വരുത്താൻ സ്ഥാപനത്തിന് അധികാരമുണ്ട്.</li>
                    <li>വായ്പയുടെ ബാക്കി തുകയും പലിശയും പൂർണ്ണമായി അടച്ചതിന് ശേഷം മാത്രമേ സ്വർണ്ണം തിരികെ നൽകുകയുള്ളൂ.</li>
                </ol>
                <hr style="border:1px solid #ddd;margin:2rem 0;">
                
                <table style="width:100%;margin:2rem 0;">
                    <tr>
                        <td style="padding:20px;width:50%;">
                            <strong>ഒപ്പ് (Signature):</strong> __________________<br>
                            <span style="font-size:0.9rem;color:#666;">(വായ്പക്കാരൻ / Borrower)</span>
                        </td>
                        <td style="padding:20px;width:50%;">
                            <strong>തീയതി (Date):</strong> """ + datetime.now().strftime('%d-%m-%Y') + """
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:20px;">
                            <strong>സ്ഥലം (Place):</strong> __________________
                        </td>
                        <td style="padding:20px;">
                            <strong>സാക്ഷി (Witness):</strong> __________________
                        </td>
                    </tr>
                </table>
                
                <div style="background:#f0f2f6;padding:1rem;border-radius:8px;text-align:center;margin-top:2rem;">
                    <p style="color:#666;font-size:0.9rem;">
                        ⚠️ ഈ ഉടമ്പടി സിസ്റ്റം ജനറേറ്റ് ചെയ്തതാണ്. ഒപ്പ് വയ്ക്കുന്നതിന് മുമ്പ് എല്ലാ വിശദാംശങ്ങളും പരിശോധിക്കുക.
                    </p>
                </div>
            </div>
            """
            
            st.markdown(agreement_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.download_button(
                    label="📥 Download as HTML",
                    data=agreement_html,
                    file_name=f"Agreement_{party['party_name']}_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
            with col2:
                st.markdown("""
                <button onclick="window.print()" style="width:100%;padding:0.75rem;background:#FFD700;color:#1a1a2e;border:none;border-radius:8px;font-weight:bold;font-size:1rem;cursor:pointer;">
                    🖨️ Print Agreement
                </button>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("❌ Close Agreement"):
                    st.session_state.show_agreement = False
                    st.session_state.agreement_data = None
                    st.rerun()

# ============ MODULE: EMI SCHEDULE ============
elif menu == "📅 EMI Schedule":
    st.markdown('<div class="section-header">📅 EMI Schedule</div>', unsafe_allow_html=True)
    
    if not st.session_state.loans:
        st.info("📭 No loans available.")
    else:
        loan_options = {f"{l['loan_id']} - {l['party_name']}": lid for lid, l in st.session_state.loans.items()}
        selected = st.selectbox("Select Loan", list(loan_options.keys()))
        loan_id = loan_options[selected]
        loan = st.session_state.loans[loan_id]
        
        st.markdown(f"""
        <div class="info-box-gold">
            <strong>📊 Loan Summary</strong><br>
            Loan ID: {loan['loan_id']}<br>
            Party: {loan['party_name']}<br>
            Principal: ₹{loan['principal']:,.2f}<br>
            EMI: ₹{loan['emi']:,.2f}<br>
            Total Amount Due: ₹{loan['total_amount']:,.2f}<br>
            Outstanding: ₹{loan['outstanding_balance']:,.2f}
        </div>
        """, unsafe_allow_html=True)
        
        if 'emi_schedule' in loan and loan['emi_schedule']:
            df = pd.DataFrame(loan['emi_schedule'])
            
            st.markdown("#### Complete EMI Schedule")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Schedule as CSV", csv, f"EMI_{loan['loan_id']}.csv", "text/csv")
        else:
            st.info("📭 No EMI schedule available for this loan.")

# ============ MODULE: BACKUP ============
elif menu == "💾 Backup & Restore":
    st.markdown('<div class="section-header">💾 Backup & Restore</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Export Data")
        if st.button("📥 Download Backup", use_container_width=True):
            backup = {
                'parties': st.session_state.parties,
                'loans': st.session_state.loans,
                'gold_items': st.session_state.gold_items,
                'transactions': st.session_state.transactions,
                'party_counter': st.session_state.party_counter,
                'backup_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            json_data = json.dumps(backup, indent=2, default=str)
            b64 = base64.b64encode(json_data.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="gold_loan_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" style="background:#FFD700;color:#1a1a2e;padding:0.75rem;border-radius:8px;text-decoration:none;display:block;text-align:center;font-weight:bold;">📥 Click to Download</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ Backup file created successfully!")
    
    with col2:
        st.markdown("#### 📥 Import Data")
        uploaded = st.file_uploader("Upload Backup JSON File", type=['json'])
        if uploaded:
            if st.button("🔄 Restore from Backup", use_container_width=True):
                try:
                    data = json.load(uploaded)
                    st.session_state.parties = data.get('parties', {})
                    st.session_state.loans = data.get('loans', {})
                    st.session_state.gold_items = data.get('gold_items', {})
                    st.session_state.transactions = data.get('transactions', {})
                    st.session_state.party_counter = data.get('party_counter', 1)
                    auto_save()
                    st.markdown("""
                    <div class="success-message">
                        ✅ Data restored successfully from backup!
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    st.info("🔄 Refreshing page to show updated data...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error restoring backup: {str(e)}")
    
    st.markdown("---")
    st.markdown("#### 📊 Current Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Parties", len(st.session_state.parties))
    with col2:
        st.metric("💰 Loans", len(st.session_state.loans))
    with col3:
        st.metric("💍 Gold Pledges", len(st.session_state.gold_items))
    with col4:
        st.metric("📝 Transactions", len(st.session_state.transactions))
    
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

auto_save()






