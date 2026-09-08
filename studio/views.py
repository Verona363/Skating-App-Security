from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ClientRegistrationForm
from .models import Profile, Training, Registration
def index(request):
    return HttpResponse("Hello, world.")

# Create your views here.
def home(request):
    return render(request, "studio/home.html")


def register(request):

    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        #request.POST takes the submitted data
        #and gives it to the form

        if form.is_valid():
            user = form.save()
            # Django creates the actual user
            #we have username/email/password
            Profile.objects.create(
                user=user,
                role="CLIENT"
            )

            return redirect("login")

    else:
        form = ClientRegistrationForm()

    return render(request, "studio/register.html", {"form": form})

def trainings(request):
    trainings = Training.objects.all()
    return render(request, "studio/trainings.html", {"trainings": trainings})




@login_required
def register_for_training(request, training_id):
    training = Training.objects.get(id=training_id)
    try:
        Registration.objects.create(
            client=request.user,
            training=training
        )
        messages.success(request, "You are registered for this training.")

    except IntegrityError:
        messages.warning(
            request,
            "You are already registered for this training."
        )
    return redirect("studio:trainings")