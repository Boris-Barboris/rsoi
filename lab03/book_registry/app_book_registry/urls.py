from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^prints/$', views.prints),
    url(r'^prints/(?P<isbn>[0-9]+)/$', views.prints_isbn),
]