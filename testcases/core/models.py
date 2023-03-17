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
    subjects = models.ManyToManyField(
        User,
        through='UserTest',
        verbose_name='испытуемые',
    )
    prize = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.MIN_PRIZE),
            MaxValueValidator(settings.MAX_PRIZE),
        ],
        verbose_name='награда',
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


class UserTest(models.Model):
    """Промежуточная модель для связывания пользователей и тестов."""

    subject = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    testcase = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name='тест',
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='время начала прохождения теста',
    )
    finish_time = models.DateTimeField(
        verbose_name='время окончания прохождения теста',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('testcase',)
        verbose_name = 'пользователь + тест'
        verbose_name_plural = 'пользователи + тесты'

        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'testcase'],
                name='unique_user_test',
            )
        ]

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.subject} + {self.testcase}'


class Answer(models.Model):
    """Модель ответа."""

    body_text = models.CharField(
        max_length=512,
        unique=True,
        verbose_name='текст ответа',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('body_text',)
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.body_text}'


class Question(models.Model):
    """Модель вопроса."""

    body_text = models.CharField(
        max_length=512,
        unique=True,
        verbose_name='текст вопроса',
    )
    test_base = models.ForeignKey(
        Test,
        related_name='questions',
        on_delete=models.CASCADE,
        verbose_name='тесты',
    )
    answers = models.ManyToManyField(
        Answer,
        through='QuestionAnswer',
        verbose_name='ответы',
    )
    one_correct_answer = models.BooleanField(
        default=True,
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('body_text',)
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.body_text} ({self.test_base})'


class QuestionAnswer(models.Model):
    """Модель для связывания вопросов и ответов."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='вопрос',
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        verbose_name='ответ',
    )
    correct = models.BooleanField()

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('question',)
        verbose_name = 'вопрос + ответ'
        verbose_name_plural = 'вопросы + ответы'

        constraints = [
            models.UniqueConstraint(
                fields=['question', 'answer'],
                name='unique_question_answer',
            )
        ]

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.question} + {self.answer}'


class UserQuestionAnswer(models.Model):
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
    )
    subject = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    date_answering = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата ответа пользователя на вопрос',
    )

    class Meta:
        """
        Сортирует и добавляет названия в админке.
        """
        ordering = ('subject',)
        verbose_name = 'вопрос + пользователь'
        verbose_name_plural = 'вопросы + пользователи'

        constraints = [
            models.UniqueConstraint(
                fields=['question', 'answer', 'subject'],
                name='unique_question_subject',
            )
        ]

    def __str__(self):
        """
        Добавляет удобочитаемый вывод при вызове экземпляра объекта
        на печать.
        """
        return f'{self.subject} + {self.question}'


class Wallet(models.Model):
    """Кошелек с наградами пользователя."""

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
