from django.db import connection

def reset_customer_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('"customers_customer"', 'customer_id'),
                COALESCE((SELECT MAX(customer_id) FROM "customers_customer"), 1),
                true
            );
        """)
