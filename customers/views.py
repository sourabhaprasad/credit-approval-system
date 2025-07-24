from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import Customer
from .serializers import CustomerSerializer
import math


class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data

        required_fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_income']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            monthly_income = int(data.get('monthly_income'))
        except ValueError:
            return Response({"error": "monthly_income must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        approved_limit = math.ceil((36 * monthly_income) / 100000) * 100000

        try:
            customer = Customer.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                age=data.get('age'),
                phone_number=data.get('phone_number'),
                monthly_salary=monthly_income,
                approved_limit=approved_limit,
                current_debt=0
            )
        except IntegrityError:
            return Response(
                {"error": "Customer with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
