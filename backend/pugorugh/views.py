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
    bdays = []
    today = timezone.now().date()
    for age in age_list:
        if age == 'b':
            td_to = timezone.timedelta(days=1*365)
            from_to = (today-td_to, today)
            bdays.append(from_to)
        elif age == 'y':
            td_from = timezone.timedelta(days=1*365)
            td_to = timezone.timedelta(days=3*365)
            from_to = (today-td_to, today-td_from)
            bdays.append(from_to)
        elif age == 'a':
            td_from = timezone.timedelta(days=3*365)
            td_to = timezone.timedelta(days=8*365)
            from_to = (today - td_to, today - td_from)
            bdays.append(from_to)
        else:
            td_from = timezone.timedelta(days=8*365)
            td_to = timezone.timedelta(days=30*365)
            from_to = (today-td_to, today-td_from)
            bdays.append(from_to)

    query = reduce(
        operator.or_,
        (Q(date_of_birth__range=time_range) for time_range in bdays)
    )
    return query


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class IsStaff(APIView):
    def get(self, request):
        user = self.request.user
        serializer = serializers.StaffUserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateDog(generics.CreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class DestroyDog(generics.DestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
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


        if dog_filter == 'undecided':
            # Get ids of all dogs liked and disliked by the current user.
            decided_dogs_ids = models.Dog.objects.filter(
                userdog__user=user
            ).values_list('id', flat=True)

            # Get size, gender and age of dogs the current user prefers.
            (size, gender, age) = models.UserPref.objects.filter(
                user=user
            ).values_list('size','gender', 'age')[0]

            # Convert the preferred age into the age query.
            age_query = age_to_query(age)

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
                # Set dog_id to the lowest filtered dog id
                dog_id = filtered_dogs_ids[0]
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
                index = bisect(filtered_dogs_ids, pk)
                dog_id = filtered_dogs_ids[index]

            return get_object_or_404(
                self.get_queryset(),
                pk=dog_id,
            )

        # If there are no filtered dogs
        else:
            raise Http404


# class RetrieveFilteredDog(APIView):
#     def get(self, request, pk, dog_filter):
#         queryset = models.Dog.objects.all()
#         serializer_class = serializers.DogSerializer
#
#         user = self.request.user
#         pk = int(pk)
#         # dog_filter = self.kwargs.get('dog_filter')
#
#
#         if dog_filter == 'undecided':
#             # Get ids of all dogs liked and disliked by the current user.
#             decided_dogs_ids = models.Dog.objects.filter(
#                 userdog__user=user
#             ).values_list('id', flat=True)
#
#             # Get size, gender and age of dogs the current user prefers.
#             (size, gender, age) = models.UserPref.objects.filter(
#                 user=user
#             ).values_list('size','gender', 'age')[0]
#
#             # Convert the preferred age into the age query.
#             age_query = age_to_query(age)
#
#             # Get a list of ordered ids of all undecided dogs, which suit the
#             # current user.
#             filtered_dogs_ids = models.Dog.objects.exclude(
#                 id__in=decided_dogs_ids
#             ).filter(
#                 age_query,
#                 size__in=list(size),
#                 gender__in=gender,
#             ).order_by('id').values_list('id', flat=True)
#
#         elif dog_filter == 'liked':
#             # Get ids of all dogs liked by the current user.
#             filtered_dogs_ids = models.Dog.objects.filter(
#                 userdog__user=user,
#                 userdog__status='l'
#             ).order_by('id').values_list('id', flat=True)
#
#         else:
#             # Get ids of all dogs disliked by the current user.
#             filtered_dogs_ids = models.Dog.objects.filter(
#                 userdog__user=user,
#                 userdog__status='d'
#             ).order_by('id').values_list('id', flat=True)
#
#         # If there are filtered dogs
#         if filtered_dogs_ids:
#
#             # If pk is equal or greater than the highest filtered dog id
#             if pk >= filtered_dogs_ids[len(filtered_dogs_ids) - 1]:
#                 # Set dog_id to the lowest filtered dog id
#                 dog_id = filtered_dogs_ids[0]
#                 return Response(
#                     {"name": None, "image": None,
#                      "breed": None,
#                      "date_of_birth": None, "gender": None, "id": -1,
#                      "intact_or_neutered": None, "size": None},
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 index = bisect(filtered_dogs_ids, pk)
#                 dog_id = filtered_dogs_ids[index]
#
#             object = get_object_or_404(
#                 models.Dog,
#                 pk=dog_id,
#             )
#             serializer = serializer_class(object)
#
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         # If there are no filtered dogs
#         else:
#             raise Http404





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
