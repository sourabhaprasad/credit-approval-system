from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customers.models import Customer

class CustomerTests(APITestCase):
    def test_register_customer(self):
        url = reverse('register-customer')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "monthly_income": 60000,
            "phone_number": "9123456789"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('approved_limit', response.data)
        self.assertTrue(Customer.objects.filter(phone_number="9123456789").exists())

    def test_register_customer_missing_income(self):
        """Test registration with missing monthly_income"""
        url = reverse('register-customer')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "phone_number": "9123456799"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monthly_income", response.data.get("error", ""))
