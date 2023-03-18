from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'core'

urlpatterns = [
    path('', TemplateView.as_view(template_name="core/index.html"), name='index'),
    path('themes/', views.ThemeListView.as_view(), name='themes-list'),
    path('themes/<slug:slug>/', views.ThemeDetailView.as_view(), name='themes-detail'),
    path('tests/', views.TestListView.as_view(), name='tests-list'),
    path('tests/<int:pk>/', views.TestDetailView.as_view(), name='tests-detail'),
]
