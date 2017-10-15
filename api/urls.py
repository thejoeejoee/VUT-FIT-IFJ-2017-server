# coding=utf-8

from django.conf.urls import url, include

from api.views.v1 import BenchmarkResultView, GenerateAuthorTokenView, ChartResultDataView

v1 = [
    url(r'benchmark-result$', BenchmarkResultView.as_view()),
    url(r'generate-author-token$', GenerateAuthorTokenView.as_view()),
    url(r'chart-result-data/(?P<pk>[\w\d-]+)$', ChartResultDataView.as_view(), name='chart_result_data'),
]

urlpatterns = [
    url(r'v1/', include(v1))
]
