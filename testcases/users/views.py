from django.contrib.auth import get_user_model
from django.db.models import Case, Count, F, When
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView, TemplateView

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

    template_name = 'users/users_list.html'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.annotate(
            tests_finished=Count(Case(When(usertest__finish=True, then=1)))
        ).annotate(
            tests_started=Count(Case(When(usertest__start=True, then=1)))
        ).order_by('-wallet__total_won')


class UserMeView(TemplateView):
    """
    Представление для личной страницы пользователя.

    Где он может потратить свои монетки.
    """

    template_name = 'users/user_me.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color'] = None
        user_color_cost = self.request.user.color.cost
        queryset = Color.objects.filter(cost__gt=user_color_cost)
        if queryset:
            context['color'] = queryset.first()
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
