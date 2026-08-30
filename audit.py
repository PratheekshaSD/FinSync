import csv
from datetime import datetime

AUDIT_FILE='audit_trail.csv'

def init_audit():
    with open(AUDIT_FILE, 'w', newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow(['timestamp','txn_id','action','details'])

def log(txn_id,action,details):
    with open(AUDIT_FILE,'a',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            txn_id,
            action,
            details
        ])