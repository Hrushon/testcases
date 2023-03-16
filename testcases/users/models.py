from django.contrib.auth.models import AbstractUser
from django.db import models


class Color(models.Model):
    """Модель цвета для дифференциации пользователей."""

    hex_code = models.CharField(
        max_length=6,
        unique=True,
        verbose_name='hex-код цвета',
    )
    cost = models.PositiveSmallIntegerField()

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('cost',)
        verbose_name = 'цвет'
        verbose_name_plural = 'цвета'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.hex_code}'


class User(AbstractUser):
    """Кастомизация базовой модели пользователя."""

    color = models.ForeignKey(
        Color,
        related_name='users',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='цвет',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('-id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.username}'
