# Generated by Django 3.2.12 on 2022-05-07 08:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_group_member_examiner_advisor'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_name', models.CharField(max_length=200)),
                ('title_description', models.TextField()),
                ('no', models.IntegerField(choices=[(1, 'One'), (2, 'Two'), (3, 'Three')])),
                ('rejection_reason', models.CharField(default=None, max_length=1000)),
                ('status', models.CharField(choices=[('APPROVED', 'Approved'), ('PENDING', 'Pending'), ('REJECTED', 'Rejected')], max_length=10)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_titles', to='core.group')),
            ],
            options={
                'unique_together': {('group', 'no')},
            },
        ),
        migrations.AlterField(
            model_name='member',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='SubmissionType',
            fields=[
                ('name', models.CharField(max_length=200, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'submission_types',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='StudentEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=255, null=True)),
                ('mark', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('examiner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_evaluation', to='core.examiner')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_student', to='core.member')),
                ('submission_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_evaluation', to='core.submissiontype')),
            ],
            options={
                'db_table': 'student_evalaution',
            },
        ),
        migrations.CreateModel(
            name='TopProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('title_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.projecttitle')),
            ],
            options={
                'db_table': 'top_projects',
                'unique_together': {('title_name',)},
            },
        ),
        migrations.CreateModel(
            name='SubmissionDeadLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dead_line', models.DateTimeField(default=django.utils.timezone.now)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_deadline_batch', to='core.batch')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_type_deadline', to='core.submissiontype')),
            ],
            options={
                'db_table': 'submission_dead_lines',
                'unique_together': {('name', 'batch')},
            },
        ),
    ]