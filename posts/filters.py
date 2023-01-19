import django_filters as filters
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Post


class CustomDjangoFilterBackend(DjangoFilterBackend):

    def get_filterset(self, request, queryset, view):

        if request.user.is_authenticated:
            if request.user.is_staff:
                return AdminPostFilterSet(request.GET, queryset=queryset)
            return AuthorFilterSet(request.GET, queryset=queryset)
        return GuestPostFilterSet(request.GET, queryset=queryset)


class PostsFilterSet(filters.FilterSet):
    search = filters.CharFilter(method='search_post')

    @staticmethod
    def search_post(queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(body__icontains=value) | Q(tags__name__icontains=value)
        ).distinct()

    class Meta:
        model = Post
        fields = ['title', 'body', 'tags__name']


class AuthorFilterSet(PostsFilterSet):
    order_by = filters.CharFilter(method='order_by_posts')

    def order_by_posts(self, queryset, name, value):
        if value.startswith('-'):
            field_to_order = value[1:]
        else:
            field_to_order = value

        if getattr(self.Meta.model, field_to_order) is not None:
            return queryset.order_by(value)
        else:
            return queryset


class GuestPostFilterSet(PostsFilterSet):
    top_10 = filters.CharFilter(method='top_10_posts')
    author = filters.CharFilter(field_name='user__id', lookup_expr='exact')

    @staticmethod
    def top_10_posts(queryset, name, value):
        if value == 'likes':
            return queryset.annotate(likes_count=Count('likes')).order_by('-likes_count')[:10]
        elif value == 'comments':
            return queryset.annotate(comments_count=Count('comments')).order_by('-comments_count')[:10]


class AdminPostFilterSet(AuthorFilterSet):
    tag = filters.CharFilter(field_name='tags__name', lookup_expr='exact')
    author = filters.CharFilter(field_name='user__id', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='exact')
