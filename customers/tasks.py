import pandas as pd
from celery import shared_task
from .models import Customer
from loans.models import Loan
from datetime import datetime

@shared_task
def ingest_data():
    import pandas as pd
    from .models import Customer
    from loans.models import Loan
    from datetime import datetime

    # Helper to normalize column names
    def normalize_columns(df):
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        return df

    # Load customer data
    customer_df = pd.read_excel('/app/data/customer_data.xlsx')
    customer_df = normalize_columns(customer_df)

    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['customer_id'],
            defaults={
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'phone_number': row.get('phone_number', ''),
                'monthly_salary': row.get('monthly_salary', 0),
                'approved_limit': row.get('approved_limit', 0),
                'current_debt': row.get('current_debt', 0),
            }
        )

    # Load loan data
    loan_df = pd.read_excel('/app/data/loan_data.xlsx')
    loan_df = normalize_columns(loan_df)

    for _, row in loan_df.iterrows():
        Loan.objects.update_or_create(
            loan_id=row['loan_id'],
            defaults={
                'customer_id': row['customer_id'],
                'loan_amount': row.get('loan_amount', 0),
                'tenure': row.get('tenure', 0),
                'interest_rate': row.get('interest_rate', 0),
                'monthly_repayment': row.get('monthly_payment', 0),
                'emis_paid_on_time': row.get('emis_paid_on_time', 0),
                'start_date': pd.to_datetime(row.get('date_of_approval')).date(),
                'end_date': pd.to_datetime(row.get('end_date')).date(),
            }
        )

    return "Data Ingestion Completed"
