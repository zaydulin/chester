# Generated by Django 4.2 on 2024-01-14 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_alter_periods_event_api_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periods',
            name='away_score',
            field=models.IntegerField(default=0, verbose_name='Очки гостей'),
        ),
        migrations.AlterField(
            model_name='periods',
            name='home_score',
            field=models.IntegerField(default=0, verbose_name='Очки дома'),
        ),
    ]