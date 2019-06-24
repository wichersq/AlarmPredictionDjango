from django.contrib import admin
from .models import User as app_model

admin.site.register(app_model)