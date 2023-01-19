from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import User
from groups.permissions import CustomDjangoModelPermissions
from .serializer import ProfileSerializer, ChangePasswordSerializer, UserSerializer, CreateAdminSerializer


class ProfileView(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_name='profile', url_path='profile', permission_classes=[IsAuthenticated])
    def get_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

    # change password for user by comparing old password with new password via serializer validate method
    @action(detail=False, methods=['post'], url_name='change-password', url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully'})


class UserView(ModelViewSet):
    queryset = User.objects.prefetch_related('groups')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        #user.groups.add(2)
        return Response( status=status.HTTP_201_CREATED, data=serializer.data)

    @action(detail=False, methods=['post'], url_name='user_role', url_path='user-role', permission_classes=[CustomDjangoModelPermissions])
    def user_role(self, request, *args, **kwargs):
        role_type = kwargs.get('role_type')
        if request.data.get('user_id') == request.user.id:
            return Response({'message': 'You cannot change your own role'})

        if role_type == 'assign':
            user = User.objects.get(id=request.data.get('user_id'))
            group = Group.objects.get(id=request.data.get('group_id'))
            user.groups.add(group)
            return Response({'message': 'Role assigned successfully'})
        elif role_type == 'revoke':
            user = User.objects.get(id=request.data.get('user_id'))
            group = Group.objects.get(id=request.data.get('group_id'))
            user.groups.remove(group)
            return Response({'message': 'Role revoked successfully'})



