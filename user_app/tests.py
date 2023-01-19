from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from core.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Group


class UserTestCase(TestCase):
    def setUp(self):
        group = Group.objects.create(name='admin')
        admin_permissions = [
            'add_user',
            'change_user',
            'delete_user',
            'view_user',
            'add_group',
            'change_group',
            'delete_group',
            'view_group',
            'group_permissions',
        ]
        for permission in admin_permissions:
            group.permissions.add(Permission.objects.filter(codename=permission).first())

        self.user = User.objects.create_admin(email='admin@blog.com', password='admin', username='admin')

        self.user.groups.add(group)
        self.client = APIClient()
        self.token = self.client.post(
            reverse('login'),
            data={'email': 'admin@blog.com', 'password': 'admin'},
            format='json'
        ).data['access']

    def test_view_profile (self):
        response = self.client.get(
            reverse('profile'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_profile (self):
        response = self.client.patch(
            reverse('profile'),
            data={'username': 'new_username', 'email': 'admin@blog.com', 'first_name': 'new_first_name', 'last_name': 'new_last_name'},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password (self):
        response = self.client.post(
            reverse('change-password'),
            data={'old_password': 'admin', 'new_password': 'new_password'},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users (self):
        response = self.client.get(
            reverse('users'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user (self):
        response = self.client.patch(
            reverse('user', kwargs={'pk': self.user.pk}),
            data={'username': 'new_username', 'email': 'a@b.com', 'first_name': 'new_first_name', 'last_name': 'new_last_name'},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_admin (self):
        response = self.client.post(
            reverse('create-admin'),
            data={'username': 'new_admin', 'email': 'test@gmail.com', 'password': 'test'},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_assign_user_role(self):
        response = self.client.post(
            reverse('user-role', kwargs={'role_type': 'assign'}),
            data={'user_id': self.user.pk, 'role_id': 1},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_revoke_user_role(self):
        response = self.client.post(
            reverse('user-role', kwargs={'role_type': 'revoke'}),
            data={'user_id': self.user.pk, 'role_id': 1},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
