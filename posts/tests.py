import os

from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag, User, Group


class PostTestCase(TestCase):
    def setUp(self):
        authorPermissions = [
            "add_post",
            "change_post",
            "delete_post",
            "view_post",
            "add_comment",
            "change_comment",
            "delete_comment",
            "view_comment",
            "like_post",
        ]
        group = Group.objects.create(name='author')
        for permission in authorPermissions:
            group.permissions.add(Permission.objects.get(codename=permission))

        self.user = User.objects.create_verified_user(email='test@test.com', password='test', username='test')
        self.user.groups.add(group)
        self.post = Post.objects.create(title='test', body='test', user=self.user)
        self.tag = Tag.objects.create(name='test')
        self.post.tags.add(self.tag)
        self.client = APIClient()
        self.token = self.client.post(
            reverse('login'),
            data={'email': 'test@test.com', 'password': 'test'},
            format='json'
        ).data['access']
        self.client.force_authenticate(user=self.user)
        self.valid_payload = {
            'title': '<h1>test</h1>',
            'body': 'teswekjewnt',
            'tags[0]': 'test',
            'tags[1]': 'test2',
            'image_url': SimpleUploadedFile(os.path.join('C:\\Users\\wrya mohammed\\Desktop', 'ago.PNG'),
                                            open(os.path.join('C:\\Users\\wrya mohammed\\Desktop', 'ago.PNG'),
                                                 'rb').read(), content_type='image/png')
        }
        self.invalid_payload = {
            'title': '',
            'body': '',
            'tags': [],
            'image_url': ''
        }

    def test_create_valid_post(self):
        response = self.client.post(
            reverse('posts-list'),
            data=self.valid_payload,
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_post(self):
        response = self.client.post(
            reverse('posts-list'),
            data=self.invalid_payload,
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_valid_single_post(self):
        response = self.client.get(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post)

    def test_get_invalid_single_post(self):
        response = self.client.get(
            reverse('posts-detail', kwargs={'pk': 30}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_valid_multiple_post(self):
        response = self.client.get(
            reverse('posts-list'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post)

    def test_update_valid_post(self):
        response = self.client.put(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            data=self.valid_payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_post(self):
        response = self.client.put(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            data=self.invalid_payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_valid_post(self):
        response = self.client.delete(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json',
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_post(self):
        response = self.client.delete(
            reverse('posts-detail', kwargs={'pk': 30}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json',
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_get_post(self):
        client = APIClient()
        response = client.get(
            reverse('posts-list'),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_create_post(self):
        client = APIClient()
        response = client.post(
            reverse('posts-list'),
            data=self.valid_payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_update_post(self):
        client = APIClient()
        response = client.put(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            data=self.valid_payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_post(self):
        client = APIClient()
        response = client.delete(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            format='json',
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_get_single_post(self):
        client = APIClient()
        response = client.get(
            reverse('posts-detail', kwargs={'pk': self.post.pk}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_create_valid(self):
        response = self.client.post(
            reverse('comments-list', kwargs={'pid': self.post.id}),
            data={'body': 'test'},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_create_invalid(self):
        response = self.client.post(
            reverse('comments-list', kwargs={'pid': self.post.id}),
            data={'body': ''},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_get_valid(self):
        response = self.client.get(
            reverse('comments-list', kwargs={'pid': self.post.id}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_update_valid(self):
        self.test_comment_create_valid()
        response = self.client.put(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 1}),
            data={'body': 'test1', 'post': self.post.id},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_update_invalid(self):
        self.test_comment_create_valid()
        response = self.client.put(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 1}),
            data={'body': '', 'post': self.post.id},
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_delete_valid(self):
        self.test_comment_create_valid()
        response = self.client.delete(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 1}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_delete_invalid(self):
        self.test_comment_create_valid()
        response = self.client.delete(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 2}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_comment_create(self):
        client = APIClient()
        response = client.post(
            reverse('comments-list', kwargs={'pid': self.post.id}),
            data={'body': 'test'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_comment_update(self):
        self.test_comment_create_valid()
        client = APIClient()
        response = client.put(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 1}),
            data={'body': 'test1', 'post': self.post.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_comment_delete(self):
        self.test_comment_create_valid()
        client = APIClient()
        response = client.delete(
            reverse('comments-detail', kwargs={'pid': self.post.id, 'pk': 1}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_comment_get(self):
        client = APIClient()
        response = client.get(
            reverse('comments-list', kwargs={'pid': self.post.id}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_create_valid(self):
        response = self.client.post(
            reverse('posts-like-post', kwargs={'pk': self.post.id}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dislike_create_valid(self):
        self.test_like_create_valid()
        response = self.client.post(
            reverse('posts-like-post', kwargs={'pk': self.post.id}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_like_create(self):
        client = APIClient()
        response = client.post(
            reverse('posts-like-post', kwargs={'pk': self.post.id}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_dislike_create(self):
        client = APIClient()
        self.test_like_create_valid()
        response = client.post(
            reverse('posts-like-post', kwargs={'pk': self.post.id}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_post_valid(self):
        response = self.client.post(
            reverse('posts-favorite-post', kwargs={'pk': self.post.id}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unfavorite_post_valid(self):
        self.test_favorite_post_valid()
        response = self.client.post(
            reverse('posts-favorite-post', kwargs={'pk': self.post.id}),
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
