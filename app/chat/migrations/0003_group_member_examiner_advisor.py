# Generated by Django 4.0.2 on 2022-03-26 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_coordinator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=25)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='core.batch')),
            ],
            options={
                'unique_together': {('group_name', 'batch')},
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.group')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.student')),
            ],
            options={
                'unique_together': {('group', 'member')},
            },
        ),
        migrations.CreateModel(
            name='Examiner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('examiner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examiners', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examiners', to='core.group')),
            ],
            options={
                'unique_together': {('group', 'examiner')},
            },
        ),
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advisors', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advisors', to='core.group')),
            ],
            options={
                'unique_together': {('group', 'advisor')},
            },
        ),
    ]