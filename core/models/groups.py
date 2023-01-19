from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

class Group(Group):
    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        permissions = [
            ('group_permissions', 'Can assign or revoke permissions to a group'),
        ]
