from bisect import bisect

from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from . import serializers


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class CreateDog(generics.CreateAPIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class RetrieveUpdateDog(generics.RetrieveUpdateAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get('pk'),
        )


class RetrieveFilteredDog(generics.RetrieveAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        user = self.request.user
        pk = int(self.kwargs.get('pk'))
        dog_filter = self.kwargs.get('dog_filter')
        print(filter)

        if dog_filter == 'undecided':
            # Get ids of all dogs liked and disliked by the current user.
            decided_dogs_ids = models.Dog.objects.filter(
                userdog__user=user
            ).values_list('id', flat=True)
            print(decided_dogs_ids)

            # Get a list of ordered ids of all dogs undecided by the current
            # user.
            filtered_dogs_ids = models.Dog.objects.exclude(
                id__in=decided_dogs_ids
            ).order_by('id').values_list('id', flat=True)
            print(filtered_dogs_ids)

        elif dog_filter == 'liked':
            # Get ids of all dogs liked by the current user.
            filtered_dogs_ids = models.Dog.objects.filter(
                userdog__user=user,
                userdog__status='l'
            ).order_by('id').values_list('id', flat=True)
            print(filtered_dogs_ids)

        else:
            # Get ids of all dogs disliked by the current user.
            filtered_dogs_ids = models.Dog.objects.filter(
                userdog__user=user,
                userdog__status='d'
            ).order_by('id').values_list('id', flat=True)
            print(filtered_dogs_ids)

        # If there are filtered dogs
        if filtered_dogs_ids:

            # If pk is equal or greater than the highest filtered dog id
            if pk >= filtered_dogs_ids[len(filtered_dogs_ids) - 1]:
                # Set dog_id to the lowest filtered dog id
                dog_id = filtered_dogs_ids[0]
            else:
                index = bisect(filtered_dogs_ids, pk)
                dog_id = filtered_dogs_ids[index]

            print(dog_id)

            return get_object_or_404(
                self.get_queryset(),
                pk=dog_id,
            )

        # If there are no filtered dogs
        else:
            raise Http404


class UpdateDogStatus(APIView):
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

    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(
            self.get_queryset(),
            user=user,
        )
