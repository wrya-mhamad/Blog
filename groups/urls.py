from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import GroupView
from django.conf.urls.static import static
from django.conf import settings

group_router = routers.DefaultRouter()
group_router.register(prefix='', viewset=GroupView, basename='groups')

urlpatterns = [
    path('', include(group_router.urls)),
    path('group_permission/<str:opt_type>/', GroupView.as_view({'post': 'group_permissions'}), name='group-permissions'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
