"""Defines URL patterns."""
from django.views.generic import TemplateView
from django.conf.urls import url
from . import views
# from .views import SearchAutocomplete

app_name = 'wordsinmovies_main'

urlpatterns = [

url(r'^$', views.index, name='index'),

url(r'^search/', views.search, name='search'),

url(r'^help/', TemplateView.as_view(template_name="wordsinmovies_main/help.html"), name='help'),

url(r'^about/', TemplateView.as_view(template_name="wordsinmovies_main/about.html"), name='about'),

url(r'^wordlists/', TemplateView.as_view(template_name="wordsinmovies_main/wordlists.html"), name='wordlists'),

url(r'^technical_note/', TemplateView.as_view(template_name="wordsinmovies_main/technical_note.html"), name='technical_note'),

# url(r'^server_err/', TemplateView.as_view(template_name="wordsinmovies_main/500.html"), name='server_err'),

                ]
