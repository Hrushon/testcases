from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.forms import ModelChoiceField
from django.test import Client, TestCase
from django.urls import reverse

from users.models import Color, Wallet
from ..models import Answer, Attempt, Question, Test, TestingData, Theme

User = get_user_model()


class CoreViewTests(TestCase):
    """Тестирует view-функции приложения `core`."""

    @classmethod
    def setUpClass(cls):
        """Создает экземпляры пользователя, вопросов, ответов,
        тестов, пользовательских попыток, статистики и тем тестов.
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.wallet = Wallet.objects.create(
            owner=cls.user,
            total_won=0,
            current_sum=0,
        )
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
            'THEMES_LIST_PAGE': reverse('core:themes-list'),
            'THEMES_DETAIL_PAGE': reverse('core:themes-detail', kwargs={
                    'slug': cls.theme.slug,
                }),
            'TESTS_LIST_PAGE': reverse('core:tests-list'),
            'TESTS_DETAIL_PAGE': reverse('core:tests-detail', kwargs={
                    'pk': cls.test.id,
                }),
        }

    @classmethod
    def tearDownClass(cls):
        """Прибирает за собой."""
        super().tearDownClass()
        cls.user.delete()
        cls.theme.delete()
        cls.test.delete()
        cls.question.delete()
        cls.answer.delete()

    def setUp(self):
        """Создает пользователей."""
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_themes_list_page_show_correct_context(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        шаблону страницы со списком тем тестов.
        """
        response = self.authorized_client.get(
            self.PAGES['THEMES_LIST_PAGE']
        )
        object = response.context.get('object_list').first()

        self.assertEqual(object.title, self.theme.title)
        self.assertEqual(object.slug, self.theme.slug)
        self.assertEqual(object.tests.count(), self.theme.tests.count())

    def test_themes_detail_page_show_correct_context(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        шаблону страницы тестов конкретной темы и страницы списка тестов,
        отображаемой при поиске.
        """
        for page, object in (
            'THEMES_DETAIL_PAGE', 'object'
        ), (
            'TESTS_LIST_PAGE', 'object_list'
        ):
            with self.subTest(page=self.PAGES[page]):
                response = self.authorized_client.get(self.PAGES[page])
                object = response.context.get(object)

                if page == 'THEMES_DETAIL_PAGE':
                    self.assertEqual(object.title, self.theme.title)
                    test = object.tests.all().first()
                else:
                    test = object.first()

                self.assertEqual(test.title, self.test.title)
                self.assertEqual(
                    test.questions.count(), self.test.questions.count()
                )
                self.assertEqual(test.prize, self.test.prize)
                self.assertEqual(
                    test.percent_success, self.test.percent_success
                )

    def test_testdetail_page_show_correct_context(self):
        """Проверяет корректность возвращаемого view-функцией контекста
        шаблону страницы теста.
        """
        response = self.authorized_client.get(
            self.PAGES['TESTS_DETAIL_PAGE']
        )
        test = response.context.get('test')
        question = response.context.get('question')

        self.assertEqual(test.title, self.test.title)
        self.assertEqual(question.question_text, self.question.question_text)
   
        form_field = response.context.get('form').fields.get('answer')
        self.assertIsInstance(form_field, ModelChoiceField)

    def test_testdetail_get_request_correct_create_objects(self):
        """Проверяет, что при GET-запросе к странице прохождения теста
        создаются объекты `Попытки` и `Тестовых данных`.
        """
        self.assertFalse(Attempt.objects.all().exists())
        self.assertFalse(TestingData.objects.all().exists())

        response = self.authorized_client.get(
            self.PAGES['TESTS_DETAIL_PAGE']
        )

        self.assertTrue(Attempt.objects.all().exists())
        self.assertTrue(TestingData.objects.all().exists())

    def test_testdetail_post_request_correct_create_objects(self):
        """Проверяет, что при успешном прохождении теста
        изменяются соответствующие данные объектов `Пользовательского
        кошелька`, `Попытки` и `Тестовых данных` и возвращается
        соответствующий контекст.
        """
        total_coins = self.user.wallet.total_won
        current_coins = self.user.wallet.current_sum

        self.assertFalse(Attempt.objects.all().exists())
        self.assertFalse(TestingData.objects.all().exists())

        response = self.authorized_client.post(
            self.PAGES['TESTS_DETAIL_PAGE'],
            data={'answer': [str(self.answer.id)]},
            follow=True,
        )

        self.assertTrue(Attempt.objects.all().exists())
        self.assertTrue(TestingData.objects.all().exists())

        test = response.context.get('test')
        attempt = response.context.get('attempt')
        self.assertEqual(test.title, self.test.title)
        self.assertEqual(test.prize, self.test.prize)       
        self.assertEqual(attempt.result, 100)
        self.assertTrue(attempt.success)

        user_db = User.objects.get(id=self.user.id)
        self.assertEqual(
            user_db.wallet.total_won, total_coins + self.test.prize
        )
        self.assertEqual(
            user_db.wallet.current_sum, current_coins + self.test.prize
        )
