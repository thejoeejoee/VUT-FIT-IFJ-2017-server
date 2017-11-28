# coding=utf-8
from operator import attrgetter
from uuid import uuid4

from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from benchmark.managers import TestResultManager


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    x_created = models.DateTimeField(auto_created=True, default=timezone.now)

    class Meta(object):
        abstract = True


class Team(BaseModel):
    leader_login = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.leader_login

    @property
    def authors(self):
        return ', '.join(map(str, set(filter(None, map(attrgetter('login'), self.result_author_team.all())))))

    @property
    def last_result(self):
        return getattr(self, 'last_result_', None) or self.result_author_team.filter(
            result_author__isnull=False
        ).latest('result_author__x_created').result_author.latest('x_created')

    class Meta(object):
        ordering = ['x_created', ]


class ResultAuthor(BaseModel):
    team = models.ForeignKey(Team, related_name='result_author_team', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4)

    ip = models.GenericIPAddressField()
    login = models.CharField(max_length=8)

    def __str__(self):
        return '{} ({})'.format(self.login, self.team)

    class Meta(object):
        ordering = ['x_created', ]


class TestCase(BaseModel):
    section = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    info = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return '/'.join((self.section, self.name))

    @property
    def cache_key(self):
        return 'test-case_{}'.format(self.id)

    @property
    def slug(self):
        return slugify(str(self))

    @property
    def github_link(self):
        if len(self.name) == 3:  # by JSON
            return 'https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/blob/master/ifj2017/tests/{}/tests.json'.format(
                self.section
            )
        return 'https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/blob/master/ifj2017/tests/{}/{}.code'.format(
            self.section,
            self.name
        )

    class Meta(object):
        unique_together = ('section', 'name'),
        ordering = ('section', 'name',)


class Result(BaseModel):
    objects = TestResultManager()

    author = models.ForeignKey(ResultAuthor, related_name='result_author', on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, related_name='result_test_case', on_delete=models.CASCADE)

    instruction_price = models.PositiveIntegerField()
    operand_price = models.PositiveIntegerField()

    @property
    def price(self):
        return self.operand_price + self.instruction_price

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.x_created, self.test_case, self.author, self.price)


class VBenchmarkResultPriceProgress(models.Model):
    test_case = models.ForeignKey(TestCase, related_name='v_benchmark_result_price_progress_test_case',
                                  on_delete=models.DO_NOTHING)
    day = models.DateField()
    team_leader_logins = ArrayField(models.CharField(max_length=128))
    prices = ArrayField(models.IntegerField())

    def __str__(self):
        return '{} - {} - {}'.format(self.test_case, self.day, self.team_leader_logins), self.prices

    class Meta(object):
        managed = False
        db_table = 'v_benchmark_result_price_progress'


class VTeamLastResult(models.Model):
    team = models.OneToOneField(Team, related_name='v_team_last_result_team', on_delete=models.DO_NOTHING)
    last_result = models.DateTimeField()
    result_count = models.IntegerField()

    def __str__(self):
        return '{} - {}'.format(self.team, self.last_result)

    class Meta(object):
        managed = False
        db_table = 'v_team_last_result'
