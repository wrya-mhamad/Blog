from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import User
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.valid_user_regiter_data = {
            'username': 'test1',
            'email': 'test1@test.com',
            'password': 'test',
        }

        self.invalid_user_regiter_data = {
            'username': 'test1',
            'email': '',
            'password': 'test',
        }

    def test_valid_register(self):
        response = self.client.post(
            reverse('register'),
            self.valid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_register(self):
        response = self.client.post(
            reverse('register'),
            self.invalid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_login(self):
        self.test_valid_register()
        response = self.client.post(
            reverse('login'),
            self.valid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        self.test_valid_register()
        response = self.client.post(
            reverse('login'),
            self.invalid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_verify_user(self):
        self.test_valid_register()
        user = User.objects.get(username=self.valid_user_regiter_data['username'])
        response = self.client.post(
            reverse('login'),
            self.valid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        res = self.client.post(
            reverse('verify-user'),
            HTTP_AUTHORIZATION='Bearer ' + token,
            type='json',
            data={'verification_code': user.verification_code},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_verify_user(self):
        self.test_valid_register()
        user = User.objects.get(username=self.valid_user_regiter_data['username'])
        response = self.client.post(
            reverse('login'),
            self.valid_user_regiter_data,
            type='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        res = self.client.post(
            reverse('verify-user'),
            HTTP_AUTHORIZATION='Bearer ' + token,
            type='json',
            data={'verification_code': '1234'},
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)