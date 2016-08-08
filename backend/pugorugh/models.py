from django.contrib.auth.models import User
from django.db import models


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
    """UserDog model class."""
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
    """User Pref model class."""
    user = models.ForeignKey(User)
    age = models.CharField(
        max_length=1,
        choices=(
            ('b', 'Baby'),
            ('y', 'Young'),
            ('a', 'Adult'),
            ('s', 'Senior'),
        ),
    )
    gender = models.CharField(
        max_length=1,
        choices=(
            ('m', 'Male'),
            ('f', 'Female'),
        ),
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
