from django.apps import AppConfig


class AppAccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_accounts'

def ready(self):
    import app_accounts.signals