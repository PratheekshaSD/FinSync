import pandas as pd
from thefuzz import fuzz

def normalize_id(txn_id):
    return str(txn_id).upper().replace('-','').replace('_','').strip()

def detect_duplicates(df):
    duplicates=df[df.duplicated(subset=['txn_id'],keep=False)]
    return duplicates['txn_id'].unique().tolist()

def get_risk_level(amount):
    if amount is None:
        return 'UNKNOWN'
    amount=float(amount)
    if amount>=100000:
        return 'CRITICAL 🚨🚨'
    elif amount>=10000:
        return 'HIGH 🚨'
    else:
        return 'LOW'

def load_settlement_report():
    settlement=pd.read_csv('data/settlement_report.csv')
    settlement['txn_id']=settlement['txn_id'].apply(normalize_id)
    return settlement

def check_settlement(txn_id, razorpay_amount,bank_amount, settlement):
    row=settlement[settlement['txn_id']==txn_id]
    if row.empty:
        return 'amount_mismatch',None
    fee=row.iloc[0]['fee']
    fee_type=row.iloc[0]['fee_type']

    if fee_type=='PENDING':
        return 'settlement_pending',fee_type

    expected_bank_amount=razorpay_amount-fee
    if expected_bank_amount==bank_amount:
        return 'resolved_by_fee', fee_type
    else:
        return 'amount_mismatch',fee_type

def normalize_merchant(name):
    return str(name).upper().strip()

def fuzzy_match_merchant(name1,name2,threshold=80):
    n1=normalize_merchant(name1)
    n2=normalize_merchant(name2)
    score=fuzz.token_sort_ratio(n1,n2)
    return score>=threshold,score

def load_data():
    razorpay = pd.read_csv('data/razorpay_records.csv')
    razorpay['txn_id']=razorpay['txn_id'].apply(normalize_id)

    bank = pd.read_csv('data/bank_statement.csv')
    bank['txn_id']=bank['txn_id'].apply(normalize_id)

    return razorpay, bank

def reconcile(razorpay, bank):
    matched = []
    exceptions = []
    settlement=load_settlement_report()
    duplicate_ids=detect_duplicates(bank)
    for dup_id in duplicate_ids:
        exceptions.append({
            'txn_id':dup_id,
            'issue': 'duplicate_in_bank',
            'razorpay_amount':None,
            'bank_amount':bank[bank['txn_id']==dup_id].iloc[0]['amount'],
            'risk': get_risk_level(bank[bank['txn_id']==dup_id].iloc[0]['amount'])
        })

    for _, rp_row in razorpay.iterrows():
        bank_row = bank[bank['txn_id'] == rp_row['txn_id']]

        if bank_row.empty:
            exceptions.append({
                'txn_id': rp_row['txn_id'],
                'issue': 'missing_in_bank',
                'razorpay_amount': rp_row['amount'],
                'bank_amount': None,
                'risk':get_risk_level(rp_row['amount'])
            })
        elif bank_row.iloc[0]['amount'] != rp_row['amount']:
            status, fee_type = check_settlement(
            rp_row['txn_id'],
            rp_row['amount'],
            bank_row.iloc[0]['amount'],
            settlement
            )
            if status == 'resolved_by_fee':
                matched.append(rp_row['txn_id'])
            else:
                exceptions.append({
                    'txn_id': rp_row['txn_id'],
                    'issue': status,
                    'razorpay_amount': rp_row['amount'],
                    'bank_amount': bank_row.iloc[0]['amount'],
                    'risk': get_risk_level(rp_row['amount'])
                })
        else:
            is_match,score=fuzzy_match_merchant(
                rp_row['merchant'],
                bank_row.iloc[0]['merchant']
            )
            if is_match:
                matched.append(rp_row['txn_id'])
            else:
                exceptions.append({
                    'txn_id': rp_row['txn_id'],
                    'issue': 'merchant_mismatch',
                    'razorpay_amount': rp_row['amount'],
                    'bank_amount': bank_row.iloc[0]['amount'],
                    'risk':get_risk_level(rp_row['amount'])
                })

    # check for extra entries in bank not in razorpay
    for _, bank_row in bank.iterrows():
        if bank_row['txn_id'] not in razorpay['txn_id'].values:
            exceptions.append({
                'txn_id': bank_row['txn_id'],
                'issue': 'extra_in_bank',
                'razorpay_amount': None,
                'bank_amount': bank_row['amount'],
                'risk': get_risk_level(bank_row['amount'])
            })

    return matched, exceptions

def get_match_rate(matched, exceptions):
    total = len(matched) + len(exceptions)
    return round((len(matched) / total) * 100, 2)