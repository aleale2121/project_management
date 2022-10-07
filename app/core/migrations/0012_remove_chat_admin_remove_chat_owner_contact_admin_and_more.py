# Generated by Django 4.0.4 on 2022-06-21 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_chat_admin_chat_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='owner',
        ),
        migrations.AddField(
            model_name='contact',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='owner',
            field=models.BooleanField(default=False),
        ),
    ]