# Generated by Django 4.1.10 on 2024-02-11 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_remove_generalsettings_default_from_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsettings',
            name='default_from_email',
            field=models.TextField(default=1, verbose_name='Email Site HOST'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generalsettings',
            name='email_use_ssl',
            field=models.BooleanField(default=False, verbose_name='Use SSL'),
        ),
        migrations.AddField(
            model_name='generalsettings',
            name='email_use_tls',
            field=models.BooleanField(default=False, verbose_name='Use TLS'),
        ),
    ]
