from reconcile import load_data, reconcile, get_match_rate
from agent import analyze_all_exceptions
import csv

def export_to_csv(matched, analyzed_exceptions, match_rate):
    with open('reconciliation_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # summary row
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Matched', 'Total Exceptions', 'Match Rate'])
        writer.writerow([len(matched), len(analyzed_exceptions), f'{match_rate}%'])
        writer.writerow([])
        
        # matched transactions
        writer.writerow(['MATCHED TRANSACTIONS'])
        writer.writerow(['txn_id'])
        for txn in matched:
            writer.writerow([txn])
        writer.writerow([])
        
        # exceptions
        writer.writerow(['EXCEPTIONS'])
        writer.writerow(['txn_id', 'issue', 'risk', 'razorpay_amount', 'bank_amount', 'ai_analysis'])
        for ex in analyzed_exceptions:
            writer.writerow([
                ex['txn_id'],
                ex['issue'],
                ex.get('risk', 'UNKNOWN'),
                ex['razorpay_amount'],
                ex['bank_amount'],
                ex['ai_analysis']
            ])

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
        export_to_csv(matched, analyzed_exceptions, match_rate)
        print("\n📁 Report exported to reconciliation_report.csv")      
        print("-" * 40)

if __name__ == "__main__":
    generate_report()


