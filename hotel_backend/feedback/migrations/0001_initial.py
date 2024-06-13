# Generated by Django 5.0.3 on 2024-04-22 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_alter_accountant_photo_alter_accountant_resume_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.PositiveIntegerField()),
                ('text', models.TextField(blank=True, null=True)),
                ('date_time_created', models.DateTimeField(auto_now_add=True)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.guest')),
            ],
            options={
                'db_table': 'feedback',
            },
        ),
    ]
