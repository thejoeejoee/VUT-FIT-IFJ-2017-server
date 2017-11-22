# coding=utf-8
from operator import attrgetter

from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Avg, F
from django.db.models.aggregates import Count, Max
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from benchmark.models import TestCase, Team, Result
from web.utils import DefaultOrderedDict


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        sections = DefaultOrderedDict(list)
        for test_case in TestCase.objects.order_by('section').prefetch_related(
                'result_test_case',
        ).annotate(
            average_price=Avg(F('result_test_case__operand_price') + F('result_test_case__instruction_price')),
            results_count=Count('result_test_case__id'),
        ):
            sections[test_case.section].append(test_case)

        return dict(
            sections=sections.items(),
            main_cases=TestCase.objects.filter(
                result_test_case__isnull=False
            ).annotate(
                avg=Avg(F('result_test_case__operand_price') + F('result_test_case__instruction_price'))
            ).annotate(
                team_count=Count('result_test_case__author__team', distinct=True)
            ).order_by('-result_test_case__author__team')[:8],

            teams=Team.objects.prefetch_related('result_author_team__result_author').filter(
                result_author_team__result_author__isnull=False
            ).distinct(), reverse=True, key=attrgetter('last_result.x_created'),
        )


class ChartDetailView(TemplateView):
    template_name = "web/chart-detail.html"

    def get_context_data(self, **kwargs):
        return dict(
            case=get_object_or_404(TestCase, pk=self.kwargs.get('pk')),
            prefix='detail'
        )
