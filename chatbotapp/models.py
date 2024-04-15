# Inside chatbotapp/models.py

from django.db import models


class FAQ(models.Model):
    faq_id = models.AutoField(primary_key=True)
    faq_question = models.CharField(max_length=255)
    faq_answer = models.CharField(max_length=255, null=True)
    faq_tags = models.CharField(max_length=255, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    updation_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.faq_question


class UserQuery(models.Model):
    query_id = models.AutoField(primary_key=True)
    user_query = models.CharField(max_length=255)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    is_query_resolved = models.BooleanField(default=True)
    query_resolved_by = models.CharField(max_length=255, blank=True, null=True)
    response_given = models.CharField(max_length=255)
    time_taken_to_solve_query = models.DurationField()
    creation_time = models.DateTimeField(auto_now_add=True)
    updation_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_query


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, null=True)
    user_email = models.EmailField(unique=True, null=True)
    user_contact_number = models.CharField(max_length=20, null=True)
    user_type = models.CharField(max_length=255)  # registered user or guest user
    creation_time = models.DateTimeField(auto_now_add=True)
    updation_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_name
