from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('is_staff',)


class DogSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'name',
            'image',
            'breed',
            'age',
            'date_of_birth',
            'gender',
            'id',
            'intact_or_neutered',
            'size',
        )
        model = models.Dog

    def get_age(self, object):
        """Returns a string describing dog's age from its date of birth in
        the format 'X Year(s) Y Month(s)'. """
        age = ''
        date_of_birth = object.date_of_birth
        if date_of_birth:
            today = timezone.now().date()
            age_years = relativedelta(today, date_of_birth).years
            age_months = relativedelta(today, date_of_birth).months

            if age_years > 1:
                age += str(age_years) + " Years "
            elif age_years == 1:
                age += str(age_years) + " Year "

            if age_months > 1:
                age += str(age_months) + " Months"
            elif age_months == 1:
                age += str(age_months) + " Month"

            if age_years == 0 and age_months == 0:
                age = "Just born"

        return age

    def validate_date_of_birth(self, value):
        """Checks that date of birth is not in the future."""
        today = timezone.now().date()
        print(value, today)
        if value > today:
            raise serializers.ValidationError(
                'Date of birth cannot be in the future'
            )
        return value


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user',
            'age',
            'gender',
            'size',
        )
        extra_kwargs = {'user': {'write_only': True}}
        model = models.UserPref
