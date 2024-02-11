import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from dadata import Dadata
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
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
    headerImage = models.ImageField("Шапка сайта", blank=True, null=True)
    content = models.TextField("Контент", max_length=500, blank=True, null=True)
    copyright_text = models.CharField("© Копирайт", max_length=500, blank=True, null=True)
    registration = models.PositiveSmallIntegerField("Регистрация", choices=REGISTRATION, default=1)
    of_register_message = models.TextField(
        "Сообщение при отключение регистрации", max_length=500, blank=True, null=True
    )
    yandex_metrika_link = models.TextField("Ссылка Яндекс Метрика")
    rapidapi_key_events = models.TextField("FlashScoreRapid", help_text='<a href="https://rapidapi.com/tipsters/api/flashlive-sports" target="_blank">Cсылка</a>',
                                           blank=True, null=True)
    rapidapi_key_stream = models.TextField("SoccerVideosRapid",
                                           help_text='<a href="https://rapidapi.com/scorebat/api/free-football-soccer-videos/" target="_blank">Cсылка</a>',
                                           blank=True, null=True)
    email_host = models.TextField("Email Site HOST")
    email_port = models.TextField("Email Site PORT")
    email_host_user = models.TextField("Email Site User")
    email_host_password = models.TextField("Email Site Password")
    def __str__(self):
        return "Общая настройка"

    def save(self, *args, **kwargs):
        # Сначала сохраняем модель
        super().save(*args, **kwargs)

        # Путь к файлу, куда будем сохранять данные
        file_path = os.path.join(settings.BASE_DIR, 'media/smtp.py')

        # Сохраняем данные в текстовый файл
        with open(file_path, 'w') as f:
            f.write(f"EMAIL_HOST = '{self.email_host}'\n")
            f.write(f"EMAIL_PORT = '{self.email_port}'\n")
            f.write(f"EMAIL_USE_TLS = {self.email_use_tls}\n")
            f.write(f"EMAIL_USE_SSL = {self.email_use_ssl}\n")
            f.write(f"EMAIL_HOST_USER = '{self.email_host_user}'\n")
            f.write(f"EMAIL_HOST_PASSWORD = '{self.email_host_password}'\n")
            f.write(f"DEFAULT_FROM_EMAIL = '{self.default_from_email}'\n")
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
    slug = models.SlugField("Ссылка на сайте", max_length=160,blank=True, null=True)
    other_link = models.TextField("Ссылка на другой источник", blank=True,null=True)
    picture = models.ImageField("Изображениe", upload_to='pages/img', blank=True, null=True)

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
        (1, "GMT-12:00"),
        (2, "GMT-11:00"),
        (3, "GMT-10:00"),
        (4, "GMT-9:00"),
        (5, "GMT-8:00"),
        (6, "GMT-7:00"),
        (7, "GMT-6:00"),
        (8, "GMT-5:00"),
        (9, "GMT-4:00"),
        (10, "GMT-3:00"),
        (11, "GMT-2:00"),
        (12, "GMT-1:00"),
        (13, "GMT±00:00"),
        (14, "GMT+01:00"),
        (15, "GMT+02:00"),
        (16, "GMT+03:00"),
        (17, "GMT+04:00"),
        (18, "GMT+05:00"),
        (19, "GMT+06:00"),
        (20, "GMT+07:00"),
        (21, "GMT+08:00"),
        (22, "GMT+09:00"),
        (23, "GMT+10:00"),
        (24, "GMT+11:00"),
        (25, "GMT+12:00"),
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
