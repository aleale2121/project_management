# Generated by Django 4.0.2 on 2022-03-13 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
