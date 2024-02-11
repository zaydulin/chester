# Generated by Django 4.2 on 2024-02-01 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_remove_country_sort_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='sort_by',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Позиция в списке'),
        ),
    ]
