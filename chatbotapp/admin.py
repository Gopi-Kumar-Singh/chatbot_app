from django.contrib import admin

# Register your models here.
from .models import FAQ, UserQuery, User

admin.site.register(FAQ)
admin.site.register(UserQuery)
admin.site.register(User)