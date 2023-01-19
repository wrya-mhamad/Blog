from rest_framework.decorators import action

from .serializer import RegisterSerializer, LoginSerializer
from rest_framework.viewsets import ModelViewSet
from core.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import status
from django.core.mail import send_mail


class RegisterView(ModelViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # user.groups.add(1)
        send_mail(
            'Welcome to Blog',
            'Thank you for registering to our blog\n your verification code is: ' + user.verification_code,
            'wrya.mhamad33@gmail.com',
            ['kiriy18251@cnogs.com'],
            fail_silently=False,

        )
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_name='verify_user', url_path='verify-user',
            permission_classes=[IsAuthenticated])
    def verify_user(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)

        if user.is_verified:
            return Response({'message': 'User already verified'})

        if user.verification_code == request.data.get('verification_code'):
            user.is_verified = True
            user.save()
            return Response({'message': 'User verified successfully'})
        else:
            return Response({'message': 'Invalid verification code'}, status=400)


class LoginView(ModelViewSet):
    serializer_class = LoginSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access = AccessToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'email': user.email,
            })
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
