# Generated by Django 4.1.7 on 2023-11-21 09:04

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mainapp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_guest', models.BooleanField(default=False, verbose_name='Гость')),
                ('is_moderar', models.BooleanField(default=False, verbose_name='Админ')),
                ('login_status', models.BooleanField(default=False, verbose_name='Статус')),
                ('blocked', models.BooleanField(default=False, verbose_name='Заблокирован')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('avatar', models.ImageField(blank=True, default='default/profile/profile-thumb.jpg', upload_to=mainapp.models.get_user_dir, verbose_name='Аватар')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='Возвраст')),
                ('gender', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Мужской'), (2, 'Женский')], null=True, verbose_name='Пол')),
                ('time_zone', models.PositiveSmallIntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3')], null=True, verbose_name='Часовой пояс')),
                ('sum_message', models.IntegerField(blank=True, default=0, null=True, verbose_name='Сообщений в чате')),
                ('sum_bal', models.IntegerField(blank=True, default=0, null=True, verbose_name='Баллы')),
                ('date_of_registration', models.DateField(auto_now_add=True, verbose_name='дата регистрации')),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_set', to='auth.group', verbose_name='Groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_set_permissions', to='auth.permission', verbose_name='User permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Baners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now=True)),
                ('baner', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Изображения')),
                ('slug', models.CharField(max_length=160, verbose_name='Ссылка')),
                ('type', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Сайдбар'), (2, 'Горизонтальный-ВЕРХ'), (3, 'Горизонтальный-НИЗ'), (4, 'C право'), (5, 'С лево')], null=True, verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Банер',
                'verbose_name_plural': 'Банеры',
            },
        ),
        migrations.CreateModel(
            name='Banerspopap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now=True)),
                ('baner', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Изображения')),
                ('slug', models.CharField(max_length=160, verbose_name='Ссылка')),
                ('type', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Включить'), (2, 'Выключить')], null=True, verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Банер всплывающий',
                'verbose_name_plural': 'Банеры всплывающие',
            },
        ),
        migrations.CreateModel(
            name='GeneralSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Логотип')),
                ('logo_light', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Логотип светлый')),
                ('favicon', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фавикон')),
                ('name', models.CharField(blank=True, max_length=500, null=True, verbose_name='Название')),
                ('content', models.TextField(blank=True, max_length=500, null=True, verbose_name='Контент')),
                ('copyright_text', models.CharField(blank=True, max_length=500, null=True, verbose_name='© Копирайт')),
                ('registration', models.PositiveSmallIntegerField(choices=[(1, 'Включено'), (2, 'Отключено')], default=1, verbose_name='Регистрация')),
                ('of_register_message', models.TextField(blank=True, max_length=500, null=True, verbose_name='Сообщение при отключение регистрации')),
            ],
            options={
                'verbose_name': 'Общая настройка',
                'verbose_name_plural': 'Общие настройки',
            },
        ),
        migrations.CreateModel(
            name='Pages',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('data', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500, null=True, verbose_name='Название')),
                ('description', models.TextField(null=True, verbose_name='Описание')),
                ('title', models.CharField(max_length=500, null=True, verbose_name='Заголовок')),
                ('content', models.TextField(max_length=500, null=True, verbose_name='Мета-описание')),
                ('slug', models.SlugField(max_length=160, unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Страница',
                'verbose_name_plural': 'Страницы',
            },
        ),
        migrations.CreateModel(
            name='Stopwords',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120, verbose_name='Стоп слова')),
            ],
            options={
                'verbose_name': 'Стоп слово',
                'verbose_name_plural': 'Стоп слова',
            },
        ),
        migrations.CreateModel(
            name='Views',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('browser', models.CharField(blank=True, max_length=250, null=True, verbose_name='Браузер')),
                ('operationsistem', models.CharField(blank=True, max_length=250, null=True, verbose_name='Операционая система')),
                ('region', models.CharField(blank=True, max_length=2500, null=True, verbose_name='Регион')),
                ('url', models.CharField(max_length=200)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Просмотр',
                'verbose_name_plural': 'Просмотры',
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.BooleanField(default=False, verbose_name='Заблокирован')),
                ('stopwords', models.CharField(blank=True, max_length=130, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.events')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
        migrations.CreateModel(
            name='Bookmarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Относится')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Закладка',
                'verbose_name_plural': 'Закладки',
            },
        ),
    ]
