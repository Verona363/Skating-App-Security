from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name="studio"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name = "register"),
    #name = "register" gives this URL a name that we can use later in templates:
    #{% url "studio:register" %}
    path("login/", auth_views.LoginView.as_view(), name="login"),
]