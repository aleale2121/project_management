# Generated by Django 4.0.4 on 2022-05-29 06:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20220507_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='topproject',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='submissiontype',
            name='max_mark',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='topproject',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='top_projects_batch', to='core.batch'),
        ),
        migrations.AddField(
            model_name='topproject',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='topproject',
            name='doc_path',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='topproject',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='top_projects_group', to='core.group'),
        ),
        migrations.AddField(
            model_name='topproject',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='topproject',
            name='title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='top_projects_title', to='core.projecttitle'),
        ),
        migrations.AddField(
            model_name='topproject',
            name='vote',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='coordinator',
            unique_together={('user', 'batch')},
        ),
        migrations.AlterUniqueTogether(
            name='topproject',
            unique_together={('batch', 'title')},
        ),
        migrations.AlterModelTable(
            name='projecttitle',
            table='project_title',
        ),
        migrations.CreateModel(
            name='Semister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'db_table': 'semisters',
                'unique_together': {('name',)},
            },
        ),
        migrations.RemoveField(
            model_name='topproject',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='topproject',
            name='level',
        ),
        migrations.RemoveField(
            model_name='topproject',
            name='title_name',
        ),
        migrations.RemoveField(
            model_name='topproject',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='submissiontype',
            name='semister',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='semisters', to='core.semister'),
        ),
        # migrations.CreateModel(
        #     name='Voter',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.projecttitle')),
        #         ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voters', to=settings.AUTH_USER_MODEL)),
        #     ],
        #     options={
        #         'db_table': 'voters',
        #         'unique_together': {('user_id',)},
        #     },
        # ),
    ]
