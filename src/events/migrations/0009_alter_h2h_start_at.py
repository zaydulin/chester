# Generated by Django 4.1.10 on 2023-12-19 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_events_start_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='h2h',
            name='start_at',
            field=models.CharField(max_length=500, null=True, verbose_name='Начало'),
        ),
    ]