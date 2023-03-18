from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Theme, Test, Question


class ThemeListView(ListView):
    """Представление списка тем тестов."""

    model = Theme
    template_name="core/themes_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Темы тестов'
        return context


class ThemeDetailView(DetailView):
    """Представление списка тестов конкретной темы."""

    model = Theme
    template_name="core/test_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Тесты соответствующей тематики'
        return context


class TestListView(ListView):
    """
    Представление общего списка тестов.
    
    Разработано на будущее. Перейти можно только по `url`, т.к. ссылки в
    шаблон не добавлялись.
    """

    model = Test
    template_name="core/test_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'Все тесты'
        return context


class TestDetailView(ListView):
    """Представление для прохождения теста."""

    template_name="core/test_detail.html"
    paginate_by = 1

    def get_queryset(self):
        self.test = get_object_or_404(Test, id=self.kwargs['pk'])
        return self.test.questions.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = self.test.title
        return context
