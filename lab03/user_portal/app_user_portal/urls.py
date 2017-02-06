from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^prints/stored/$', views.prints_stored, name='prints_stored'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^prints/(?P<isbn>[\w]+)/borrow/$', views.borrow, name='borrow'),
    url(r'^borrows/(?P<borrow_id>[0-9]+)/return/$', views.do_return, name='do_return'),
    url(r'^borrows/$', views.borrows, name='borrows'),
    url(r'^$', views.root, name='root'),
]
