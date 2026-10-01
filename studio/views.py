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
    membership_active=False
    if request.user.is_authenticated:
        membership=Membership.objects.filter(
            client=request.user
            ).order_by("-purchased_at").first()

        if membership:
            membership_active=membership.valid_until>=timezone.localdate()

    return render(request, "studio/home.html", {"membership": membership, "membership_active": membership_active})
#"memebrship" is HTML variable
# membership backend variable


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
    search=request.GET.get ("search", "")
    #gets the value from a URL such as: /trainings/?search=adult
    trainings = Training.objects.filter(date__gte=timezone.now())
    #Django only sends trainings whose date/time is now or in the future to the template.
    #Even after hiding past trainings, someone could manually send:
    #POST /trainings/5/register/ for an old training
    if search:
        trainings = trainings.filter(title__icontains=search)
    
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
    return render(request, "studio/trainings.html", {"trainings": trainings, "registered_training_ids":registered_training_ids, "search": search})

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
    membership=Membership.objects.filter(client=request.user
            ).order_by("-purchased_at").first()
        #gets the most recently purchased membership
    today= timezone.localdate()
    if (membership is None 
            or membership.trainings_left==0
            or membership.valid_until<today):

            messages.warning(
                    request,
                    "You don't have any valid trainings left or your membership is not valid.")
            return redirect("studio:trainings")


        
    #we also need to add a feature for checking whther the training exists:
    try:
        training = Training.objects.get(id=training_id)
        if training.date.date() > membership.valid_until:
            messages.warning(
                    request,
                    "Your membership expires before the training you're trying to register for.")
            return redirect("studio:trainings")
        
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
def coach_cancel_registration(request, registration_id):

    if not request.user.is_staff:
        return redirect("studio:trainings")

    if request.method != "POST":
        return redirect("studio:trainings")

    try:
        registration = Registration.objects.get(id=registration_id)
        #next block does not allow to cancel registration through the trainings page to the past training
        if registration.training.date < timezone.now():
            
            messages.warning(
                request,
                "You cannot cancel a registration for a training that has already taken place.")
            
            return redirect("studio:training",training_id=registration.training.id)
        # end of block, can be deleted later if i change my mind 
        
        membership = Membership.objects.filter(
            client=registration.client,
            valid_until__gte=timezone.localdate()
        ).order_by("-purchased_at").first()

        training_id = registration.training.id
        #training_id = registration.training   variable would contain the Training object
            
        registration.delete()

        if membership:
            membership.trainings_left += 1
            membership.save()

        messages.success(
            request,
            "Client registration successfully canceled."
        )

    except Registration.DoesNotExist:
        messages.warning(
            request,
            "This registration does not exist."
        )
        return redirect("studio:trainings")


    return redirect(
        "studio:training",
        training_id=training_id
    )

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
                if request.user.profile.role == "CLIENT":
                        if registration.training.date < timezone.now():
                            messages.warning(request,
                                 "You cannot cancel a training that has already taken place.")
                            return redirect("studio:trainings")

            #if registration.client==request.user:#hence not needed
                registration.delete()
                messages.success(
                    request, "Reservation successfully canceled."
                )
                membership=Membership.objects.filter(client=request.user, valid_until__gte=timezone.localdate()).order_by("-purchased_at").first()
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

