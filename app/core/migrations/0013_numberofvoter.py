# Generated by Django 4.0.4 on 2022-06-21 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_chat_admin_remove_chat_owner_contact_admin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberOfVoter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staffs', models.IntegerField(default=0)),
                ('students', models.IntegerField(default=0)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='top_project_vote_statics', to='core.topproject')),
            ],
        ),
    ]