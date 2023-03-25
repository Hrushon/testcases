from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (CreateView, ListView, RedirectView,
                                  TemplateView)

from .forms import СustomUserCreationForm
from .models import Color, Wallet

User = get_user_model()


class SignUp(CreateView):
    """Представление для создания объекта пользователя."""

    form_class = СustomUserCreationForm
    success_url = reverse_lazy('core:index')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        self.object = form.save()
        Wallet.objects.create(owner=self.object)
        return super().form_valid(form)


class UserListView(ListView):
    """Представление для списка пользователей."""

    template_name = 'users/user_list.html'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.select_related('wallet', 'color').annotate(
            tests_attempts=Count('attempts'),
            tests_count=Count('attempts__testcase', distinct=True),
            tests_success=Count(
                'attempts__testcase', distinct=True, filter=Q(
                    attempts__success=True
                )
            ),
        ).order_by('-wallet__total_won')


class UserMeView(TemplateView):
    """
    Представление для личной страницы пользователя.

    Где он может потратить свои монеты.
    """

    template_name = 'users/user_me.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color'] = None
        queryset = User.objects.select_related(
            'wallet', 'color'
        ).get(id=self.request.user.id)
        context['object'] = queryset
        user_color_cost = queryset.color.cost
        available_colors = Color.objects.filter(cost__gt=user_color_cost)
        if available_colors:
            context['color'] = available_colors.first()
        return context


class UserColorView(RedirectView):
    """Представление для изменения цвета пользователя."""

    url = reverse_lazy('users:users-me')

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        color = get_object_or_404(Color, pk=kwargs['pk'])
        if color.cost <= user.wallet.current_sum:
            Wallet.objects.filter(owner=user.id).update(
                current_sum=F('current_sum') - color.cost
            )
            self.request.user.color = color
            self.request.user.save()
        return super().get_redirect_url()
