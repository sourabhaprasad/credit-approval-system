from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = "Reset all primary key sequences to the max ID in each table."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for model in apps.get_models():
                table = model._meta.db_table
                pk_name = model._meta.pk.column

                if not pk_name:
                    continue

                try:
                    cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('"{table}"', '{pk_name}'),
                            COALESCE((SELECT MAX({pk_name}) FROM "{table}"), 1),
                            true
                        );
                    """)
                    self.stdout.write(self.style.SUCCESS(f"Sequence reset for table: {table}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Skipping {table}: {e}"))

        self.stdout.write(self.style.SUCCESS("All sequences reset successfully."))
