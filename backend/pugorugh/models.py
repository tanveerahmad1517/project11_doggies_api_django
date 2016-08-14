from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Dog(models.Model):
    """Dog model class."""
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='dogs/', blank=True, null=True)
    breed = models.CharField(max_length=100, default="Unknown mix")
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=(
            ('m', 'Male'),
            ('f', 'Female'),
        ),
    )
    intact_or_neutered = models.CharField(
        max_length=1,
        choices=(
            ('i', 'Intact'),
            ('n', 'Neutered'),
        ),
        default='i',
    )
    size = models.CharField(
        max_length=2,
        choices=(
            ('s', 'Small'),
            ('m', 'Medium'),
            ('l', 'Large'),
            ('xl', 'Extra Large'),
        ),
    )


class UserDog(models.Model):
    """User's Dog decision model class."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=(
            ('l', 'Liked'),
            ('d', 'Disliked'),
        ),
    )

    class Meta:
        unique_together = ('user', 'dog')


class UserPref(models.Model):
    """User Preference model class."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.CharField(
        max_length=7,
        default='b,y,a,s'
    )
    gender = models.CharField(
        max_length=3,
        default='m,f'
    )
    size = models.CharField(
        max_length=8,
        default='s,m,l,xl'
    )


def create_userpref(sender, **kwargs):
    """Create UserPref instance whenever User is created."""
    user = kwargs["instance"]
    if kwargs["created"]:
        user_pref = UserPref(user=user)
        user_pref.save()

post_save.connect(create_userpref, sender=User)
