import pandas as pd

def load_data():
    razorpay = pd.read_csv('data/razorpay_records.csv')
    bank = pd.read_csv('data/bank_statement.csv')
    return razorpay, bank

def reconcile(razorpay, bank):
    matched = []
    exceptions = []

    for _, rp_row in razorpay.iterrows():
        bank_row = bank[bank['txn_id'] == rp_row['txn_id']]

        if bank_row.empty:
            exceptions.append({
                'txn_id': rp_row['txn_id'],
                'issue': 'missing_in_bank',
                'razorpay_amount': rp_row['amount'],
                'bank_amount': None
            })
        elif bank_row.iloc[0]['amount'] != rp_row['amount']:
            exceptions.append({
                'txn_id': rp_row['txn_id'],
                'issue': 'amount_mismatch',
                'razorpay_amount': rp_row['amount'],
                'bank_amount': bank_row.iloc[0]['amount']
            })
        else:
            matched.append(rp_row['txn_id'])

    # check for extra entries in bank not in razorpay
    for _, bank_row in bank.iterrows():
        if bank_row['txn_id'] not in razorpay['txn_id'].values:
            exceptions.append({
                'txn_id': bank_row['txn_id'],
                'issue': 'extra_in_bank',
                'razorpay_amount': None,
                'bank_amount': bank_row['amount']
            })

    return matched, exceptions

def get_match_rate(matched, exceptions):
    total = len(matched) + len(exceptions)
    return round((len(matched) / total) * 100, 2)