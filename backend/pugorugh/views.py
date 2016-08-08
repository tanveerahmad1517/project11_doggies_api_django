from bisect import bisect

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import generics

from . import models
from . import serializers


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class RetrieveDog(generics.RetrieveUpdateAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get('pk'),
        )


class RetrieveUndecidedDog(generics.RetrieveUpdateAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        user = self.request.user
        # Get ids of all dogs liked and disliked by the current user.
        decided_dogs_ids = models.Dog.objects.filter(
            userdog__user=user
        ).values_list('id', flat=True)
        print(decided_dogs_ids)

        # Get a list of ordered ids of all dogs undecided by the current user.
        undecided_dogs_ids = models.Dog.objects.exclude(
            id__in=decided_dogs_ids
        ).order_by('id').values_list('id', flat=True)
        print(undecided_dogs_ids)

        # If there are undecided dogs
        if undecided_dogs_ids:
            pk = int(self.kwargs.get('pk'))

            # If pk is equal or greater than the highest undecided dog id
            if pk >= undecided_dogs_ids[len(undecided_dogs_ids)-1]:
                # Set dog_id to the lowest undecided dog id
                dog_id = undecided_dogs_ids[0]
            else:
                index = bisect(undecided_dogs_ids, pk)
                dog_id = undecided_dogs_ids[index]

            print(dog_id)
            return get_object_or_404(
                self.get_queryset(),
                pk=dog_id,
            )
        # If there are no undecided dogs
        else:
            return models.Dog.objects.none()
