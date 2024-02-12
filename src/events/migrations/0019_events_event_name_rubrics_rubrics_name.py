# Generated by Django 4.2 on 2024-01-28 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_alter_player_player_id'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='events',
            index=models.Index(fields=['name'], name='event_name'),
        ),
        migrations.AddIndex(
            model_name='rubrics',
            index=models.Index(fields=['name'], name='rubrics_name'),
        ),
    ]
