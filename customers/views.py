from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import Customer
from .serializers import CustomerSerializer
from .utils import reset_customer_id_sequence 
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

        if Customer.objects.filter(phone_number=data.get('phone_number')).exists():
            return Response(
                {"error": "Customer with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reset_customer_id_sequence()

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
        except IntegrityError as e:
            return Response(
                {"error": f"Database integrity error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
