# Generated by Django 4.2 on 2023-12-20 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_h2h_start_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='image',
            field=models.CharField(max_length=150, verbose_name='Флаг в формате flag-icon flag-icon-<название>'),
        ),
    ]