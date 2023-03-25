from django.db.models import Count, F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView

from users.models import Wallet
from .forms import TestingDataForm
from .models import Attempt, Test, TestingData, Theme


class ThemeListView(ListView):
    """Представление списка тем тестов."""

    queryset = Theme.objects.prefetch_related('tests')
    template_name = "core/themes_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Темы тестов'
        return context


class ThemeDetailView(DetailView):
    """Представление списка тестов конкретной темы."""

    queryset = Theme.objects.prefetch_related(
        'tests', 'tests__questions'
    )
    template_name = "core/test_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Тесты соответствующей тематики'
        return context


class TestListView(ListView):
    """
    Представление общего списка тестов.

    Используется при выдаче результатов теста по поисковому запросу.
    """

    queryset = Test.objects.select_related(
        'theme'
    ).prefetch_related('questions')
    template_name = "core/test_list.html"

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        if not search_query:
            return self.queryset.all()
        return self.queryset.filter(
            Q(title__iregex=search_query)
            | Q(theme__title__iregex=search_query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Реузльтаты поиска'
        return context


class TestDetailView(ListView, FormView):
    """Представление для проведения тестирования пользователя."""

    template_name = 'core/test_detail.html'
    context_object_name = 'question'
    form_class = TestingDataForm

    def get(self, request, *args, **kwargs):
        self.get_testing_data()
        return super(ListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_testing_data()
        self.object_list = self.get_queryset()

        form = self.form_class(
            self.request.POST or None,
            instance=self.testing_data,
        )
        if form.is_valid():
            form.save()

            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['test'] = self.test
        if self.testing_data:
            context['form'] = self.form_class(
                self.request.GET or None,
                initial={
                    'question': 0,
                    'attempt': 0,
                },
                instance=self.testing_data,
                field_queryset=context['question'].answers
            )
            return context
        context['attempt'] = self.attempt
        context['re_passing_test'] = self.re_passing_test
        return context

    def get_queryset(self):
        self.testing_data = self.attempt.testing_data.select_related(
            'question'
        ).filter(
            answer=None
        ).first()
        if not self.testing_data:
            return self.create_testing_result()
        return self.testing_data.question

    def get_testing_data(self):
        self.test = get_object_or_404(
            Test.objects.prefetch_related('questions'),
            pk=self.kwargs['pk'],
        )
        self.attempt, created = Attempt.objects.filter(
            result=None
        ).get_or_create(
            subject=self.request.user,
            testcase=self.test,
        )
        if created:
            TestingData.objects.bulk_create([
                TestingData(
                    attempt=self.attempt, question=obj
                ) for obj in self.test.questions.all()
            ])

    def create_testing_result(self):
        self.results = TestingData.objects.filter(
            attempt=self.attempt
        ).aggregate(
            count_corr_answers=Count('answer', filter=Q(answer__correct=True)),
            count_questions=Count('question'),
        )
        self.results['percent_corr_answers'] = (
            self.results['count_corr_answers']
            / self.results['count_questions']
            if self.results['count_questions'] else 0
        ) * 100
        return self.added_attempts_data()

    def added_attempts_data(self):
        self.re_passing_test = Attempt.objects.filter(
            subject=self.request.user,
            testcase=self.test,
            success=True,
        ).exists()
        self.attempt.result = self.results['percent_corr_answers']
        self.attempt.success = (
            True if self.test.percent_success <= self.attempt.result else False
        )
        self.attempt.save()
        if not self.re_passing_test and self.attempt.success:
            return self.get_coins_in_wallet()
        return self.attempt

    def get_coins_in_wallet(self):
        Wallet.objects.filter(owner=self.request.user).update(
            current_sum=F('current_sum') + self.test.prize,
            total_won=F('total_won') + self.test.prize,
        )
        return self.attempt

    def get_success_url(self):
        return reverse(
            'core:tests-detail', kwargs={'pk': self.kwargs['pk']}
        )
