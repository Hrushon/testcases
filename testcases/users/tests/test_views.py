from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.core.cache import cache
from django.forms import CharField, EmailField, ImageField
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Answer, Attempt, Question, Test, Theme
from ..models import Color, Wallet

User = get_user_model()


class UsersViewTests(TestCase):
    """Тестирует view-функции приложения `users`."""

    @classmethod
    def setUpClass(cls):
        """Создает экземпляры пользователя, вопросов, ответов,
        тестов, пользовательских попыток, статистики и тем тестов.
        """
        super().setUpClass()
        cls.color2 = Color.objects.create(
            hex_code='FE8855',
            cost=100,
        )
        cls.user1 = User.objects.create_user(username='tester')
        cls.user2 = User.objects.create_user(username='einshtein')
        cls.wallet1 = Wallet.objects.create(
            owner=cls.user1,
            total_won=100,
            current_sum=100,
        )
        cls.wallet2 = Wallet.objects.create(
            owner=cls.user2,
            total_won=50,
            current_sum=50,
        )
        cls.theme = Theme.objects.create(
            title='История',
            slug='history',
        )
        cls.test = Test.objects.create(
            theme=cls.theme,
            title='Тестовая история',
            author=cls.user1,
            prize=100,
            percent_success=50,
        )
        cls.question = Question.objects.create(
            question_text='Исторический вопрос',
            test_base=cls.test,
        )
        cls.answer = Answer.objects.create(
            answer_text='Исторический ответ',
            question=cls.question,
            correct=True,
        )
        cls.attempt1 = Attempt.objects.create(
            subject=cls.user1,
            testcase=cls.test,
            success=False,
            result=20.00,
        )
        cls.attempt2 = Attempt.objects.create(
            subject=cls.user1,
            testcase=cls.test,
            success=True,
            result=100.00,
        )
        cls.attempt3 = Attempt.objects.create(
            subject=cls.user2,
            testcase=cls.test,
            success=True,
            result=100.00,
        )
        cls.PAGES = {
            'RESULTS_PAGE': reverse('users:users-list'),
            'USER_SELF_PAGE': reverse('users:users-me'),
            'USER_CHANGE_COLOR_PAGE': reverse('users:user-color', kwargs={
                'pk': cls.color2.id,
            }),
            'SIGNUP_PAGE': reverse('users:signup'),
        }

    @classmethod
    def tearDownClass(cls):
        """Прибирает за собой."""
        super().tearDownClass()
        cls.color2.delete()
        cls.user1.delete()
        cls.user2.delete()
        cls.wallet1.delete()
        cls.wallet2.delete()
        cls.theme.delete()
        cls.test.delete()
        cls.question.delete()
        cls.answer.delete()
        cls.attempt1.delete()
        cls.attempt2.delete()
        cls.attempt3.delete()

    def setUp(self):
        """Создает пользователей."""
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)

    def test_users_results_page_show_correct_context(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        шаблону страницы со списком резльтатов пользователей.
        """
        response = self.authorized_client.get(
            self.PAGES['RESULTS_PAGE']
        )
        object = response.context.get('object_list').first()

        self.assertEqual(object.photo, self.user1.photo)
        self.assertEqual(object.color, self.user1.color)
        self.assertEqual(object.tests_attempts, 2)
        self.assertEqual(object.tests_count, 1)
        self.assertEqual(object.tests_success, 1)
        self.assertEqual(object.wallet.total_won, self.user1.wallet.total_won)

        object = response.context.get('object_list')[1]

        self.assertEqual(object.photo, self.user2.photo)
        self.assertEqual(object.color, self.user2.color)
        self.assertEqual(object.tests_attempts, 1)
        self.assertEqual(object.tests_count, 1)
        self.assertEqual(object.tests_success, 1)
        self.assertEqual(object.wallet.total_won, self.user2.wallet.total_won)


    def test_users_self_page_show_correct_context(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        шаблону страницы личного кабинета пользователя.
        """
        response = self.authorized_client.get(
            self.PAGES['USER_SELF_PAGE']
        )
        object = response.context.get('object')
        color = response.context.get('color')

        for client, test_user in (
            self.authorized_client, self.user1
        ), (self.authorized_client_2, self.user2):
            with self.subTest(test_user=test_user):
                response = client.get(self.PAGES['USER_SELF_PAGE'])
                object = response.context.get('object')
                color = response.context.get('color')
                self.assertEqual(object.photo, test_user.photo)
                self.assertEqual(
                    object.wallet.total_won,
                    test_user.wallet.total_won,
                )
                self.assertEqual(
                    object.wallet.current_sum,
                    test_user.wallet.current_sum,
                )
                self.assertNotEqual(color, object.color)
                self.assertEqual(color, self.color2)
                self.assertEqual(color.cost, self.color2.cost)

    def test_users_change_color_correct(self):
        """Проверяет, что при POST-запросе происходит корректное изменение
        связанного с пользователем объекта цвета.
        """
        user_1 = User.objects.get(id=self.user1.id)
        user_color_1 = user_1.color
        user_sum_coins_1 = user_1.wallet.current_sum
        response = self.authorized_client.post(
            self.PAGES['USER_CHANGE_COLOR_PAGE'],
            follow=True,
        )
        user = User.objects.get(id=self.user1.id)

        self.assertNotEqual(user.color, user_color_1)
        self.assertEqual(user.color, self.color2)
        self.assertNotEqual(user.wallet.current_sum, user_sum_coins_1)
        self.assertEqual(
            user.wallet.current_sum, user_sum_coins_1 - user.color.cost
        )

        user_2 = User.objects.get(id=self.user2.id)
        user_sum_coins_2 = user_2.wallet.current_sum
        response = self.authorized_client_2.post(
            self.PAGES['USER_CHANGE_COLOR_PAGE'],
            follow=True,
        )
        user = User.objects.get(id=self.user2.id)

        self.assertNotEqual(user.color, self.color2)
        self.assertEqual(user.wallet.current_sum, user_sum_coins_2)

    def test_users_signup_page_show_correct_form(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        формы шаблону страницы регистрации пользователя.
        """
        form_fields = {
            'first_name': CharField,
            'last_name': CharField,
            'username': UsernameField,
            'email': EmailField,
            'photo': ImageField,
            'password1': CharField,
            'password2': CharField,
        }
        response = self.authorized_client.get(
            self.PAGES['SIGNUP_PAGE']
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form'
                ).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_users_signup_page_correct_create_objects(self):
        """Проверяет, что при POST-запросе создаются объекты моделей
        `Пользователь` и `Кошелек`.
        """
        users_count = User.objects.count()
        wallet_count = Wallet.objects.count()
        form_data = {
            'first_name': 'Вася',
            'last_name': 'Васечкин',
            'username': 'basilio',
            'email': 'vasya@kot.com',
            'password1': 'Wiskas2023',
            'password2': 'Wiskas2023',
        }
        response = self.guest_client.post(
            self.PAGES['SIGNUP_PAGE'],
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        users_count_1 = User.objects.count()
        wallet_count_1 = Wallet.objects.count()
        self.assertEqual(users_count_1, users_count + 1)
        self.assertEqual(wallet_count_1, wallet_count + 1)

        created_user = User.objects.get(username='basilio')
        created_wallet = created_user.wallet
        self.assertEqual(created_wallet.total_won, 0)
        self.assertEqual(created_wallet.current_sum, 0)


class PaginatorUsersViewsTest(TestCase):
    """Тестирует паджинатор view-функции приложения `users` для
    списка пользователей с их результатами.
    """

    @classmethod
    def setUpClass(cls):
        """Создание экземпляров Users."""
        super().setUpClass()
        cls.user = User.objects.create_user('tester')
        for i in range(23):
            User.objects.create_user(f'tester{i}')
        cls.PAGE = reverse('users:users-list')
        cls.FIRST_SECOND_PAGE = 10
        cls.THIRD_PAGE = 4

    def setUp(self):
        """Создание экземпляра клиента."""
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        """Прибирает за собой."""
        super().tearDownClass()
        cls.user.delete()

    def test_paginator(self):
        """Проверка контекста шаблона страниц."""
        response = self.authorized_client.get(self.PAGE)
        self.assertEqual(
            len(response.context['page_obj']), self.FIRST_SECOND_PAGE
        )
        response = self.authorized_client.get(self.PAGE + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), self.FIRST_SECOND_PAGE
        )
        response = self.authorized_client.get(self.PAGE + '?page=3')
        self.assertEqual(
            len(response.context['page_obj']), self.THIRD_PAGE
        )
