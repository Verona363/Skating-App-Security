from django.contrib import admin
from .models import Training, Profile, Registration
# Register your models here.
#we will register training model here
admin.site.register(Training)
#"Show the Training table in the admin interface."
admin.site.register(Profile)
admin.site.register(Registration)