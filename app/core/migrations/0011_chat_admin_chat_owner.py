# Generated by Django 4.0.4 on 2022-06-21 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_voter'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='chat',
            name='owner',
            field=models.BooleanField(default=False),
        ),
    ]