# Generated by Django 4.2 on 2024-01-28 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_events_event_name_rubrics_rubrics_name'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='events',
            new_name='events_even_name_8aa231_idx',
            old_name='event_name',
        ),
        migrations.RenameIndex(
            model_name='rubrics',
            new_name='events_rubr_name_7e8f5f_idx',
            old_name='rubrics_name',
        ),
    ]
