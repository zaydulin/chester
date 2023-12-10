import os
from celery import Celery

# Установка переменной окружения для настройки Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")

# Создание экземпляра Celery
celery_app = Celery("_project")

# Загрузка настроек Celery из настроек Django
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение и регистрация всех задач Django из файлов tasks.py
celery_app.autodiscover_tasks()
