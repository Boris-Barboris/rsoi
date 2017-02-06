from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^books/status/$', views.books_status),
    url(r'^books/$', views.books),
    url(r'^books/(?P<id>[0-9]+)/$', views.books_id),
    url(r'^books/(?P<id>[0-9]+)/borrow/(?P<borrow_id>[0-9]+)/$', 
        views.book_borrow),
    url(r'^books/(?P<id>[0-9]+)/return/$', views.book_return),
]