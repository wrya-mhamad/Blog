from django.db import models
from django.contrib.auth.models import User
from .user import User


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey('core.Post', related_name='comments', on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    reply_to = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.user} commented on {self.post}'

    class Meta:
        ordering = ['-created']
