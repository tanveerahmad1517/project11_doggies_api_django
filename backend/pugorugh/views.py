import operator

from bisect import bisect
from functools import reduce

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from . import serializers


def age_to_query(age_list):
    """From UserPref age attributes forms a query to filter dogs."""
    time_ranges = []
    today = timezone.now().date()
    for age in age_list:
        if age == 'b':
            td_start = timezone.timedelta(days=1*365)
            time_range = (today-td_start, today)
        elif age == 'y':
            td_end = timezone.timedelta(days=1*365)
            td_start = timezone.timedelta(days=3*365)
            time_range = (today-td_start, today-td_end)
        elif age == 'a':
            td_end = timezone.timedelta(days=3*365)
            td_start = timezone.timedelta(days=8*365)
            time_range = (today - td_start, today - td_end)
        else:
            td_end = timezone.timedelta(days=8*365)
            td_start = timezone.timedelta(days=30*365)
            time_range = (today-td_start, today-td_end)
        time_ranges.append(time_range)

    query = reduce(
        operator.or_,
        (Q(date_of_birth__range=time_range) for time_range in time_ranges)
    )
    return query


class UserRegisterView(generics.CreateAPIView):
    """View for user registration."""
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class IsStaff(generics.RetrieveAPIView):
    """View to get whether the current user is staff or not."""
    serializer_class = serializers.StaffUserSerializer

    def get_object(self):
        return self.request.user


class CreateDog(generics.CreateAPIView):
    """View to create a dog."""
    permission_classes = (permissions.IsAdminUser,)
    # parser_classes = (
        # parsers.MultiPartParser,
        # parsers.FormParser,
        # parsers.JSONParser,
        # )
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class DestroyDog(generics.DestroyAPIView):
    """View to delete a dog."""
    permission_classes = (permissions.IsAdminUser,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get('pk'),
        )


class RetrieveFilteredDog(generics.RetrieveAPIView):
    """View to get the next dog based on the user filter choice (undecided,
    liked or disliked).

    When all the dogs have been shown an imaginary Dog
    with the id of -1 is sent in a response to let user know that there are
    no more dogs left.

    Only those undecided dogs that match user preferences are shown.
    """
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        user = self.request.user
        pk = int(self.kwargs.get('pk'))
        dog_filter = self.kwargs.get('dog_filter')

        if dog_filter == 'undecided':
            # Get size, gender and age of dogs the current user prefers.
            (size, gender, age) = models.UserPref.objects.filter(
                user=user
            ).values_list('size','gender', 'age')[0]

            # Convert the preferred age into the age query.
            age_query = age_to_query(age)

            # Get ids of all dogs liked and disliked by the current user.
            decided_dogs_ids = models.Dog.objects.filter(
                userdog__user=user
            ).values_list('id', flat=True)

            # Get a list of ordered ids of all undecided dogs, which suit the
            # current user.
            filtered_dogs_ids = models.Dog.objects.exclude(
                id__in=decided_dogs_ids
            ).filter(
                age_query,
                size__in=list(size),
                gender__in=gender,
            ).order_by('id').values_list('id', flat=True)

        elif dog_filter == 'liked':
            # Get ids of all dogs liked by the current user.
            filtered_dogs_ids = models.Dog.objects.filter(
                userdog__user=user,
                userdog__status='l'
            ).order_by('id').values_list('id', flat=True)

        else:
            # Get ids of all dogs disliked by the current user.
            filtered_dogs_ids = models.Dog.objects.filter(
                userdog__user=user,
                userdog__status='d'
            ).order_by('id').values_list('id', flat=True)

        # If there are filtered dogs
        if filtered_dogs_ids:

            # If pk is equal or greater than the highest filtered dog id
            if pk >= filtered_dogs_ids[len(filtered_dogs_ids) - 1]:
                # Send an imaginary Dog with the id od -1
                return models.Dog(
                    name=None,
                    image=None,
                    breed=None,
                    date_of_birth=None,
                    gender=None,
                    id=-1,
                    intact_or_neutered=None,
                    size=None
                )
            else:
                # Get the id of the next dog
                index = bisect(filtered_dogs_ids, pk)
                dog_id = filtered_dogs_ids[index]

            return get_object_or_404(
                self.get_queryset(),
                pk=dog_id,
            )

        # If there are no filtered dogs
        else:
            raise Http404


class UpdateDogStatus(APIView):
    """View to update dog's status."""
    def put(self, request, pk, dog_status):

        user = request.user
        pk = int(pk)

        dog = get_object_or_404(models.Dog, pk=pk)

        if dog_status == 'liked':
            models.UserDog.objects.update_or_create(
                user=user,
                status='l',
                dog=dog,
            )
        elif dog_status == 'disliked':
            models.UserDog.objects.update_or_create(
                user=user,
                status='d',
                dog=dog,
            )
        else:
            models.UserDog.objects.filter(dog=dog, user=user).delete()

        serializer = serializers.DogSerializer(dog)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveUpdateUserPreferences(generics.RetrieveUpdateAPIView):
    """View to get and set user preferences."""
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(
            self.get_queryset(),
            user=user,
        )
