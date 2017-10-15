# coding=utf-8
from django.db.models import Avg, F
from django.views.generic import TemplateView

from benchmark.models import TestCase


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        return dict(
            cases=TestCase.objects.all(),
            main_cases=TestCase.objects.annotate(
                avg=Avg(F('result_test_case__operand_price') + F('result_test_case__instruction_price'))
            ).order_by('-avg')[:5],
        )
