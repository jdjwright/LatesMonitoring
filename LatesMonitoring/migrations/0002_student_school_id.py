# Generated by Django 4.2.17 on 2024-12-12 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LatesMonitoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='school_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]