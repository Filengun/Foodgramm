from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    '''Модель юзера'''
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'[\w.@+-]+$',
            message='Недопустимые символы'
        )],
        verbose_name='Никнейм'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'password',
        'username',
        'first_name',
        'last_name'
    ]

    @property
    def is_admin(self):
        """Администратор"""
        return self.role == 'admin' or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    '''Модель подписки'''
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_following'
            )
        ]

    def __str__(self) -> str:
        return f'{self.subscriber} подписан на: {self.author}'
