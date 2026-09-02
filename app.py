import streamlit as st
import pandas as pd
from reconcile import load_data, reconcile, get_match_rate
from agent import analyze_all_exceptions
from report import export_to_csv

st.set_page_config(page_title="FinSync", page_icon="💳", layout="wide")
st.title("💳 FinSync — AI Reconciliation Agent")
st.markdown("Upload your Razorpay records and bank statement to reconcile automatically.")

col1, col2 = st.columns(2)

with col1:
    razorpay_file = st.file_uploader("Upload Razorpay Records", type="csv")

with col2:
    bank_file = st.file_uploader("Upload Bank Statement", type="csv")

if razorpay_file and bank_file:
    if st.button("🚀 Run Reconciliation"):
        with st.spinner("Reconciling..."):
            razorpay = pd.read_csv(razorpay_file)
            bank = pd.read_csv(bank_file)
            
            matched, exceptions = reconcile(razorpay, bank)
            match_rate = get_match_rate(matched, exceptions)

        st.success(f"✅ Reconciliation Complete! Match Rate: {match_rate}%")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Total Matched", len(matched))
        
        with col4:
            st.metric("Total Exceptions", len(exceptions))
        
        with col5:
            st.metric("Match Rate", f"{match_rate}%")

        st.subheader("✅ Matched Transactions")
        st.dataframe(pd.DataFrame(matched, columns=["txn_id"]))

        st.subheader("❌ Exceptions")
        
        for ex in exceptions:
            risk = ex.get('risk', 'UNKNOWN')
            
            if 'CRITICAL' in str(risk):
                st.error(f"🚨🚨 {ex['txn_id']} — {ex['issue']} | Risk: {risk} | Amount: {ex['razorpay_amount'] or ex['bank_amount']}")
            elif 'HIGH' in str(risk):
                st.warning(f"🚨 {ex['txn_id']} — {ex['issue']} | Risk: {risk} | Amount: {ex['razorpay_amount'] or ex['bank_amount']}")
            else:
                st.info(f"ℹ️ {ex['txn_id']} — {ex['issue']} | Risk: {risk} | Amount: {ex['razorpay_amount'] or ex['bank_amount']}")

        st.subheader("🤖 AI Analysis")
        with st.spinner("Analyzing exceptions with AI..."):
            analyzed_exceptions = analyze_all_exceptions(exceptions)
        
        for ex in analyzed_exceptions:
            with st.expander(f"{ex['txn_id']} — {ex['issue']}"):
                st.write(f"**Risk:** {ex.get('risk', 'UNKNOWN')}")
                st.write(f"**Razorpay Amount:** {ex['razorpay_amount']}")
                st.write(f"**Bank Amount:** {ex['bank_amount']}")
                st.write(f"**AI Analysis:** {ex['ai_analysis']}")
        
        export_to_csv(matched, analyzed_exceptions, match_rate)
        with open('reconciliation_report.csv', 'rb') as f:
            st.download_button(
                label="📁 Download Report CSV",
                data=f,
                file_name="reconciliation_report.csv",
                mime="text/csv"
            )