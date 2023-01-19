from django.contrib import admin
from core.models import Post, Tag
from core.models.likes import Like

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Like)
# Register your models here.
