# Generated by Django 4.1.10 on 2024-01-18 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_alter_periods_away_score_alter_periods_home_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_id',
            field=models.CharField(max_length=10, null=True, verbose_name='ID игрока API'),
        ),
    ]
