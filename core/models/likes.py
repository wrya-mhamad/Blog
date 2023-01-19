from django.db import models
from .user import User


class Like(models.Model):
    user = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    post = models.ForeignKey('core.Post', related_name='likes', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} liked {self.post}'

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created']
