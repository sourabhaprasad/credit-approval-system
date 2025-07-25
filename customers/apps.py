from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command


def run_fix_sequences(sender, **kwargs):
    try:
        call_command('fix_sequences')
        print("Auto sequence reset after migrate.")
    except Exception as e:
        print(f"Auto sequence reset failed: {e}")


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'

    def ready(self):
        post_migrate.connect(run_fix_sequences, sender=self)
