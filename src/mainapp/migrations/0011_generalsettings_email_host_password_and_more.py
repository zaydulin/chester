# Generated by Django 4.2 on 2024-02-10 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_alter_generalsettings_rapidapi_key_events_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsettings',
            name='email_host_password',
            field=models.TextField(default=1, verbose_name='Email Site Password'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generalsettings',
            name='email_host_user',
            field=models.TextField(default=1, verbose_name='Email Site User'),
            preserve_default=False,
        ),
    ]
