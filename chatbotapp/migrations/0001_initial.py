# Generated by Django 4.2.11 on 2024-04-15 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('faq_id', models.AutoField(primary_key=True, serialize=False)),
                ('faq_question', models.TextField()),
                ('faq_answer', models.TextField()),
                ('faq_tags', models.CharField(max_length=255)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('updation_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=255)),
                ('user_email', models.EmailField(max_length=254, unique=True)),
                ('user_contact_number', models.CharField(max_length=20)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('updation_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserQuery',
            fields=[
                ('query_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_query', models.TextField()),
                ('is_query_resolved', models.BooleanField(default=False)),
                ('query_resolved_by', models.CharField(blank=True, max_length=255, null=True)),
                ('response_given', models.TextField(blank=True, null=True)),
                ('time_taken_to_solve_query', models.DurationField()),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('updation_time', models.DateTimeField(auto_now=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbotapp.user')),
            ],
        ),
    ]
