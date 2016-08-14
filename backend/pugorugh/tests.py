from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from . import models
from . import serializers


class ModelTests(TestCase):
    def setUp(self):
        self.dog1 = models.Dog.objects.create(
            name="Benny",
            breed="Jack Chi",
            date_of_birth=timezone.datetime(2015, 3, 31).date(),
            gender='m',
            intact_or_neutered='n',
            size='s',
        )
        self.dog2 = models.Dog.objects.create(
            name="Nika",
            breed="Labrador",
            date_of_birth=timezone.datetime(2012, 7, 2).date(),
            gender='f',
            intact_or_neutered='i',
            size='l',
        )
        self.dog3 = models.Dog.objects.create(
            name="Coco",
            breed="Chihuahua",
            date_of_birth=timezone.datetime(2016, 4, 18).date(),
            gender='m',
            intact_or_neutered='n',
            size='s',
        )
        self.dog4 = models.Dog.objects.create(
            name="Daddy",
            breed="Pit Bull Terrier",
            date_of_birth=timezone.datetime(2010, 1, 22).date(),
            gender='m',
            intact_or_neutered='n',
            size='m',
        )
        self.dog5 = models.Dog.objects.create(
            name="Changa",
            breed="German Shepherd",
            date_of_birth=timezone.datetime(2011, 5, 18).date(),
            gender='f',
            intact_or_neutered='i',
            size='l',
        )
        self.dog6 = models.Dog.objects.create(
            name="Mini",
            breed="Newfoundland",
            date_of_birth=timezone.datetime(2013, 9, 16).date(),
            gender='f',
            intact_or_neutered='i',
            size='xl',
        )

        self.user1 = User.objects.create(
            username='user1',
            is_staff=False,
        )
        self.user1.set_password('password')
        self.user1.save()

        self.user2 = User.objects.create(
            username='user2',
            is_staff=False,
        )
        self.user2.set_password('password')
        self.user2.save()

        self.staff = User.objects.create(
            username='staff',
            is_staff=True,
        )
        self.staff.set_password('password')
        self.staff.save()

    def test_dogs_creation(self):
        self.assertEqual(models.Dog.objects.count(), 6)

    def test_user_pref_creation(self):
        user1_pref = models.UserPref.objects.get(user=self.user1)
        self.assertEqual(user1_pref.size, 's,m,l,xl')
        self.assertEqual(user1_pref.age, 'b,y,a,s')
        self.assertEqual(user1_pref.gender, 'm,f')


class SerializersTests(TestCase):
    def test_date_of_birth_to_age(self):
        today = timezone.now().date()
        td = timezone.timedelta(days=100)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, '3 Months')

        td = timezone.timedelta(days=10)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, 'Just born')

        td = timezone.timedelta(days=367)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, '1 Year')

        td = timezone.timedelta(days=397)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, '1 Year 1 Month')

        td = timezone.timedelta(days=734)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, '2 Years')

        td = timezone.timedelta(days=35)
        date_of_birth = today - td
        age = serializers.date_of_birth_to_age(date_of_birth)
        self.assertEqual(age, '1 Month')



class UserTests(APITestCase):
    def setUp(self):
        ModelTests.setUp(self)

    def test_register(self):
        url = reverse('register-user')
        data = {
            'username': 'vasilty',
            'password': 'password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_token(self):
        url = reverse('login-user')
        data = {
            'username': 'user1',
            'password': 'password'
        }
        response = self.client.post(url, data, format='json')
        token = Token.objects.get(user=self.user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'token': token.key})

    def test_is_staff(self):
        token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('user-is-staff')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'is_staff': False})

    def test_is_staff_unauthenticated(self):
        url = reverse('user-is-staff')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DogTests(APITestCase):
    def setUp(self):
        ModelTests.setUp(self)

        models.UserPref.objects.filter(user=self.user1).update(
            user=self.user1,
            age='b,y',
            gender='m',
            size='s',
        )

    def like_dislike_dogs(self):
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog1,
            status='l',
        )
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog3,
            status='l',
        )
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog5,
            status='d',
        )
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog6,
            status='d',
        )

    def authenticate(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token '+token.key)

    def test_create_dog_success(self):
        self.authenticate(user=self.staff)
        url = reverse('new-dog')
        data = {
            'name': 'Kiki',
            'gender': 'f',
            'intact_or_neutered': 'i',
            'size': 'm',
            'date_of_birth': timezone.datetime(2014, 9, 16).date(),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_dog_unauthenticated(self):
        url = reverse('new-dog')
        data = {
            'name': 'Kiki',
            'gender': 'f',
            'intact_or_neutered': 'i',
            'size': 'm',
            'date_of_birth': timezone.datetime(2014, 9, 16).date(),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_dog_unauthorized(self):
        self.authenticate(user=self.user2)
        url = reverse('new-dog')
        data = {
            'name': 'Kiki',
            'gender': 'f',
            'intact_or_neutered': 'i',
            'size': 'm',
            'date_of_birth': timezone.datetime(2014, 9, 16).date(),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_dog_unsuccess(self):
        today = timezone.now().date()
        self.authenticate(user=self.staff)
        url = reverse('new-dog')
        data = {
            'name': 'Kiki',
            'gender': 'f',
            'intact_or_neutered': 'i',
            'size': 'm',
            'date_of_birth': today + timezone.timedelta(days=10),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_dog_success(self):
        self.authenticate(user=self.staff)
        url = reverse('delete-dog', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Dog.objects.count(), 5)

    def test_destroy_dog_unauthenticated(self):
        url = reverse('delete-dog', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_dog_unauthorized(self):
        self.authenticate(user=self.user2)
        url = reverse('delete-dog', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_liked_dogs_first(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog1)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'liked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_liked_dogs_pk_1(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog3)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 1,
                'dog_filter': 'liked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_liked_dogs_last(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 3,
                'dog_filter': 'liked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), -1)

    def test_retrieve_liked_dogs_when_no_dogs(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user2)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'liked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_liked_dogs_unauthorized(self):
        self.like_dislike_dogs()
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'liked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_disliked_dogs_first(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog5)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'disliked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_disliked_dogs_pk_5(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog6)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 5,
                'dog_filter': 'disliked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_disliked_dogs_last(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user1)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 6,
                'dog_filter': 'disliked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), -1)

    def test_retrieve_disliked_dogs_when_no_dogs(self):
        self.like_dislike_dogs()
        self.authenticate(user=self.user2)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'disliked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_disliked_dogs_unauthenticated(self):
        self.like_dislike_dogs()
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'disliked'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_undecided_dogs_first(self):
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog1)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'undecided'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_undecided_dogs_pk_1(self):
        self.authenticate(user=self.user1)
        serializer = serializers.DogSerializer(self.dog3)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 1,
                'dog_filter': 'undecided'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_undecided_dogs_last(self):
        self.authenticate(user=self.user1)
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': 3,
                'dog_filter': 'undecided'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), -1)

    def test_retrieve_undecided_dogs_unauthenticated(self):
        self.like_dislike_dogs()
        url = reverse(
            'filtered-dog-detail',
            kwargs={
                'pk': -1,
                'dog_filter': 'undecided'
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_dog_status_undecided_to_liked(self):
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'liked'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
            status='l'
        ).count(), 1)

    def test_update_dog_status_undecided_to_disliked(self):
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'disliked'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
            status='d'
        ).count(), 1)

    def test_update_dog_status_undecided_to_undecided(self):
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'undecided'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
        ).count(), 0)

    def test_update_dog_status_liked_to_undecided(self):
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog1,
            status='l'
        )
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'undecided'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
        ).count(), 0)

    def test_update_dog_status_liked_to_disliked(self):
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog1,
            status='l'
        )
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'disliked'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
        ).count(), 1)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
            dog=self.dog1,
            status='d',
        ).count(), 1)

    def test_update_dog_status_disliked_to_liked(self):
        models.UserDog.objects.create(
            user=self.user1,
            dog=self.dog1,
            status='d'
        )
        self.authenticate(user=self.user1)
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'liked'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
        ).count(), 1)
        self.assertEqual(models.UserDog.objects.filter(
            user=self.user1,
            dog=self.dog1,
            status='l',
        ).count(), 1)

    def test_update_dog_status_unauthenticated(self):
        url = reverse(
            'update-dog-status',
            kwargs={
                'pk': 1,
                'dog_status': 'liked'
            })
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserPrefTests(APITestCase):
    def setUp(self):
        DogTests.setUp(self)

    def test_get_user_preferences(self):
        DogTests.authenticate(self, self.user1)
        url = reverse('update-user-preferences')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'age': 'b,y', 'gender': 'm', 'size': 's'})

    def test_get_user_preferences_unauthorized(self):
        url = reverse('update-user-preferences')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_preferences(self):
        DogTests.authenticate(self, self.user1)
        url = reverse('update-user-preferences')
        data = {
            'age': 's',
            'gender': 'm,f',
            'size': 'l'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'age': 's', 'gender': 'm,f', 'size': 'l'})
        userpref = models.UserPref.objects.get(user=self.user1)
        self.assertEqual(userpref.age, 's')
        self.assertEqual(userpref.gender, 'm,f')
        self.assertEqual(userpref.size, 'l')
        self.assertEqual(
            models.UserPref.objects.filter(user=self.user1).count(),
            1
        )