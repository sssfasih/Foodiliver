# Generated by Django 4.0.1 on 2022-01-30 08:30

from django.db import migrations, models
import json.encoder


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='Bill',
            field=models.JSONField(default={}, encoder=json.encoder.JSONEncoder),
        ),
    ]
