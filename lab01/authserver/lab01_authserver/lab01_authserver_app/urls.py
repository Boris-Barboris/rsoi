from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^login/$', views.login, name='login'),
    url(r'^users/$', views.users, name='users'),
    url(r'^users/me$', views.users_me),
    url(r'^users/list$', views.users_list),
    url(r'^token/issue$', views.token_issue),
    url(r'^token/verify$', views.token_verify),
    url(r'^token/refresh$', views.token_refresh),
    url(r'^token/grant$', views.token_grant),
]