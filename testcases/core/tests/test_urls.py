from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from users.models import Color
from ..models import Answer, Question, Theme, Test

User = get_user_model()


class CoreUrlsTests(TestCase):
    """Тестирует Url-адреса приложения `core`."""

    @classmethod
    def setUpClass(cls):
        """Создает экземпляры пользователя, вопросов, ответов,
        тестов и тем тестов.
        """
        super().setUpClass()
        cls.color = Color.objects.create(
            hex_code='D8BFD8',
            cost=0,
        )
        cls.user = User.objects.create_user(username='tester')
        cls.theme = Theme.objects.create(
            title='История',
            slug='history',
        )
        cls.test = Test.objects.create(
            theme=cls.theme,
            title='Тестовая история',
            author=cls.user,
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
        cls.PAGES = {
            'MAIN_PAGE': {
                'url': reverse('core:index'),
                'template': 'core/index.html',
            },
            'THEMES_LIST_PAGE': {
                'url': reverse('core:themes-list'),
                'template': 'core/themes_list.html',
            },
            'THEMES_DETAIL_PAGE': {
                'url': reverse('core:themes-detail', kwargs={
                    'slug': cls.theme.slug,
                }),
                'template': 'core/test_list.html',
            },
            'TESTS_LIST_PAGE': {
                'url': reverse('core:tests-list'),
                'template': 'core/test_list.html',
            },
            'TESTS_DETAIL_PAGE': {
                'url': reverse('core:tests-detail', kwargs={
                    'pk': cls.test.id,
                }),
                'template': 'core/test_detail.html',
            },
            'TESTS_RESULT': {
                'url': reverse('core:tests-result', kwargs={
                    'pk': cls.test.id,
                }),
                'template': 'core/test_detail.html',
            },
            'UNEXISTING_PAGE': {
                'url': '/unexisting_page/',
                'template': 'errors/404.html',
            },
        }
    
    @classmethod
    def tearDownClass(cls):
        """Прибирает за собой."""
        super().tearDownClass()
        cls.color.delete()
        cls.user.delete()
        cls.theme.delete()
        cls.test.delete()
        cls.question.delete()
        cls.answer.delete()

    def setUp(self):
        """Создает пользователей."""
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
                        'TESTS_DETAIL_PAGE', 'TESTS_RESULT'
                    ):
                        status = HTTPStatus.FOUND
                    elif title == 'UNEXISTING_PAGE':
                        status = HTTPStatus.NOT_FOUND
                    response = test_user.get(page['url'])
                    self.assertEqual(response.status_code, status)

    def test_redirects_urls(self):
        """Проверяет адрес редиректов неавторизованного пользователя."""
        for page in (
            self.PAGES['TESTS_DETAIL_PAGE']['url'],
            self.PAGES['TESTS_RESULT']['url'],
        ):
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertRedirects(response, f'/users/login/?next={page}')

    def test_urls_uses_correct_template(self):
        """Проверяет использование верных шаблонов."""
        for page in self.PAGES.values():
            with self.subTest(page=page):
                response = self.authorized_client.get(page['url'])
                self.assertTemplateUsed(response, page['template'])
