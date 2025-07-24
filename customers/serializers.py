from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 'age',
            'phone_number', 'monthly_salary', 'approved_limit',
            'current_debt'
        ]
