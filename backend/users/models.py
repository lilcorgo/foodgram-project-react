from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from .validators import username_validation


class User(AbstractUser):
    '''Стандартная модель пользователя.'''

    username = models.CharField(
        verbose_name='Ник пользователя',
        unique=True,
        max_length=150,
        validators=([username_validation]),
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='Электронная почта пользователя',
        null=False,
        unique=True,
        max_length=254,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Following(models.Model):
    '''Стандартная модель подписки.'''

    follower = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    to_follow = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        ordering = ('-follower',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['follower', 'to_follow'],
                name='unique_follow',
            )
        ]

    def __str__(self):
        return (f'{self.follower.username} подписался на '
                f'{self.to_follow.username}.')
