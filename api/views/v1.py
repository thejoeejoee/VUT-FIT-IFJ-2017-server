# coding=utf-8
from json import loads

from django.http.response import JsonResponse
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
    def post(self, *args, **kwargs):
        try:
            data = loads(str(self.request.body, encoding='utf-8'))  # type: dict
        except ValueError as e:
            return self._invalid('Invalid JSON ({}).'.format(e))

        leader = data.get('leader')
        if not leader or len(leader) != 8:
            self._invalid('Invalid team leader login.')

        login = data.get('login')
        if not login or len(login) != 8:
            self._invalid('Invalid login.')

        team, _ = Team.objects.get_or_create(leader_login=leader)
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

    def _process_results(self, author, reports):
        for report in reports:
            case, _ = TestCase.objects.get_or_create(
                name=report.get('name'),
                section=report.get('section')
            )
            Result.objects.create(
                author=author,
                test_case=case,
                operand_price=report.get('operand_price'),
                instruction_price=report.get('instruction_price'),
            )