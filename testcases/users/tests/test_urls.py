from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Color, Wallet

User = get_user_model()


class UsersUrlsTests(TestCase):
    """Тестирует Url-адреса приложения `users`."""

    @classmethod
    def setUpClass(cls):
        """Создает экземпляры пользователя, цвета и кошелька."""
        super().setUpClass()
        cls.color1 = Color.objects.create(
            hex_code='D8BFD8',
            cost=0,
        )
        cls.color2 = Color.objects.create(
            hex_code='D88888',
            cost=50,
        )
        cls.user = User.objects.create_user(username='tester')
        cls.wallet = Wallet.objects.create(
            owner=cls.user,
            total_won=1000,
            current_sum=1000,
        )
        cls.PAGES = {
            'SIGNUP_PAGE': {
                'url': reverse('users:signup'),
                'template': 'users/signup.html',
            },
            'LOGIN_PAGE': {
                'url': reverse('users:login'),
                'template': 'users/login.html',
            },
            'PASSWORD_CHANGE_PAGE': {
                'url': reverse('users:password_change'),
                'template': 'users/password_change_form.html',
            },
            'PASSWORD_CHANGE_DONE_PAGE': {
                'url': reverse('users:password_change_done'),
                'template': 'users/password_change_done.html',
            },
            'PASSWORD_RESET_PAGE': {
                'url': reverse('users:password_reset_done'),
                'template': 'users/password_reset_done.html',
            },
            'PASSWORD_RESET_DONE_PAGE': {
                'url': reverse('users:password_reset'),
                'template': 'users/password_reset_form.html',
            },
            'PASSWORD_RESET_TOKEN_PAGE': {
                'url': reverse(
                'users:password_reset_confirm', kwargs={
                    'uidb64': 'Mg',
                    'token': 'blmrls-a899327db3c505fd2e0766f76f340d13',
                }),
                'template': 'users/password_reset_confirm.html',
            },
            'PASSWORD_RESET_COMPLETE_PAGE': {
                'url': reverse('users:password_reset_complete'),
                'template': 'users/password_reset_complete.html',
            },
            'CURRENT_USER_PAGE': {
                'url': reverse('users:users-me'),
                'template': 'users/user_me.html',
            },
            'COLOR_CHANGE_PAGE': {
                'url': reverse(
                'users:user-color', kwargs={
                    'pk': cls.color2.id,
                }),
                'template': 'users/user_me.html',
            },
            'USERS_RESULTS_PAGE': {
                'url': reverse('users:users-list'),
                'template': 'users/user_list.html',
            },
            'LOGOUT_PAGE': {
                'url': reverse('users:logout'),
                'template': 'users/logged_out.html',
            },
        }

    @classmethod
    def tearDownClass(cls):
        """Прибирает за собой."""
        super().tearDownClass()
        cls.color1.delete()
        cls.color2.delete()
        cls.user.delete()
        cls.wallet.delete()

    def setUp(self):
        """Создает пользователей, чистит кэш."""
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages(self):
        """Проверяет доступ пользователей к страницам."""
        for title, page in self.PAGES.items():
            for test_user in (self.guest_client, self.authorized_client):
                with self.subTest(page=page):
                    status = HTTPStatus.OK
                    if test_user is self.guest_client and title in (
                        'PASSWORD_CHANGE_PAGE', 'PASSWORD_CHANGE_DONE_PAGE',
                        'CURRENT_USER_PAGE',
                    ) or title in ('COLOR_CHANGE_PAGE', 'LOGOUT_PAGE',):
                        status = HTTPStatus.FOUND
                    response = test_user.get(page['url'])
                    self.assertEqual(response.status_code, status)

    def test_redirects_urls(self):
        """Проверяет адреса редиректов пользователей."""
        for page in (
            self.PAGES['PASSWORD_CHANGE_PAGE']['url'],
            self.PAGES['PASSWORD_CHANGE_DONE_PAGE']['url'],
            self.PAGES['CURRENT_USER_PAGE']['url'],
            self.PAGES['COLOR_CHANGE_PAGE']['url'],
        ):
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertRedirects(response, f'/users/login/?next={page}')

        for page, address in (
            self.PAGES['COLOR_CHANGE_PAGE']['url'],
            self.PAGES['CURRENT_USER_PAGE']['url'],
        ),(
            self.PAGES['LOGOUT_PAGE']['url'],
            reverse('core:index'),
        ):
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertRedirects(response, address)

    def test_urls_uses_correct_template(self):
        """Проверяет использование верных шаблонов."""
        for title, page in self.PAGES.items():
            if title not in ('COLOR_CHANGE_PAGE', 'LOGOUT_PAGE'):
                with self.subTest(page=page):
                    response = self.authorized_client.get(page['url'])
                    self.assertTemplateUsed(response, page['template'])
