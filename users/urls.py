"""Defines URL patterns for users"""
from django.conf.urls import url
from django.contrib.auth.views import LoginView

from . import views

app_name = 'users'
urlpatterns = [
              # Login page
              url(r'^login/$', LoginView.as_view(template_name = 'users/login.html'), name='login'),
              #Link for logged in message
              url(r'^loged_in/$', views.logged_in, name='logged_in'),
              # Logout page
              url(r'^logout/$', views.logout_view, name='logout'),
              # Registration page
              url(r'^register/$', views.register, name='register'),
              #activation from e-mail
              url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
              views.activate, name='activate'),
              # User's profile page
              url(r'^profile/$', views.update_profile, name='profile'),
              # Delete account
              url(r'delete_my_account/$', views.delete_profile, name='delete'),
              # Forgot my password page
              url(r'forgot_my_pswd/$', views.forgot_my_pswd, name='forgot_my_pswd'),
              # Reset password from e-mail
              url(r'^reset_pswd/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.reset_pswd, name='reset_pswd'),
              # Change password page
              url(r'^change_pswd/$', views.change_pswd, name='change_pswd'),

]
