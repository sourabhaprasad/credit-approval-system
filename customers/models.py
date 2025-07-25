from django.db import models

class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
