# coding=utf-8

from django.conf.urls import url

from .views import HomepageView, ChartDetailView

urlpatterns = [
    url(r'^$', HomepageView.as_view()),
    url(r'^chart-detail/(?P<pk>[\w\d-]+)$', ChartDetailView.as_view(), name="chart_detail"),
]
