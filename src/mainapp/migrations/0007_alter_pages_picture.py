# Generated by Django 4.2 on 2023-12-29 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_alter_pages_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='pages/img', verbose_name='Изображениe'),
        ),
    ]
