# coding=utf-8

from django.conf.urls import url, include

from .views import HomepageView

urlpatterns = [
    url(r'^$', HomepageView.as_view()),
    url(r'api/', include('api.urls')),
]
