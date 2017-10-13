# coding=utf-8

from django.conf.urls import url, include

from api.views.v1 import BenchmarkResultView, GenerateAuthorTokenView

v1 = [
    url(r'benchmark-result$', BenchmarkResultView.as_view()),
    url(r'generate-author-token$', GenerateAuthorTokenView.as_view()),
]

urlpatterns = [
    url(r'v1/', include(v1))
]
