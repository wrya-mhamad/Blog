from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Post, Comment
from posts.permissions import IsAuthor, CustomDjangoModelPermissions, IsVerified
from posts.serializer import ReadCommentSerializer, WriteCommentSerializer, UpdateCommentSerializer
from posts.serializer import ReadPostSerializer, WritePostSerializer
from .filters import CustomDjangoFilterBackend
from rest_framework import filters


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related('user').prefetch_related('tags', 'likes', 'comments')
    filter_backends = [CustomDjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = (IsVerified, IsAuthor, CustomDjangoModelPermissions,)
    parser_classes = (MultiPartParser, FormParser)
    filter_fields = ['id', 'title', ]
    search_fields = ['title', 'body', 'tags__name']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadPostSerializer
        return WritePostSerializer

    # like specific post by user
    @action(detail=True, methods=['post'],
            url_name='like-post', url_path='like_post', permission_classes=[IsVerified, CustomDjangoModelPermissions])
    def like_post(self, request, pk=None):
        post = self.get_object()

        try:
            like = post.likes.get(user=request.user)
            like.delete()
            return Response({'message': 'Post disliked'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            post.likes.create(user=request.user)
            return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)

            # favorite specific post by user

    @action(detail=True, methods=['post'], url_name='favorite-post', url_path='favorite_post',
            permission_classes=[IsVerified, CustomDjangoModelPermissions])
    def favorite_post(self, request, pk=None):
        post = self.get_object()
        try:
            favorite = post.favorites.get(user=request.user)
            favorite.delete()
            return Response({'message': 'Post remove from favorite '}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            post.favorites.create(user=request.user)
            return Response({'message': 'Post add to favorite'}, status=status.HTTP_201_CREATED)


class CommentViewSet(ModelViewSet):
    permission_classes = [IsVerified, IsAuthor, DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        request.data['post'] = kwargs.get('pid')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCommentSerializer
        elif self.action in ('update', 'partial_update'):
            return UpdateCommentSerializer
        return WriteCommentSerializer

    def get_queryset(self):
        if self.action in ('update', 'partial_update', 'retrieve'):
            return Comment.objects.select_related('user')
        return Comment.objects.select_related('user').prefetch_related('replies').filter(reply_to=None)
