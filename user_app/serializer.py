from django.contrib.auth.models import Group
from rest_framework import serializers
from groups.serializer import ReadGroupSerializer

from core.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


# change password for user by comparing old password with new password
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate(self, attrs):
        user = self.context['request'].user

        old_password = attrs.get('old_password')
        if user.check_password(old_password):

            return attrs
        else:
            raise serializers.ValidationError({'old_password': 'Wrong old password'})

    def create(self, validated_data):
        user = self.context['request'].user
        password = validated_data.get('new_password')
        user.set_password(password)
        user.save()
        return user


class CreateAdminSerializer(serializers.ModelSerializer):
    is_staff = serializers.HiddenField(default=True)
    is_verified = serializers.HiddenField(default=True)

    class Meta:
        model = User
        fields = ('email', 'username',  'password', 'is_staff', 'is_verified')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    groups = ReadGroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'groups')
