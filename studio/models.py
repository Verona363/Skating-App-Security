from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Training(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField (max_length=10,
                            choices=[("CLIENT", "Client"),
                            ("COACH", "Coach"),])
    #uppercase is stored in the database, normal will show in forms on the website
#later we will add choices for the role
    def __str__(self):
        return self.user.username

class Membership(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    #before it was  models.OneToOneField(User, on_delete=models.CASCADE)
    #hoewver the correct version is to use foreign key, because
    # one client can have severla memberships dut to renewal
    #connecting membership to the user
    trainings_left = models.PositiveIntegerField(default=8)
    #a new membership starts with 8 trainings
    purchased_at = models.DateField()
    valid_until = models.DateField()
    def __str__(self):
        return self.client.username

class Registration(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "training"],
                #combination client+training must be unique
                name="unique_client_training",
            )
        ]    