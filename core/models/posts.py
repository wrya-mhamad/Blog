from django.db import models

from .tags import Tag
from .user import User


def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to=upload_to, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='posts')

    class Meta:
        ordering = ['-id']
        permissions = [
            ('like_post', 'Can like post'),
            ('favorite_post', 'Can favorite post'),
        ]

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.image_url.delete()
        super().delete(*args, **kwargs)
