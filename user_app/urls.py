from django.urls import path

from .views import ProfileView, UserView

urlpatterns = [
    path('profile/', ProfileView.as_view({'get': 'get_profile', 'patch': 'update'}), name='profile'),
    path('change_password/', ProfileView.as_view({'post': 'change_password'}), name='change-password'),
    path('', UserView.as_view({'get': 'list'}), name='users'),
    path('<int:pk>/', UserView.as_view({'patch': 'update'}), name='user'),
    path('create_admin/', UserView.as_view({'post': 'create'}), name='create-admin'),
    path('user_role/<str:role_type>/', UserView.as_view({'post': 'user_role'}), name='user-role'),

]
