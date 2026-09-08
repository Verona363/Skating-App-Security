from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ClientRegistrationForm
from .models import Profile
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