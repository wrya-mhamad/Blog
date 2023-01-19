from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from posts.views import PostViewSet, CommentViewSet
from django.conf.urls.static import static
from django.conf import settings

# create a default router and register post viewsets
post_router = routers.DefaultRouter()
post_router.register(prefix='posts', viewset=PostViewSet, basename='posts')

comment_router = routers.DefaultRouter()
comment_router.register(prefix='comments', viewset=CommentViewSet, basename='comments')

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include(post_router.urls)),
                  path('posts/<int:pid>/', include(comment_router.urls)),
                  path('', include('authentication.urls')),
                  path('users/', include('user_app.urls')),
                  path('groups/', include('groups.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
