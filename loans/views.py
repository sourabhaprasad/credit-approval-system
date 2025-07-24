from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from customers.models import Customer
from .serializers import CheckEligibilityRequestSerializer, CheckEligibilityResponseSerializer
from .serializers import CreateLoanRequestSerializer, CreateLoanResponseSerializer
from .utils import calculate_emi, calculate_credit_score
from loans.models import Loan
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from loans.models import Loan
from customers.models import Customer
from datetime import datetime, timedelta

class CheckEligibilityView(APIView):
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Validate loan_amount and tenure
        if data['loan_amount'] <= 0:
            return Response(
                {"error": "loan_amount must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if data['tenure'] <= 0:
            return Response(
                {"error": "tenure must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(pk=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        credit_score = calculate_credit_score(customer)
        requested_interest = data['interest_rate']

        # Determine minimum interest rate based on score
        if credit_score > 50:
            min_rate = requested_interest
            approved = True
        elif 30 < credit_score <= 50:
            min_rate = max(requested_interest, 12)
            approved = True
        elif 10 < credit_score <= 30:
            min_rate = max(requested_interest, 16)
            approved = True
        else:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": requested_interest,
                "corrected_interest_rate": requested_interest,
                "tenure": data['tenure'],
                "monthly_installment": 0,
                "reason": "Credit score too low"
            }, status=status.HTTP_200_OK)

        # EMI calculation
        monthly_installment = calculate_emi(data['loan_amount'], min_rate, data['tenure'])

        # Check EMI cap
        all_emis = sum(l.monthly_repayment for l in Loan.objects.filter(customer=customer))
        if all_emis + monthly_installment > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": requested_interest,
                "corrected_interest_rate": min_rate,
                "tenure": data['tenure'],
                "monthly_installment": monthly_installment,
                "reason": "EMI exceeds 50% of monthly salary"
            }, status=status.HTTP_200_OK)

        return Response({
            "customer_id": customer.customer_id,
            "approval": approved,
            "interest_rate": requested_interest,
            "corrected_interest_rate": min_rate,
            "tenure": data['tenure'],
            "monthly_installment": monthly_installment
        }, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Validate loan_amount and tenure
        if data['loan_amount'] <= 0:
            return Response(
                {"error": "loan_amount must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if data['tenure'] <= 0:
            return Response(
                {"error": "tenure must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(pk=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Calculate credit score
        credit_score = calculate_credit_score(customer)
        requested_interest = data['interest_rate']

        # Determine min interest rate
        if credit_score > 50:
            min_rate = requested_interest
        elif 30 < credit_score <= 50:
            min_rate = max(requested_interest, 12)
        elif 10 < credit_score <= 30:
            min_rate = max(requested_interest, 16)
        else:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Credit score too low",
                "monthly_installment": 0
            }, status=status.HTTP_200_OK)

        # EMI calculation
        monthly_installment = calculate_emi(data['loan_amount'], min_rate, data['tenure'])

        # Check EMI cap
        all_emis = sum(l.monthly_repayment for l in Loan.objects.filter(customer=customer))
        if all_emis + monthly_installment > 0.5 * customer.monthly_salary:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "EMI exceeds 50% of monthly salary",
                "monthly_installment": monthly_installment
            }, status=status.HTTP_200_OK)

        # 2. Create loan record
        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=(data['tenure'] * 30))  # approx tenure in days
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=min_rate,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date,
        )

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": monthly_installment
        }, status=status.HTTP_201_CREATED)


class ViewLoanDetail(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, pk=loan_id)
        customer = loan.customer

        response_data = {
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "tenure": loan.tenure
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class ViewCustomerLoans(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id)
        loans = Loan.objects.filter(customer=customer)

        response_data = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emis_paid_on_time
            response_data.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": repayments_left
            })

        return Response(response_data, status=status.HTTP_200_OK)
