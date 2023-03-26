from django.contrib.auth.models import AbstractUser
from django.db import models


class Color(models.Model):
    """Модель цвета для дифференциации пользователей."""

    hex_code = models.CharField(
        max_length=6,
        unique=True,
        verbose_name='hex-код цвета',
    )
    cost = models.PositiveSmallIntegerField(
        verbose_name='стоимость',
    )

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

    @classmethod
    def get_default_pk(cls):
        exam, created = cls.objects.get_or_create(
            hex_code='D8BFD8',
            cost=0,
        )
        return exam.pk


class User(AbstractUser):
    """Кастомизация базовой модели пользователя."""

    first_name = models.CharField(
        max_length=150,
        verbose_name='имя',
        help_text='Введите свое имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия',
        help_text='Введите свою фамилию',
    )
    photo = models.ImageField(
        upload_to='users_photos',
        default='user_avatar/default_user.jpg',
        verbose_name='фото пользователя',
        help_text='Добавьте к профилю свою фотографию',
    )
    color = models.ForeignKey(
        Color,
        related_name='users',
        on_delete=models.SET_NULL,
        default=Color.get_default_pk,
        null=True,
        blank=True,
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


class Wallet(models.Model):
    """Кошелек с наградными монетами пользователя."""

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец',
    )
    total_won = models.PositiveSmallIntegerField(
        verbose_name='получено монет за все время',
        default=0,
    )
    current_sum = models.PositiveSmallIntegerField(
        verbose_name='текущая сумма монет',
        default=0,
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('owner',)
        verbose_name = 'кошелек'
        verbose_name_plural = 'кошельки'

        constraints = [
            models.CheckConstraint(
                check=models.Q(current_sum__lte=models.F('total_won')),
                name='check_current_sum',
            )
        ]

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.owner} + {self.current_sum}'
