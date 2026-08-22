from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_exception(exception):
    prompt = f"""
    You are a finance reconciliation expert.
    
    A transaction has failed reconciliation with the following details:
    - Transaction ID: {exception['txn_id']}
    - Issue Type: {exception['issue']}
    - Razorpay Amount: {exception['razorpay_amount']}
    - Bank Amount: {exception['bank_amount']}
    
    In 2-3 sentences:
    1. Explain what this exception means in simple terms
    2. Suggest the most likely cause
    3. Recommend the next action to resolve it
    """
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text

def analyze_all_exceptions(exceptions):
    results = []
    for exception in exceptions:
        analysis = analyze_exception(exception)
        results.append({
            'txn_id': exception['txn_id'],
            'issue': exception['issue'],
            'razorpay_amount': exception['razorpay_amount'],
            'bank_amount': exception['bank_amount'],
            'ai_analysis': analysis
        })
    return results