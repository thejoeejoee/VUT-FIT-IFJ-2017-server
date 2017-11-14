# coding=utf-8
import re
from json import loads

from django.core.cache import cache
from django.db.models import F
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from ipware.ip import get_ip

from benchmark.models import ResultAuthor, Team, TestCase, Result


class BaseApiView(View):
    @staticmethod
    def _invalid(message):
        return JsonResponse(dict(
            success=False,
            message=message,
        ))

    @staticmethod
    def _valid(**data):
        return JsonResponse(dict(
            success=True,
            **data
        ))


class GenerateAuthorTokenView(BaseApiView):
    LOGIN_RE = re.compile(r'^x\w{5}\d{2}$')

    def post(self, *args, **kwargs):
        try:
            data = loads(str(self.request.body, encoding='utf-8').lower())  # type: dict
        except ValueError as e:
            return self._invalid('Invalid JSON ({}).'.format(e))

        leader = data.get('leader') or ''
        if not self.LOGIN_RE.match(leader):
            return self._invalid('Invalid team leader login.')

        login = data.get('login') or ''
        if not self.LOGIN_RE.match(login):
            return self._invalid('Invalid login.')

        team, _ = Team.objects.get_or_create(leader_login=leader)
        author = ResultAuthor.objects.filter(
            team=team,
            login=login
        ).first()
        if not author:
            author = ResultAuthor.objects.create(
                team=team,
                ip=get_ip(self.request),
                login=login
            )
        return self._valid(token=author.token)


class BenchmarkResultView(BaseApiView):
    def post(self, *args, **kwargs):
        try:
            data = loads(str(self.request.body, encoding='utf-8'))
        except ValueError as e:
            return self._invalid('Invalid JSON ({}).'.format(e))
        try:
            author = ResultAuthor.objects.get(token=data.get('token'))
        except (TypeError, ValueError, ResultAuthor.DoesNotExist) as e:
            return self._invalid('Unable to resolve author ({}).'.format(e))

        self._process_results(author, data.get('reports', ()))
        return self._valid()

    @staticmethod
    def _process_results(author, reports):
        for report in reports:
            case, _ = TestCase.objects.get_or_create(
                name=report.get('name'),
                section=report.get('section')
            )  # type: TestCase, bool
            if Result.objects.filter(
                    test_case=case,
            ).annotate(
                price=F('operand_price') + F('instruction_price')
            ).filter(price__lt=report.get('operand_price') + report.get('instruction_price')).exists():
                cache.delete(case.cache_key)

            Result.objects.create(
                author=author,
                test_case=case,
                operand_price=report.get('operand_price'),
                instruction_price=report.get('instruction_price'),
            )


class ChartResultDataView(View):
    test_case = None  # type: TestCase

    def get(self, request, *args, **kwargs):
        self.test_case = get_object_or_404(TestCase, pk=self.kwargs.get('pk'))
        cached = cache.get(self.test_case.cache_key)
        if not cached:
            cached = Result.objects.test_case_results(self.test_case)
            cache.set(self.test_case.cache_key, cached)

        return JsonResponse(
            cached,
            json_dumps_params=dict(indent=4)
        )
