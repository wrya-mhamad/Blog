# Generated by Django 4.1.3 on 2022-12-12 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_favorite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-id'], 'permissions': [('like_post', 'Can like post'), ('favorite_post', 'Can favorite post')]},
        ),
    ]
