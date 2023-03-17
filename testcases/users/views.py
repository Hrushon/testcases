from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import СustomUserCreationForm


class SignUp(CreateView):
    form_class = СustomUserCreationForm
    success_url = reverse_lazy('core:index')
    template_name = 'users/signup.html' 
