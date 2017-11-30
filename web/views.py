# coding=utf-8

from django.core.cache import cache
from django.db.models.aggregates import Count
from django.db.models.expressions import OrderBy, F
from django.db.models.functions.base import Length
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from benchmark.models import TestCase, Team, Result
from web.utils import DefaultOrderedDict


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        sections = cache.get('sections')
        if not sections:
            sections = DefaultOrderedDict(list)
            for test_case in TestCase.objects.annotate(name_len=Length('name')).order_by('section', 'name_len', 'name'):
                sections[test_case.section].append(test_case)
            cache.set('sections', [(k, tuple(v)) for k, v in sections.items()])
            sections = sections.items()

        return dict(
            sections=sections,

            main_cases=TestCase.objects.filter(
                result_test_case__isnull=False
            ).annotate(
                team_count=Count('result_test_case__author__team', distinct=True)
            ).order_by('-team_count')[:5],

            teams=Team.objects.distinct().select_related('v_team_last_result_team').order_by(
                OrderBy(F('v_team_last_result_team__last_result'), descending=True, nulls_last=True)
            ),
            last_result=Result.objects.latest('x_created'),
        )


class ChartDetailView(TemplateView):
    template_name = "web/chart-detail.html"

    def get_context_data(self, **kwargs):
        return dict(
            case=get_object_or_404(TestCase, pk=self.kwargs.get('pk')),
            prefix='detail'
        )
