import math
from datetime import datetime
from loans.models import Loan

def calculate_emi(principal, annual_interest_rate, tenure_months):
    """
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where:
    P = principal loan amount
    r = monthly interest rate (decimal)
    n = tenure in months
    """
    r = (annual_interest_rate / 100) / 12
    n = tenure_months
    if r == 0:
        return principal / n
    emi = principal * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)
    return round(emi, 2)

def calculate_credit_score(customer):
    score = 100
    now = datetime.now()

    loans = Loan.objects.filter(customer=customer)

    # 1. Past loans paid on time
    on_time_ratio = 0
    if loans.exists():
        total_emis = sum([loan.tenure for loan in loans])
        on_time_emis = sum([loan.emis_paid_on_time for loan in loans])
        if total_emis > 0:
            on_time_ratio = on_time_emis / total_emis
        score -= int((1 - on_time_ratio) * 40)  # weight 40 points

    # 2. Number of loans taken in the past
    if loans.count() > 5:
        score -= 10

    # 3. Loan activity in current year
    current_year_loans = loans.filter(start_date__year=now.year)
    if current_year_loans.count() > 2:
        score -= 10

    # 4. Loan approved volume
    total_loan_amount = sum([loan.loan_amount for loan in loans])
    if total_loan_amount > customer.approved_limit:
        score = 0

    return max(score, 0)
