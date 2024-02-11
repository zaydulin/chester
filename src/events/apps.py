from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = "Спортивное мероприятие"
    verbose_name_plural = "Спортивные мероприятия"