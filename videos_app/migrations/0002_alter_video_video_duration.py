# Generated by Django 5.1.3 on 2024-11-17 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_duration',
            field=models.FloatField(),
        ),
    ]
