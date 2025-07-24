from datetime import date, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customers.models import Customer
from loans.models import Loan

class LoanTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=35,
            phone_number="9876543210",
            monthly_salary=80000,
            approved_limit=3000000
        )

    def test_check_eligibility(self):
        url = reverse('check-eligibility')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)

    def test_check_eligibility_invalid_customer(self):
        url = reverse('check-eligibility')
        data = {
            "customer_id": 99999,  # non-existent customer
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_create_loan(self):
        url = reverse('create-loan')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])
        self.assertTrue(Loan.objects.filter(customer=self.customer).exists())

    def test_create_loan_negative_amount(self):
        url = reverse('create-loan')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": -50000,  # invalid loan amount
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])
        self.assertIn("error", response.data)

    def test_view_loans(self):
        Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8500,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        url = reverse('view-customer-loans', args=[self.customer.customer_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_view_loans_invalid_customer(self):
        url = reverse('view-customer-loans', args=[9999])  # invalid customer
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
