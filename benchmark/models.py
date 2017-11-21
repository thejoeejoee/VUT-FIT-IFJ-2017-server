# coding=utf-8
from operator import attrgetter
from uuid import uuid4

from django.db import models
from django.db.models import Avg, F
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
        return self.result_author_team.latest('result_author__x_created').result_author.latest('x_created')

    class Meta(object):
        ordering = ['x_created', ]


class ResultAuthor(BaseModel):
    team = models.ForeignKey(Team, related_name='result_author_team')
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
        return 'https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/blob/master/ifj2017/tests/{}/{}.code'.format(
            self.section,
            self.name
        )

    @property
    def average_price(self):
        return self.result_test_case.aggregate(avg=Avg(F('operand_price') + F('instruction_price'))).get('avg')

    @property
    def cases_in_section(self):
        return TestCase.objects.filter(section=self.section).order_by('name')

    class Meta(object):
        unique_together = ('section', 'name'),
        ordering = ('section', 'name',)


class Result(BaseModel):
    objects = TestResultManager()

    author = models.ForeignKey(ResultAuthor, related_name='result_author')
    test_case = models.ForeignKey(TestCase, related_name='result_test_case')

    instruction_price = models.PositiveIntegerField()
    operand_price = models.PositiveIntegerField()

    @property
    def price(self):
        return self.operand_price + self.instruction_price

    def __str__(self):
        return '{} - {} - {}'.format(self.test_case, self.author, self.price)
