
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# ==========================================
# 1. DATABASE INITIALIZATION & MIGRATION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect('gold_loan_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Party Master Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            guardian_name TEXT,
            dob TEXT,
            mobile TEXT,
            whatsapp TEXT,
            address TEXT,
            pincode TEXT,
            pan_masked TEXT,
            occupation TEXT,
            qualification TEXT,
            kyc_status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    ''')
    
    # 2. Loans & Asset Details Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER,
            principal REAL,
            interest_rate REAL,
            duration_months INTEGER,
            emi REAL,
            processing_fee REAL,
            admin_fee REAL,
            documentation_fee REAL,
            net_disbursed REAL,
            gold_description TEXT,
            items_count INTEGER,
            gross_weight REAL,
            net_weight REAL,
            purity_karat INTEGER,
            appraised_value REAL,
            vault_id TEXT,
            status TEXT DEFAULT 'Active',
            disbursed_date TEXT,
            FOREIGN KEY (party_id) REFERENCES parties (id)
        )
    ''')
    
    # 3. Transaction Ledger Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            transaction_type TEXT,
            amount REAL,
            transaction_date TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans (id)
        )
    ''')
    
    # Schema Migration Check: Add missing columns if upgrading from old DB version
    try:
        cursor.execute("SELECT guardian_name FROM parties LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE parties ADD COLUMN guardian_name TEXT")
        cursor.execute("ALTER TABLE parties ADD COLUMN occupation TEXT")
        cursor.execute("ALTER TABLE parties ADD COLUMN qualification TEXT")
        
    try:
        cursor.execute("SELECT emi FROM loans LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE loans ADD COLUMN emi REAL")
        cursor.execute("ALTER TABLE loans ADD COLUMN processing_fee REAL")
        cursor.execute("ALTER TABLE loans ADD COLUMN admin_fee REAL")
        cursor.execute("ALTER TABLE loans ADD COLUMN documentation_fee REAL")
        cursor.execute("ALTER TABLE loans ADD COLUMN net_disbursed REAL")
        cursor.execute("ALTER TABLE loans ADD COLUMN gold_description TEXT")
        cursor.execute("ALTER TABLE loans ADD COLUMN items_count INTEGER")
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="AuraLoan | Gold Loan Management", layout="wide", page_icon="💎")

# Custom Gold-Themed Styling for Agreement
st.markdown("""
    <style>
    .gold-header { color: #b8860b; font-weight: bold; text-align: center; }
    .agreement-box { border: 2px solid #b8860b; padding: 25px; background-color: #fcfcf4; border-radius: 10px; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("💎 AuraLoan - Gold Loan Management System")
st.markdown("---")

menu = [
    "Dashboard & Analytics", 
    "Party Master (KYC)", 
    "Originate Loan & Pledge", 
    "Servicing & Ledger", 
    "Data Maintenance (Backup/Export)"
]
choice = st.sidebar.selectbox("Navigate System Modules", menu)

# ==========================================
# MODULE 5: REPORTING & ANALYTICS
# ==========================================
if choice == "Dashboard & Analytics":
    st.header("📊 Executive Portfolio Dashboard")
    conn = get_db_connection()
    
    total_active_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
    total_disbursed = conn.execute("SELECT SUM(principal) FROM loans").fetchone()[0] or 0.0
    total_gold = conn.execute("SELECT SUM(net_weight) FROM loans WHERE status='Active'").fetchone()[0] or 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Loan Accounts", total_active_loans)
    col2.metric("Total Portfolio Disbursed", f"₹{total_disbursed:,.2f}")
    col3.metric("Total Gold Vaulted (Net)", f"{total_gold:.2f} g")
    
    st.subheader("📈 Recent Loan Allocations")
    df_loans = pd.read_sql_query("""
        SELECT l.id as Loan_ID, p.name as Customer, l.principal as Principal, 
               l.interest_rate as Rate_Pct, l.net_weight as Net_Weight_g, l.status as Status 
        FROM loans l JOIN parties p ON l.party_id = p.id
    """, conn)
    st.dataframe(df_loans, use_container_width=True)
    conn.close()

# ==========================================
# MODULE 1: PARTY MASTER (CRUD)
# ==========================================
elif choice == "Party Master (KYC)":
    st.header("👤 Customer Information Management (Party Master)")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Party", "📋 View & Edit Parties", "❌ Remove Record"])
    
    with tab1:
        with st.form("add_party_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("പേര് (Name) *")
                guardian_name = st.text_input("പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name)")
                dob = st.date_input("Date of Birth")
                mobile = st.text_input("മൊബൈൽ നമ്പർ (Mobile) *")
                whatsapp = st.text_input("WhatsApp Number")
            with col2:
                occupation = st.text_input("തൊഴിൽ (Occupation)")
                qualification = st.text_input("യോഗ്യത (Qualification)")
                address = st.text_area("വിലാസം (Address)")
                pincode = st.text_input("Pincode")
                pan = st.text_input("PAN Card Number")
                kyc_status = st.selectbox("KYC Status Verification", ["Pending", "Verified", "Suspended"])
            
            submitted = st.form_submit_button("Save Customer Profile")
            if submitted:
                if name and mobile:
                    conn = get_db_connection()
                    conn.execute("""
                        INSERT INTO parties (name, guardian_name, dob, mobile, whatsapp, address, pincode, pan_masked, occupation, qualification, kyc_status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, guardian_name, str(dob), mobile, whatsapp, address, pincode, pan, occupation, qualification, kyc_status, str(datetime.now().date())))
                    conn.commit()
                    conn.close()
                    st.success(f"Successfully registered: {name}")
                else:
                    st.error("Name and Mobile fields are mandatory.")

    with tab2:
        conn = get_db_connection()
        parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
        st.dataframe(parties_df, use_container_width=True)
        
        st.markdown("### ✏️ Quick Inline Update")
        if not parties_df.empty:
            party_to_edit = st.selectbox("Select Party to Update Profile", parties_df['id'].tolist(), format_func=lambda x: parties_df[parties_df['id']==x]['name'].values[0])
            selected_row = parties_df[parties_df['id'] == party_to_edit].iloc[0]
            
            with st.form("edit_party_form"):
                new_mobile = st.text_input("Update Mobile", value=selected_row['mobile'])
                new_kyc = st.selectbox("Update KYC Status", ["Pending", "Verified", "Suspended"], index=["Pending", "Verified", "Suspended"].index(selected_row['kyc_status']))
                
                if st.form_submit_button("Apply Updates"):
                    conn.execute("UPDATE parties SET mobile=?, kyc_status=? WHERE id=?", (new_mobile, new_kyc, party_to_edit))
                    conn.commit()
                    st.success("Customer profile updated successfully.")
                    st.rerun()
        conn.close()

    with tab3:
        st.markdown("### ⚠️ Delete Customer Account Record")
        conn = get_db_connection()
        parties_df = pd.read_sql_query("SELECT * FROM parties", conn)
        if not parties_df.empty:
            delete_id = st.selectbox("Select Party Profile for Deletion", parties_df['id'].tolist(), format_func=lambda x: parties_df[parties_df['id']==x]['name'].values[0])
            if st.button("Confirm Permanently Delete Profile", type="primary"):
                conn.execute("DELETE FROM parties WHERE id=?", (delete_id,))
                conn.commit()
                st.warning("Profile dropped from tracking registers.")
                st.rerun()
        conn.close()

# ==========================================
# MODULE 2, 3 & 6: ORIGINATION, PLEDGE & AGREEMENT
# ==========================================
elif choice == "Originate Loan & Pledge":
    st.header("⚖️ Gold Loan Origination & Asset Valuation")
    
    conn = get_db_connection()
    parties = conn.execute("SELECT id, name FROM parties WHERE kyc_status='Verified'").fetchall()
    
    if not parties:
        st.warning("⚠️ No KYC Verified parties available. Please register and verify a party inside the 'Party Master' module first.")
    else:
        party_options = {p['id']: p['name'] for p in parties}
        
        with st.form("origination_form"):
            selected_party = st.selectbox("Select Verified Borrower", list(party_options.keys()), format_func=lambda x: party_options[x])
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 💎 സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)")
                gold_description = st.text_input("വിവരണം (Description)", placeholder="e.g., മാല, വളകൾ")
                items_count = st.number_input("എണ്ണം (Count)", min_value=1, step=1, value=1)
                gross_wt = st.number_input("Gross Weight (grams)", min_value=0.0, step=0.1)
                net_wt = st.number_input("Weight / Net Weight (grams)", min_value=0.0, step=0.1)
                purity = st.selectbox("പ്യൂരിറ്റി (Purity Karat)", [24, 22, 20, 18], index=1)
                appraised_val = st.number_input("മൂല്യം (Value - ₹)", min_value=0.0)
                vault_id = st.text_input("Secure Vault Envelope ID")
            
            with col2:
                st.markdown("#### 💰 വായ്പയുടെ വിവരങ്ങൾ (Loan Details)")
                max_eligible = appraised_val * 0.75
                st.info(f"Max Eligible (75% LTV Limit): ₹{max_eligible:,.2f}")
                
                principal = st.number_input("തുക (Principal - ₹)", min_value=0.0)
                interest_rate = st.number_input("പലിശ നിരക്ക് (Interest Rate %)", min_value=0.0, value=12.0)
                duration = st.number_input("കാലാവധി (Tenure Months)", min_value=1, max_value=36, value=12)
                
                # Fees Inputs
                processing_fee = st.number_input("പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee - ₹)", min_value=0.0, value=100.0)
                admin_fee = st.number_input("അഡ്മിൻ ഫീസ് (Admin Fee - ₹)", min_value=0.0, value=50.0)
                doc_fee = st.number_input("ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee - ₹)", min_value=0.0, value=50.0)
                
                # Auto-calculations for Display
                total_fees = processing_fee + admin_fee + doc_fee
                calculated_net_disbursed = max(0.0, principal - total_fees)
                
                # Simple EMI Calculator Formula: [P x R x (1+R)^N]/[(1+R)^N-1]
                r_monthly = (interest_rate / 12) / 100
                if r_monthly > 0:
                    calculated_emi = (principal * r_monthly * ((1 + r_monthly) ** duration)) / (((1 + r_monthly) ** duration) - 1)
                else:
                    calculated_emi = principal / duration
                    
                st.write(f"**പ്രതിമാസ തവണ (EMI):** ₹{calculated_emi:,.2f}")
                st.write(f"**നൽകുന്ന അറ്റതുക (Net Disbursed Amount):** ₹{calculated_net_disbursed:,.2f}")

            submitted_loan = st.form_submit_button("Approve & Disburse Asset-Backed Loan")
            
            if submitted_loan:
                if principal > max_eligible:
                    st.error("Requested funding exceeds regulatory maximum Loan-to-Value (75%) limit.")
                elif principal <= 0 or net_wt <= 0:
                    st.error("Please input valid metrics for Principal and Net Weight.")
                else:
                    today_str = str(datetime.now().date())
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO loans (
                            party_id, principal, interest_rate, duration_months, emi, 
                            processing_fee, admin_fee, documentation_fee, net_disbursed,
                            gold_description, items_count, gross_weight, net_weight, 
                            purity_karat, appraised_value, vault_id, status, disbursed_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
                    """, (selected_party, principal, interest_rate, duration, calculated_emi, 
                          processing_fee, admin_fee, doc_fee, calculated_net_disbursed,
                          gold_description, items_count, gross_wt, net_wt, purity, appraised_val, vault_id, today_str))
                    
                    loan_id = cursor.lastrowid
                    
                    cursor.execute("""
                        INSERT INTO ledger (loan_id, transaction_type, amount, transaction_date)
                        VALUES (?, 'Disbursement', ?, ?)
                    """, (loan_id, calculated_net_disbursed, today_str))
                    
                    conn.commit()
                    st.success(f"Loan Record #{loan_id} successfully finalized.")
                    st.session_state['last_loan_id'] = loan_id

        # Agreement Section Displays right below after successful creation
        if 'last_loan_id' in st.session_state:
            l_id = st.session_state['last_loan_id']
            loan_row = conn.execute(f"SELECT * FROM loans WHERE id={l_id}").fetchone()
            party_row = conn.execute(f"SELECT * FROM parties WHERE id={loan_row['party_id']}").fetchone()
            
            st.markdown("---")
            st.subheader("📄 ജനറേറ്റ് ചെയ്ത മലയാളം വായ്പാ കരാർ (Generated Malayalam Agreement)")
            
            agreement_html = f"""
            <div class="agreement-box">
                <h2 class="gold-header">സ്വർണ്ണപ്പണയ വായ്പാ കരാർ (Gold Loan Agreement)</h2>
                <p><b>കരാർ നമ്പർ (Agreement No):</b> #{loan_row['id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>തീയതി (Date):</b> {loan_row['disbursed_date']}</p>
                <hr style="border-top: 1px solid #b8860b;">
                
                <h3>👤 1. പാർട്ടി വിവരങ്ങൾ (Party Details)</h3>
                <ul>
                    <li><b>വായ്പക്കാരന്റെ പേര് (Name):</b> {party_row['name']}</li>
                    <li><b>പിതാവ്/ഭർത്താവിന്റെ പേര് (Father/Husband Name):</b> {party_row['guardian_name'] or 'N/A'}</li>
                    <li><b>വിലാസം (Address):</b> {party_row['address'] or 'N/A'}, {party_row['pincode'] or ''}</li>
                    <li><b>മൊബൈൽ നമ്പർ (Mobile):</b> {party_row['mobile']}</li>
                    <li><b>തൊഴിൽ (Occupation):</b> {party_row['occupation'] or 'N/A'}</li>
                    <li><b>യോഗ്യത (Qualification):</b> {party_row['qualification'] or 'N/A'}</li>
                </ul>

                <h3>💰 2. വായ്പയുടെ വിവരങ്ങൾ (Loan Details)</h3>
                <table style="width:100%; border-collapse: collapse; border: 1px solid #ccc;">
                    <tr style="background-color: #f2f2f2;"><th style="padding:8px; text-align:left;">വിവരണം (Description)</th><th style="padding:8px; text-align:left;">തുക / നിരക്ക് (Amount / Rate)</th></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">അനുവദിച്ച വായ്പ തുക (Principal)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['principal']:,.2f}</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">പ്രതിവർഷ പലിശ നിരക്ക് (Interest Rate)</td><td style="padding:8px; border: 1px solid #ccc;">{loan_row['interest_rate']}%</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">വായ്പ കാലാവധി (Tenure)</td><td style="padding:8px; border: 1px solid #ccc;">{loan_row['duration_months']} മാസങ്ങൾ</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">പ്രതിമാസ തവണ (EMI)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['emi']:,.2f}</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">പ്രോസസ്സിംഗ് ഫീസ് (Processing Fee)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['processing_fee']:,.2f}</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">അഡ്മിൻ ഫീസ് (Admin Fee)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['admin_fee']:,.2f}</td></tr>
                    <tr><td style="padding:8px; border: 1px solid #ccc;">ഡോക്യുമെന്റേഷൻ ഫീസ് (Documentation Fee)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['documentation_fee']:,.2f}</td></tr>
                    <tr style="font-weight:bold; background-color: #e6f7ff;"><td style="padding:8px; border: 1px solid #ccc;">നൽകിയ അറ്റതുക (Net Disbursed Amount)</td><td style="padding:8px; border: 1px solid #ccc;">₹{loan_row['net_disbursed']:,.2f}</td></tr>
                </table>

                <h3>💎 3. സ്വർണ്ണത്തിന്റെ വിവരങ്ങൾ (Gold Details)</h3>
                <ul>
                    <li><b>ആഭരണങ്ങളുടെ വിവരണം (Description):</b> {loan_row['gold_description'] or 'N/A'}</li>
                    <li><b>ആകെ എണ്ണം (Count):</b> {loan_row['items_count']} Nos</li>
                    <li><b>ആകെ ഭാരം (Gross Weight):</b> {loan_row['gross_weight']} ഗ്രാം</li>
                    <li><b>ശുദ്ധമായ ഭാരം (Net Weight):</b> {loan_row['net_weight']} ഗ്രാം</li>
                    <li><b>പ്യൂരിറ്റി (Purity):</b> {loan_row['purity_karat']} Karat</li>
                    <li><b>നിശ്ചയിച്ച വിപണി മൂല്യം (Value):</b> ₹{loan_row['appraised_value']:,.2f}</li>
                </ul>

                <h3>📝 4. നിബന്ധനകളും വ്യവസ്ഥകളും (Terms and Conditions)</h3>
                <p><b>1. സ്വർണ്ണ ഉടമസ്ഥാവകാശ പ്രഖ്യാപനം (Gold Ownership Declaration):</b> പണയപ്പെടുത്തുന്നതിനായി ഇവിടെ ഹാജരാക്കിയിട്ടുള്ള സ്വർണ്ണാഭരണങ്ങൾ പൂർണ്ണമായും വായ്പക്കാരന്റെ സ്വന്തം ഉടമസ്ഥതയിലുള്ളതും നിയമാനുസൃതമായി സമ്പാദിച്ചതുമാണെന്ന് ഇതിനാൽ സാക്ഷ്യപ്പെടുത്തുന്നു.</p>
                <p><b>2. തിരിച്ചടവ് ബാധ്യതകൾ (Repayment Obligations):</b> വായ്പക്കാരൻ മുകളിൽ ഒപ്പിട്ടിട്ടുള്ള നിബന്ധനകൾ പ്രകാരം എല്ലാ മാസവും കൃത്യസമയത്ത് പ്രതിമാസ തവണകളോ (EMI) അല്ലെങ്കിൽ പലിശയോ അടച്ചുതീർക്കാൻ ബാധ്യസ്ഥനാണ്.</p>
                <p><b>3. വീഴ്ചയും ലേലം ചെയ്യാനുള്ള അവകാശവും (Default and Auction Rights):</b> വായ്പക്കാരൻ തുടർച്ചയായി തിരിച്ചടവിൽ വീഴ്ച വരുത്തുകയോ, വായ്പ കാലാവധി കഴിഞ്ഞിട്ടും തുക അടയ്ക്കാതിരിക്കുകയോ ചെയ്താൽ, പണയം വെച്ചിരിക്കുന്ന സ്വർണ്ണം നിയമാനുസൃതമായി പരസ്യ ലേലത്തിൽ (Public Auction) വിൽക്കാനുള്ള പൂർണ്ണ അധികാരം സ്ഥാപനത്തിനുണ്ടായിരിക്കും.</p>
                <p><b>4. പലിശ നിരക്കിലെ മാറ്റങ്ങൾ (Interest Rate Changes):</b> റിസർവ് ബാങ്ക് (RBI) നിർദ്ദേശങ്ങൾക്കോ വിപണിയിലെ മാറ്റങ്ങൾക്കോ വിധേയമായി വായ്പയുടെ പലിശ നിരക്കുകളിൽ മാറ്റം വരുത്താൻ സ്ഥാപനത്തിന് അവകാശമുണ്ട്.</p>
                <p><b>5. പൂർണ്ണമായ സെറ്റിൽമെന്റ് വ്യവസ്ഥകൾ (Full Settlement Terms):</b> വായ്പ തുകയും പലിശയും മറ്റ് ചാർജ്ജുകളും പൂർണ്ണമായി അടച്ചുതീർത്താൽ മാത്രമേ പണയം വെച്ചിട്ടുള്ള സ്വർണ്ണാഭരണങ്ങൾ വായ്പക്കാരന് തിരികെ നൽകുകയുള്ളൂ.</p>
                
                <br><br>
                <table style="width:100%; margin-top:20px;">
                    <tr>
                        <td>___________________________<br><b>വായ്പക്കാരന്റെ ഒപ്പ് / വിരലടയാളം</b></td>
                        <td style="text-align:right;">___________________________<br><b>സ്ഥാപന അധികാരിയുടെ ഒപ്പ്</b></td>
                    </tr>
                </table>
            </div>
            """
            
            st.markdown(agreement_html, unsafe_allow_html=True)
            
            # Download Button for the HTML Agreement Sheet
            st.download_button(
                label="📥 ഡൗൺലോഡ് കരാർ പത്രം (Download Agreement HTML)",
                data=agreement_html,
                file_name=f"Agreement_Loan_{l_id}.html",
                mime="text/html"
            )
            
    conn.close()

# ==========================================
# MODULE 4: SERVICING & LEDGER
# ==========================================
elif choice == "Servicing & Ledger":
    st.header("🗂️ Servicing & Party Ledger Statements")
    
    conn = get_db_connection()
    active_loans = conn.execute("""
        SELECT l.id, p.name, l.principal FROM loans l 
        JOIN parties p ON l.party_id = p.id WHERE l.status='Active'
    """).fetchall()
    
    if not active_loans:
        st.info("No active accounts processing currently.")
    else:
        loan_options = {al['id']: f"Loan #{al['id']} - Account: {al['name']} (₹{al['principal']})" for al in active_loans}
        selected_loan = st.selectbox("Select Active Loan Portfolio File", list(loan_options.keys()), format_func=lambda x: loan_options[x])
        
        tab1, tab2 = st.tabs(["💳 Record Repayment Slip", "📑 View Customer Statements Ledger"])
        
        with tab1:
            with st.form("repayment_form"):
                repay_amt = st.number_input("Repayment Amount Collected (₹)", min_value=0.0, step=100.0)
                repay_date = st.date_input("Processing Settlement Date")
                type_tx = st.selectbox("Payment Structure Target", ["Repayment", "Interest Payment"])
                
                if st.form_submit_button("Post Repayment Entry"):
                    if repay_amt > 0:
                        conn.execute("""
                            INSERT INTO ledger (loan_id, transaction_type, amount, transaction_date)
                            VALUES (?, ?, ?, ?)
                        """, (selected_loan, type_tx, repay_amt, str(repay_date)))
                        conn.commit()
                        st.success(f"Successfully credited payment of ₹{repay_amt:,.2f} to account Ledger #{selected_loan}")
                    else:
                        st.error("Amount must be greater than zero.")
                        
        with tab2:
            st.markdown(f"#### Account Statement Registry for Loan ID: #{selected_loan}")
            ledger_entries = pd.read_sql_query(f"""
                SELECT transaction_type as 'Activity Type', amount as 'Transaction Vol (₹)', 
                       transaction_date as 'Entry Date' 
                FROM ledger WHERE loan_id={selected_loan}
                ORDER BY ROWID ASC
            """, conn)
            st.table(ledger_entries)
    conn.close()

# ==========================================
# BACKUP, DELETE & GOOGLE SHEETS COMPATIBLE EXPORT
# ==========================================
elif choice == "Data Maintenance (Backup/Export)":
    st.header("💾 Core Storage Maintenance & Interoperability Engine")
    
    st.markdown("""
    ### 📊 Compatibility Exports for Google Sheets
    Use the compilation modules below to dump raw database tables into normalized CSV formats. 
    You can import these directly into **Google Sheets** via `File -> Import -> Upload`.
    """)
    
    conn = get_db_connection()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Export Party Registries Matrix")
        df_p = pd.read_sql_query("SELECT * FROM parties", conn)
        csv_p = df_p.to_csv(index=False).encode('utf-8')
        st.download_button("Download Party Profiles CSV", data=csv_p, file_name="parties_master_export.csv", mime="text/csv")
        
    with col2:
        st.markdown("#### Export Active Loan Portfolio Matrix")
        df_l = pd.read_sql_query("SELECT * FROM loans", conn)
        csv_l = df_l.to_csv(index=False).encode('utf-8')
        st.download_button("Download Loan Parameters CSV", data=csv_l, file_name="loans_ledger_export.csv", mime="text/csv")
        
    st.markdown("---")
    st.markdown("### 🗄️ System Bare-Metal Recovery and Snapshot Backups")
    
    with open("gold_loan_system.db", "rb") as db_file:
        db_binary = db_file.read()
        
    st.download_button(
        label="📥 Download Full System Database (.DB File)",
        data=db_binary,
        file_name=f"gold_loan_system_backup_{datetime.now().date()}.db",
        mime="application/octet-stream"
    )
    
    st.markdown("#### 📤 Upload System Recovery Snapshot")
    uploaded_backup = st.file_uploader("Select a valid structural recovery .db payload file", type=["db"])
    if uploaded_backup is not None:
        if st.button("Execute Restoration Block Rewrite Overwrite"):
            with open("gold_loan_system.db", "wb") as f:
                f.write(uploaded_backup.getbuffer())
            st.success("System databases successfully rolled back to selected archival state parameters.")
            st.rerun()
            
    conn.close()


