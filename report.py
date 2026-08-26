from reconcile import load_data, reconcile, get_match_rate
from agent import analyze_all_exceptions

def generate_report():
    # load data
    razorpay, bank = load_data()
    
    # reconcile
    matched, exceptions = reconcile(razorpay, bank)
    
    # match rate
    match_rate = get_match_rate(matched, exceptions)
    
    # ai analysis on exceptions
    print("🤖 Analyzing exceptions with AI...\n")
    analyzed_exceptions = analyze_all_exceptions(exceptions)
    
    # print report
    print("=" * 60)
    print("RECONCILIATION REPORT")
    print("=" * 60)
    print(f"Total Matched: {len(matched)}")
    print(f"Total Exceptions: {len(exceptions)}")
    print(f"Match Rate: {match_rate}%")
    print("=" * 60)
    
    print("\n✅ MATCHED TRANSACTIONS:")
    for txn in matched:
        print(f"  - {txn}")
    
    print("\n❌ EXCEPTIONS:")
    for ex in analyzed_exceptions:
        print(f"\n  Transaction: {ex['txn_id']}")
        print(f"  Issue: {ex['issue']}")
        print(f"  Risk: {ex.get('risk', 'UNKNOWN')}")
        print(f"  Razorpay Amount: {ex['razorpay_amount']}")
        print(f"  Bank Amount: {ex['bank_amount']}")
        print(f"  AI Analysis: {ex['ai_analysis']}")
        print("-" * 40)

if __name__ == "__main__":
    generate_report()