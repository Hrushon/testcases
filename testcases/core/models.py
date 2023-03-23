from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Theme(models.Model):
    """Модель для тематики тестов."""

    title = models.CharField(
        unique=True,
        max_length=256,
        verbose_name='название',
    )
    slug = models.SlugField(
        verbose_name='слаг/аббревиатура темы',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('title',)
        verbose_name = 'тематика теста'
        verbose_name_plural = 'тематики тестов'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.title}'


class Test(models.Model):
    """Модель теста."""

    title = models.CharField(
        unique=True,
        max_length=512,
        verbose_name='название',
    )
    theme = models.ForeignKey(
        Theme,
        related_name='tests',
        verbose_name='тема',
        on_delete=models.SET_NULL,
        null=True,
    )
    date_creation = models.DateField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    author = models.ForeignKey(
        User,
        related_name='tests',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='автор теста',
    )
    prize = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.MIN_PRIZE),
            MaxValueValidator(settings.MAX_PRIZE),
        ],
        verbose_name='награда',
    )
    percent_success = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(settings.MAX_PERCENT_SUCCESS),
        ],
        verbose_name='процент правильных ответов для прохождения',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('-date_creation',)
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.title} ({self.theme})'


class UsersAttempt(models.Model):
    """Промежуточная модель для связывания пользователей и тестов."""

    subject = models.ForeignKey(
        User,
        related_name='attempts',
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    testcase = models.ForeignKey(
        Test,
        related_name='users_attempts',
        on_delete=models.CASCADE,
        verbose_name='тест',
    )
    date_test = models.DateField(
        auto_now_add=True,
        verbose_name='дата прохождения пользователем теста',
    )
    success = models.BooleanField(
        auto_created=True,
        default=False,
        verbose_name='результат выполнения теста (сдал/не сдал)',
    )
    result = models.DecimalField(
        null=True,
        max_digits=5,
        decimal_places=2,
        verbose_name='процент правильных ответов',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('subject',)
        verbose_name = 'пользователь + тест'
        verbose_name_plural = 'пользователи + тесты'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.subject} + {self.testcase}'


class Question(models.Model):
    """Модель вопроса."""

    question_text = models.CharField(
        max_length=512,
        unique=True,
        verbose_name='текст вопроса',
    )
    test_base = models.ForeignKey(
        Test,
        related_name='questions',
        on_delete=models.CASCADE,
        verbose_name='тест',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('question_text',)
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.question_text} ({self.test_base})'


class Answer(models.Model):
    """Модель ответа."""

    answer_text = models.CharField(
        max_length=512,
        unique=True,
        verbose_name='текст ответа',
    )
    question = models.ForeignKey(
        Question,
        related_name='answers',
        on_delete=models.CASCADE,
        verbose_name='вопрос',
    )
    correct = models.BooleanField(
        verbose_name='правильныйответ',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('?',)
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.answer_text}'


class TestingData(models.Model):
    """Модель для связывания вопроса и ответа пользователя."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='вопрос',
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        verbose_name='ответ',
        blank=True,
        null=True,
    )
    attempt = models.ForeignKey(
        UsersAttempt,
        related_name='testing_data',
        on_delete=models.CASCADE,
        verbose_name='попытка',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('attempt',)
        verbose_name = 'вопрос + ответ пользователя'
        verbose_name_plural = 'вопросы + ответы пользователей'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.attempt} + {self.question}'
