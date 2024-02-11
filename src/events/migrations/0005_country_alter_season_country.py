# Generated by Django 4.1.10 on 2023-12-10 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_alter_events_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("image", models.ImageField(upload_to="", verbose_name="Флаг")),
            ],
            options={
                "verbose_name": "Страна",
                "verbose_name_plural": "Страны",
            },
        ),
        migrations.AlterField(
            model_name="season",
            name="country",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="events.country"
            ),
        ),
    ]
