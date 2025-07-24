from django.apps import AppConfig
from django.db import connection


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'

    def ready(self):
        # Reset the sequence for customer_id to avoid IntegrityError
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(
                        pg_get_serial_sequence('"customers_customer"', 'customer_id'), 
                        COALESCE((SELECT MAX(customer_id) + 1 FROM "customers_customer"), 1), 
                        false
                    );
                """)
        except Exception as e:
            print(f"Sequence reset failed: {e}")
