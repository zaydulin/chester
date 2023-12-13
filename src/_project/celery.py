import os
from celery import Celery

# Установка переменной окружения для настройки Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")

# Создание экземпляра Celery
celery_app = Celery("_project")

# Загрузка настроек Celery из настроек Django
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Указываем параметр для сохранения текущего поведения при повторных попытках соединения с брокером при старте
celery_app.conf.broker_connection_retry_on_startup = True

# Автоматическое обнаружение и регистрация всех задач Django из файлов tasks.py
celery_app.autodiscover_tasks()
