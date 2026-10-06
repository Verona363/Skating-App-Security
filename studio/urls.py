from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView
from . import views
from .views import login_view

app_name="studio"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name = "register"),
    #name = "register" gives this URL a name that we can use later in templates:
    #{% url "studio:register" %}
    path("login/", login_view, name="login"), 
    path("trainings/", views.trainings, name="trainings"),
    path(
    "trainings/<int:training_id>/register/",
    views.register_for_training,
    name="register_for_training",
),
    path("training/<int:training_id>/", views.training, name="training"),
    path("training/<int:training_id>/cancel_registration/", views.cancel_registration, name="cancel_registration"),
    path("training/<int:registration_id>/coach_cancel_registration/", views.coach_cancel_registration, name="coach_cancel_registration"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/",PasswordChangeView.as_view(template_name="registration/password_change.html",success_url="/"), 
         name="change_password")

]