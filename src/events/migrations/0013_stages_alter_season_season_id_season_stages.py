# Generated by Django 4.2 on 2024-01-05 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_alter_team_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage_id', models.TextField(null=True, verbose_name='Stage_Id')),
                ('stage_name', models.TextField(null=True, verbose_name='Stage_Name')),
            ],
            options={
                'verbose_name': 'Стадия',
                'verbose_name_plural': 'Стадии',
            },
        ),
        migrations.AlterField(
            model_name='season',
            name='season_id',
            field=models.CharField(max_length=500, null=True, verbose_name='ACTUAL_TOURNAMENT_SEASON_ID'),
        ),
        migrations.AddField(
            model_name='season',
            name='stages',
            field=models.ManyToManyField(to='events.stages', verbose_name='Стадии'),
        ),
    ]
