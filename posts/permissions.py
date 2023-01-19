from rest_framework.permissions import BasePermission, DjangoModelPermissions


class IsAuthor(BasePermission):
    message = 'You are not the author of this post'

    def has_object_permission(self, request, view, obj):
        print(request.user)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.user == request.user
        return True


class IsVerified(BasePermission):
    message = 'You are not verified'

    def has_permission(self, request, view,):
        if request.method in ['PATCH', 'PUT', 'DELETE', 'POST']:
            if not request.user.is_anonymous:
                return request.user.is_verified
            return False
        return True


class CustomDjangoModelPermissions(DjangoModelPermissions):
    authenticated_users_only = False

