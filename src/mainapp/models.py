from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from dadata import Dadata
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
from ipware import get_client_ip  # Import the function to get the client's IP address
from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from events.models import Events


###############################################
###     #####    #####   ####  ###        #####
##  ########  ##  ####  #  ##  ######  ########
##  #######        ###  ##  #  ######  ########
###    ###  ######  ##  ###    ######  ########
###############################################


class GeneralSettings(models.Model):
    REGISTRATION = [
        (1, "Включено"),
        (2, "Отключено"),
    ]
    logo = models.ImageField("Логотип", blank=True, null=True)
    logo_light = models.ImageField("Логотип светлый", blank=True, null=True)
    favicon = models.ImageField("Фавикон", blank=True, null=True)
    name = models.CharField("Название", max_length=500, blank=True, null=True)
    content = models.TextField("Контент", max_length=500, blank=True, null=True)
    copyright_text = models.CharField("© Копирайт", max_length=500, blank=True, null=True)
    registration = models.PositiveSmallIntegerField("Регистрация", choices=REGISTRATION, default=1)
    of_register_message = models.TextField(
        "Сообщение при отключение регистрации", max_length=500, blank=True, null=True
    )
    yandex_metrika_link = models.TextField("Ссылка Яндекс Метрика")
    update_players_in_team = models.BooleanField("Обновить игроков во всех комнадах",default=False)
    time_interval_on_create_events = models.PositiveIntegerField("Указать временной интервал на создание событий(в секундах)")
    time_interval_on_update_events = models.PositiveIntegerField("Указать временной интервал на обновление событий(в секундах)")
    time_interval_on_update_events_statistic= models.PositiveIntegerField(
        "Указать временной интервал на обновление статистик событий(в секундах)")

    def __str__(self):
        return "Общая настройка"

    class Meta:
        verbose_name = "Общая настройка"
        verbose_name_plural = "Общие настройки"


class Pages(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    data = models.DateTimeField(auto_now=True)
    name = models.CharField("Название", max_length=500, null=True)
    description = models.TextField("Описание", null=True)
    title = models.CharField("Заголовок", max_length=500, null=True)
    content = models.TextField("Мета-описание", max_length=500, null=True)
    slug = models.SlugField("Ссылка", max_length=160, unique=True)

    def get_absolute_url(self):
        return reverse("pages", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"


class Baners(models.Model):
    TYPE = [
        (1, "Сайдбар"),
        (2, "Горизонтальный-ВЕРХ"),
        (3, "Горизонтальный-НИЗ"),
        (4, "C право"),
        (5, "С лево"),
    ]
    data = models.DateTimeField(auto_now=True)
    baner = models.ImageField("Изображения", blank=True, null=True)
    slug = models.CharField("Ссылка", max_length=160)
    type = models.PositiveSmallIntegerField("Тип", choices=TYPE, blank=True, null=True)

    class Meta:
        verbose_name = "Банер"
        verbose_name_plural = "Банеры"


class Banerspopap(models.Model):
    TYPE = [
        (1, "Включить"),
        (2, "Выключить"),
    ]
    data = models.DateTimeField(auto_now=True)
    baner = models.ImageField("Изображения", blank=True, null=True)
    slug = models.CharField("Ссылка", max_length=160)
    type = models.PositiveSmallIntegerField("Тип", choices=TYPE, blank=True, null=True)

    class Meta:
        verbose_name = "Банер всплывающий"
        verbose_name_plural = "Банеры всплывающие"


class Stopwords(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Стоп слова", max_length=120)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Стоп слово"
        verbose_name_plural = "Стоп слова"


###################################################################################
##        ##      #####      #####          ####  ###    #####     ###  ###########
##  ####  ##  ###  ###  ####  ###  ###  ###  ###  ##  #  ####  ##  ###       ######
##  ####  ##      ####  ####  ####          ####  #  ##  ###  ###  ###  ####  #####
##  ####  ##  #########      #########  ########    ###  ##  ####  ###       ######
###################################################################################
def get_user_dir(instance, filename):
    extension = filename.split(".")[-1]
    return f"users/user_{instance.id}.{extension}"


class User(AbstractUser):
    GENDER_CHOICE = [
        (1, "Мужской"),
        (2, "Женский"),
    ]
    TIME_ZONE = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
    ]
    is_guest = models.BooleanField(default=False, verbose_name="Гость")
    is_moderar = models.BooleanField(default=False, verbose_name="Админ")
    login_status = models.BooleanField(default=False, verbose_name="Статус")
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    username = models.CharField(max_length=30, unique=True)
    avatar = models.ImageField(
        upload_to=get_user_dir, blank=True, verbose_name="Аватар", default="default/profile/profile-thumb.jpg"
    )
    birthday = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    age = models.IntegerField(verbose_name="Возвраст", blank=True, null=True)
    gender = models.PositiveSmallIntegerField("Пол", choices=GENDER_CHOICE, blank=True, null=True)
    time_zone = models.PositiveSmallIntegerField("Часовой пояс", choices=TIME_ZONE, blank=True, null=True)
    sum_message = models.IntegerField("Сообщений в чате", blank=True, null=True, default=0)
    sum_bal = models.IntegerField("Баллы", blank=True, null=True, default=0)
    groups = models.ManyToManyField(
        Group,
        verbose_name="Groups",
        blank=True,
        related_name="custom_user_set",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="User permissions",
        blank=True,
        related_name="custom_user_set_permissions",
    )
    date_of_registration = models.DateField(auto_now_add=True, verbose_name="дата регистрации")

    def save(self, *args, **kwargs):
        if self.birthday:
            today = date.today()
            age = (
                today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
            )
            self.age = age
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Messages(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    message = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    stopwords = models.CharField(max_length=130, blank=True, null=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)  # Связь с событием

    def __str__(self):
        return f"Message by {self.user.username} on {self.event.name}"

    def save(self, *args, **kwargs):
        # Split the message into words
        words = self.message.split()

        # Create a case-insensitive OR condition for the stopwords
        stopword_conditions = models.Q()
        for word in words:
            stopword_conditions |= models.Q(name__icontains=word)

        # Query the Stopword model to find words in the message that match stop words
        stopwords = Stopwords.objects.filter(stopword_conditions).values_list("name", flat=True)

        # Update the 'blocked' field based on the result
        self.blocked = len(stopwords) > 0

        # Store matched stop words in the 'stopwords' field
        self.stopwords = ",".join(stopwords)

        super(Messages, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

@receiver(post_save, sender=Messages)
def delete_emprty_message(sender, instance, **kwargs):
    if instance.message == '':
        instance.delete()

class Bookmarks(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="Относится", blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"


class Views(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser = models.CharField("Браузер", max_length=250, blank=True, null=True)
    operationsistem = models.CharField("Операционая система", max_length=250, blank=True, null=True)
    region = models.CharField("Регион", max_length=2500, blank=True, null=True)
    url = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        dadata = Dadata("32b0e4e3d9b0fb24499c8414a81dd9411bd8a5ac")
        region = dadata.iplocate(self.ip_address)
        self.region = region
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user is not None:
            return str(self.user.username)
        else:
            return "Anonymous User"

    class Meta:
        verbose_name = "Просмотр"
        verbose_name_plural = "Просмотры"
