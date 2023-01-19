from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Group
from core.models import User


class GroupTest(TestCase):
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

    def test_create_valid_group(self):
        response = self.client.post(
            reverse('groups-list'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            data={
                'name': 'test',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_create_invalid_group(self):
        response = self.client.post(
            reverse('groups-list'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            data={
                'name': '',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_group(self):
        response = self.client.get(
            reverse('groups-list'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_group_detail(self):
        response = self.client.get(
            reverse('groups-detail', kwargs={'pk': 1}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_update_group(self):
        response = self.client.put(
            reverse('groups-detail', kwargs={'pk': 1}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            data={
                'name': 'test',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_group(self):
        response = self.client.delete(
            reverse('groups-detail', kwargs={'pk': 1}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, 204)

    def test_assign_permissions(self):
        response = self.client.post(
            reverse('group-permissions', kwargs={'opt_type': 'assign'}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            data={
                'group': 1,
                'permissions': ['add_user', 'change_user', 'delete_user', 'view_user']
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_revoke_permissions(self):
        response = self.client.post(
            reverse('group-permissions', kwargs={'opt_type': 'revoke'}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            data={
                'group': 1,
                'permissions': ['add_user', 'change_user', 'delete_user', 'view_user']
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)

