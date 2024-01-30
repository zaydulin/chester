# Generated by Django 4.2 on 2024-01-28 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_rename_event_name_events_even_name_8aa231_idx_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='events',
            name='events_even_name_8aa231_idx',
        ),
        migrations.AddIndex(
            model_name='events',
            index=models.Index(fields=['rubrics'], name='events_even_rubrics_1fba39_idx'),
        ),
    ]