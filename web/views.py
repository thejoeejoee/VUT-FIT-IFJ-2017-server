# coding=utf-8
from django.views.generic import TemplateView

from benchmark.models import TestCase


class HomepageView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        return dict(
            cases=TestCase.objects.all()
        )
