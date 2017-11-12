# coding=utf-8
import logging

from collections import defaultdict
from django.core.management import BaseCommand
from django.db.models import Count

from benchmark.models import ResultAuthor, Result


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            return self._process(*args, **options)
        except Exception as e:
            self.stderr.write('Command failed: ().'.format(e))
            logging.exception(e)

    def _process(self, *args, **options):
        duplicities = defaultdict(set)

        for author in ResultAuthor.objects.all():
            duplicities[author.login].add(author)

        for login, authors in filter(lambda pair: len(pair[1]) > 1, duplicities.items()):
            target = ResultAuthor.objects.filter(login=login).earliest('x_created')

            Result.objects.filter(author__login=login).update(author=target)
            ResultAuthor.objects.filter(result_author__isnull=True).delete()


