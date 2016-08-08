from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Dog(models.Model):
    """Dog model class."""
    name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=255)
    breed = models.CharField(max_length=100, default="Pure Mutt")
    age = models.IntegerField()
    gender = models.CharField(
        max_length=1,
        choices=(
            ('m', 'Male'),
            ('f', 'Female'),
            ('u', 'Unknown'),
        ),
    )


class UserDog(models.Model):
    """User's Dog decision model class."""
    user = models.ForeignKey(User)
    dog = models.ForeignKey(Dog)
    status = models.CharField(
        max_length=1,
        choices=(
            ('l', 'Liked'),
            ('d', 'Disliked'),
        ),
    )


class UserPref(models.Model):
    """User Preference model class."""
    user = models.ForeignKey(User)
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
