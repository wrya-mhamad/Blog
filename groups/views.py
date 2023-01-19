from django.contrib.auth.models import Permission
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.contrib.auth.models import Group
from groups.permissions import CustomDjangoModelPermissions

from groups.serializer import CreateGroupSerializer, ReadGroupSerializer


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = CreateGroupSerializer
    permission_classes = [CustomDjangoModelPermissions]

    def get_serializer_class(self):
        if self.action == 'list' and self.action == 'retrieve':
            return ReadGroupSerializer
        return CreateGroupSerializer

    @action(methods=['post'], detail=False, url_path='group_permissions', url_name='group-permissions', permission_classes=[CustomDjangoModelPermissions])
    # check if type is assign or revoke then assign or revoke permissions
    def group_permissions(self, request, *args, **kwargs):
        opt_type = kwargs.get('opt_type')
        if opt_type == 'assign':
            group = Group.objects.get(pk=request.data.get('group'))
            for permission in request.data.get('permissions'):
                permission = Permission.objects.filter(codename=permission).first()
                group.permissions.add(permission)
            return Response({'message': 'Permissions assigned successfully'})
        elif opt_type == 'revoke':
            group = Group.objects.get(pk=request.data.get('group'))
            for permission in request.data.get('permissions'):
                permission = Permission.objects.filter(codename=permission).first()
                group.permissions.remove(permission)
            return Response({'message': 'Permissions revoked successfully'})
