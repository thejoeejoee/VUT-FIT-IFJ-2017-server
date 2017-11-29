# coding=utf-8
import re
from json import loads

import requests
from django.core.cache import cache
from django.db.models import F
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views import View
from ipware.ip import get_ip
from requests import HTTPError

from api.utils import async_call
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


class ServiceOnlineView(BaseApiView):
    @property
    def version(self):
        version = cache.get('package_version')
        if version and False:
            return version

        try:
            response = requests.get('https://pypi.python.org/pypi/IFJcode17-toolkit/json')
            version = response.json().get('info', {}).get('version') or 'unknown'
        except (HTTPError, ValueError, KeyError):
            pass
        cache.set('package_version', version or 'unknown', 20 * 60)  # 20 minutes
        return version or 'unknown'

    def get(self, request, *args, **kwargs):
        return self._valid(
            # msg='Service is online!',
            now=now(),
            version=self.version
        )


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

        async_call(self._process_results, author, data.get('reports', ()))
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

            if Result.objects.annotate(
                    price_total=F('operand_price') + F('instruction_price')
            ).filter(
                author=author,
                test_case=case,
                price_total__lte=report.get('operand_price') + report.get('instruction_price'),
                x_created__date=now().date()
            ).exists():
                continue
            Result.objects.create(
                author=author,
                test_case=case,
                operand_price=report.get('operand_price'),
                instruction_price=report.get('instruction_price'),
            )


class ChartResultDataView(View):
    test_case = None  # type: TestCase

    def get(self, request, *args, **kwargs):
        self.test_case = get_object_or_404(
            TestCase.objects.prefetch_related(
                'result_test_case',
                'result_test_case__author',
                'result_test_case__author__team',
            ),
            pk=self.kwargs.get('pk')
        )
        cached = cache.get(self.test_case.cache_key)
        if not cached:
            cached = Result.objects.test_case_results(self.test_case)
            cache.set(self.test_case.cache_key, cached)

        return JsonResponse(
            cached,
            json_dumps_params=dict(indent=4)
        )
