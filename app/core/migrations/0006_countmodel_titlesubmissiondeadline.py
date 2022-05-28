# Generated by Django 4.0.4 on 2022-05-28 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_projecttitle_submissiontype_max_mark_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TitleSubmissionDeadline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deadline', models.DateTimeField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='title_submission_deadline_batch', to='core.batch')),
            ],
            options={
                'unique_together': {('batch', 'deadline')},
            },
        ),
    ]