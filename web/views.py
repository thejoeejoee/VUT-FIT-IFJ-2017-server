# coding=utf-8
from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from benchmark.models import TestCase, Team


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        return dict(
            cases=TestCase.objects.all(),
            main_cases=TestCase.objects.filter(
                result_test_case__isnull=False
            ).annotate(
                avg=Avg(F('result_test_case__operand_price') + F('result_test_case__instruction_price'))
            ).order_by('-avg')[:5],
            teams=Team.objects.filter(
                result_author_team__result_author__isnull=False
            ).distinct().order_by('x_created', )
        )


class ChartDetailView(TemplateView):
    template_name = "web/chart-detail.html"

    def get_context_data(self, **kwargs):
        return dict(
            case=get_object_or_404(TestCase, pk=self.kwargs.get('pk')),
            prefix='detail'
        )
