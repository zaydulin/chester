from django.apps import AppConfig


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'
    verbose_name = "Общие настройки"
    verbose_name_plural = "Общие настройки"

    def ready(self):
        import mainapp.signals