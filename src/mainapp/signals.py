from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Messages, User


@receiver(post_save, sender=Messages)
def update_user_message_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.sum_message += 1  # Увеличиваем количество сообщений пользователя
        user.save()


@receiver(post_save, sender=Messages)
def update_user_bal(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.sum_bal += 1  # Увеличиваем количество сообщений пользователя
        user.save()
