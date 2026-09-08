from django.urls import path

from . import views

app_name="studio"

urlpatterns = [
    path("register/", views.register, name = "register"),
    #name = "register" gives this URL a name that we can use later in templates:
    #{% url "studio:register" %}
]