# Generated by Django 4.0.4 on 2022-06-20 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_mark_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]