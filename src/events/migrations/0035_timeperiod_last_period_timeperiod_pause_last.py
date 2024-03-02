# Generated by Django 4.2 on 2024-03-02 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_timeperiod'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeperiod',
            name='last_period',
            field=models.CharField(max_length=500, null=True, verbose_name='Длительность прошлого периода'),
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='pause_last',
            field=models.CharField(max_length=500, null=True, verbose_name='Длительность прошлого перерыва'),
        ),
    ]
