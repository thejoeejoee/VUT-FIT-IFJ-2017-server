# coding=utf-8
import logging
from datetime import timedelta
from operator import attrgetter

from django.core.management import BaseCommand
from django.db.models import F
from django.utils.timezone import now

from benchmark.models import Result, VBenchmarkResultPriceProgress


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            return self._process(*args, **options)
        except Exception as e:
            self.stderr.write('Command failed: ({}).'.format(e))
            logging.exception(e)

    def log(self, *args):
        for arg in args:
            self.stderr.write('{}\n'.format(arg))

    def _process(self, *args, **options):
        self.log('Starting...')

        while self.remove():
            pass

    kept = set()

    def remove(self):
        for result in Result.objects.filter(
                x_created__lte=now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=2)
        ).select_related(
            'author__team'
        ).annotate(
            price_=F('operand_price') + F('instruction_price'),
            leader_login=F('author__team__leader_login')
        ).order_by('x_created').exclude(id__in=map(attrgetter('id'), self.kept)).iterator():
            deleted, info = result.test_case.result_test_case.annotate(
                price_value=F('operand_price') + F('instruction_price')
            ).filter(
                price_value__lte=result.price_,
                author__team=result.author.team,
                x_created__date=result.x_created.date()
            ).exclude(pk=result.pk).delete()
            if deleted:
                self.log('Deleted many: {}.'.format(info))
                return True

            if not VBenchmarkResultPriceProgress.objects.filter(
                    test_case=result.test_case,
                    team_leader_logins__contains=[result.leader_login],
                    prices__contains=[result.price_],
            ).exists():
                self.log('DEL {}.'.format(result))
                result.delete()
                continue

            if result.test_case.result_test_case.annotate(
                    price_=F('operand_price') + F('instruction_price')
            ).filter(
                price_=result.price_,
                author__team=result.author.team
            ).exclude(pk=result.pk).exists():
                self.log('DEL {}.'.format(result))
                result.delete()
                continue

            self.log('KEEP {}.'.format(result))
            self.kept.add(result)
