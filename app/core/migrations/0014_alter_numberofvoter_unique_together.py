# Generated by Django 4.0.4 on 2022-06-21 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_numberofvoter'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='numberofvoter',
            unique_together={('project',)},
        ),
    ]
