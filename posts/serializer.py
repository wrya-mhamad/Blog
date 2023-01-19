from rest_framework import serializers
from core.models import User
from core.models import Post, Tag, Like, Comment,Favorite
import os



class CurrentPostDefault(serializers.CurrentUserDefault):
    requires_context = True

    def __call__(self, serializer_field):
        post_id = int(serializer_field.context['request'].stream.path.split('/')[2])

        return Post.objects.get(id=post_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'created')

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'created')


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created']


class ReadCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = ReplySerializer(read_only=True, many=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'created', 'body', 'replies']


class WriteCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'created', 'body', 'reply_to']


class UpdateCommentSerializer(WriteCommentSerializer):
    replies = ReplySerializer(read_only=True, many=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'created', 'body', 'reply_to', 'replies']
        ordering = ['created']


class ReadPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    image_url = serializers.ImageField(required=False)
    comments = ReadCommentSerializer(many=True, read_only=True)
    favorite_by = FavoriteSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'user', 'image_url', 'comments', 'tags', 'likes', 'favorite_by']


class WritePostSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image_url = serializers.ImageField(required=False)
    tags = serializers.ListSerializer(
        child=serializers.CharField(max_length=40, min_length=2), min_length=0,
        write_only=False
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'user', 'tags', 'image_url']

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)

        for tag in tags:
            tag = Tag.objects.get_or_create(name=tag)[0]
            tag.save()
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        if instance.image_url != validated_data.get('image_url', instance.image_url) or instance.image_url is None:
            instance.image_url.delete()
            instance.image_url = validated_data.get('image_url', instance.image_url)

        instance.image_url = validated_data.get('image_url', instance.image_url)
        # clear existing tags
        instance.tags.clear()
        for tag in tags:
            tag = Tag.objects.get_or_create(name=tag)[0]
            tag.save()
            instance.tags.add(tag)
        instance.save()
        return instance

    def destroy(self, instance):
        os.remove(instance.image_url)
        instance.delete()

