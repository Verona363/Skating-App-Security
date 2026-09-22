from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import ClientRegistrationForm
from .models import Profile, Training, Registration, Membership
from django.utils import timezone
def index(request):
    return HttpResponse("Hello, world.")

# Create your views here.
def home(request):
    membership=None
    if request.user.is_authenticated:
        membership=Membership.objects.filter(
            client=request.user
            ).order_by("-purchased_at").first()
        
    return render(request, "studio/home.html", {"membership": membership})
#"memebrship" is HTML variable
# memebership backend variable


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

            messages.success(
                request,
                "Your account has been created successfully. Please log in."
            )
            #add if messages to html template next

            return redirect("studio:login")

    else:
        form = ClientRegistrationForm()

    return render(request, "studio/register.html", {"form": form})

def trainings(request):
    trainings = Training.objects.all()
    registered_training_ids = set()
    if request.user.is_authenticated:
        registered_training_ids=set(
            Registration.objects.filter(client=request.user).values_list("training_id", flat=True)
        )
        #For a ForeignKey, Django automatically creates the database column by taking:
        # field name + _id
        #registration.training → Training object
        # registration.training_id if that training's primary key is 5.
        # givess values 1, 3 ex and set gives us {1, 3}
    return render(request, "studio/trainings.html", {"trainings": trainings, "registered_training_ids":registered_training_ids})

@login_required
def training(request, training_id):
    if request.user.profile.role =='COACH':
        training=get_object_or_404(Training, id=training_id)
        registrations=Registration.objects.filter(training=training)
        return render(request, "studio/training.html", {"training": training, "registrations": registrations} )
    else:
        return redirect("studio:trainings")





@login_required
def register_for_training(request, training_id):
    if request.method != "POST":
        return redirect("studio:trainings")
    elif request.method == "POST":
        membership=Membership.objects.filter(client=request.user
            ).order_by("-purchased_at").first()
        #gets the most recently purchased membership
        today= timezone.localdate()
        if (membership is None 
            or membership.trainings_left==0
            or membership.valid_until<today):

            messages.warning(
                    request,
                    "You don't have any valid trainings left or ypur membership is not valid.")
            return redirect("studio:trainings")


        
    #we also need to add a feature for checking whther the training exists:
        try:
            training = Training.objects.get(id=training_id)
            try:
                Registration.objects.create(
                    client=request.user,
                    #what if some other client replaces session.cookie and registers is it possible
                    training=training)
                messages.success(request, "You are registered for this training.")
                membership.trainings_left-=1
                membership.save()

            except IntegrityError:
                messages.warning(
                    request,
                    "You are already registered for this training.")
        except Training.DoesNotExist:
            messages.warning(request, 
                            "This training does not exist.")

        return redirect("studio:trainings")

@login_required
def cancel_registration(request, training_id):
    if request.method == "POST":
        try:
            Training.objects.get(id=training_id)
    #later can be removed for optimization
    #what if training doesnt exits, it should return some beautiful error
            try:
                registration=Registration.objects.get(training=training_id, client=request.user)
            #requiring the user to be the same as who owns the registration

            #if registration.client==request.user:#hence not needed
                registration.delete()
                messages.success(
                    request, "Reservation successfully canceled."
                )
                membership=Membership.objects.filter(client=request.user).order_by("-purchased_at").first()
                if membership:
                    membership.trainings_left+=1
                    membership.save()
                return redirect ("studio:trainings")
            except Registration.DoesNotExist:
                messages.warning(
                request, 
                "You haven't registered this training."
            )
        except Training.DoesNotExist:
            messages.warning(
                    request, 
                    "This training does not exist"
                    )
    return redirect("studio:trainings")

