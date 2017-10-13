# coding=utf-8
from uuid import uuid4

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    x_created = models.DateTimeField(auto_created=True, default=timezone.now)

    class Meta(object):
        abstract = True


class Team(BaseModel):
    leader_login = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.leader_login


class ResultAuthor(BaseModel):
    team = models.ForeignKey(Team, related_name='result_author_team')
    token = models.UUIDField(default=uuid4)

    ip = models.GenericIPAddressField()
    login = models.CharField(max_length=8)

    def __str__(self):
        return '{} ({})'.format(self.login, self.team)


class TestCase(BaseModel):
    section = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    info = models.CharField(max_length=128)

    def __str__(self):
        return '/'.join((self.section, self.name))

    class Meta(object):
        unique_together = ('section', 'name'),
        ordering = ('section', 'name',)


class Result(BaseModel):
    author = models.ForeignKey(ResultAuthor, related_name='result_author')
    test_case = models.ForeignKey(TestCase, related_name='result_test_case')

    instruction_price = models.PositiveIntegerField()
    operand_price = models.PositiveIntegerField()

    @property
    def price(self):
        return self.operand_price + self.instruction_price

    def __str__(self):
        return '{} - {} - {}'.format(self.test_case, self.author, self.price)
