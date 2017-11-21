# coding=utf-8
from collections import OrderedDict
from operator import attrgetter

from django.db.models import Avg, F
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from benchmark.models import TestCase, Team, Result


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        sections = OrderedDict()
        for test_case in TestCase.objects.order_by('section'):
            if test_case.section not in sections:
                sections[test_case.section] = test_case

        return dict(
            sections=sections.items(),
            main_cases=TestCase.objects.filter(
                result_test_case__isnull=False
            ).annotate(
                avg=Avg(F('result_test_case__operand_price') + F('result_test_case__instruction_price'))
            ).annotate(
                team_count=Count('result_test_case__author__team', distinct=True)
            ).order_by('-result_test_case__author__team')[:8],
            teams=sorted(Team.objects.filter(
                result_author_team__result_author__isnull=False
            ).distinct(), reverse=True, key=attrgetter('last_result.x_created')),
            last_result=Result.objects.latest('x_created')
        )


class ChartDetailView(TemplateView):
    template_name = "web/chart-detail.html"

    def get_context_data(self, **kwargs):
        return dict(
            case=get_object_or_404(TestCase, pk=self.kwargs.get('pk')),
            prefix='detail'
        )
