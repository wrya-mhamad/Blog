
from .views import RegisterView, LoginView
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('login/', LoginView.as_view({'post': 'create'}), name='login'),
    path('verify_user/', RegisterView.as_view({'post': 'verify_user'}), name='verify-user'),
]