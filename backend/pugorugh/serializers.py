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
        extra_kwargs = {'user': {'write_only': True}}


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'image',
            'breed',
            # 'age',
            'date_of_birth',
            'gender',
            'id',
            'intact_or_neutered',
            'size',
        )
        model = models.Dog


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
