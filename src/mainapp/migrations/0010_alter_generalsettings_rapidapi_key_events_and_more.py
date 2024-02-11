# Generated by Django 4.2 on 2024-01-31 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_remove_generalsettings_time_interval_on_create_events_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalsettings',
            name='rapidapi_key_events',
            field=models.TextField(blank=True, help_text='<a href="https://rapidapi.com/tipsters/api/flashlive-sports" target="_blank">Cсылка</a>', null=True, verbose_name='FlashScoreRapid'),
        ),
        migrations.AlterField(
            model_name='generalsettings',
            name='rapidapi_key_stream',
            field=models.TextField(blank=True, help_text='<a href="https://rapidapi.com/scorebat/api/free-football-soccer-videos/" target="_blank">Cсылка</a>', null=True, verbose_name='SoccerVideosRapid'),
        ),
    ]
