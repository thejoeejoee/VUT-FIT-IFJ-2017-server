# coding=utf-8
import logging

from django.core.management import BaseCommand
from django.db.models import F, DateField
from django.db.models.functions import Cast

from benchmark.models import Result


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

    # @transaction.atomic
    def _process(self, *args, **options):
        self.log('Starting...')

        while self.remove():
            pass

    kept = set()

    def remove(self):
        for result in Result.objects.filter(
                # x_created__lte=now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=2)
        ).select_related(
            'author__team'
        ).annotate(
            price_=F('operand_price') + F('instruction_price'),
            leader_login=F('author__team__leader_login'),
            date=Cast('x_created', DateField())
        ).order_by('-date', '-price_').exclude(id__in=self.kept).iterator():

            deleted = Result.objects.annotate(
                price_value=F('operand_price') + F('instruction_price')
            ).filter(
                test_case=result.test_case,
                price_value__lte=result.price_,
                author__team=result.author.team,
                x_created__date=result.x_created.date()
            ).exclude(pk=result.pk)._raw_delete('default')
            if deleted:
                self.kept.add(result.id)
                self.log('Deleted many: {}.'.format(deleted))
                return True

            self.log('KEEP {}.'.format(result))

