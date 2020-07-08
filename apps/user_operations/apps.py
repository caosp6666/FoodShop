from django.apps import AppConfig


class UserOperationsConfig(AppConfig):
    name = 'apps.user_operations'

    def ready(self):
        import user_operations.signals
