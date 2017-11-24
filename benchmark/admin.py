# coding=utf-8
from django.contrib import admin
# Register your models here.
from django.db.models import QuerySet
from django.http.request import HttpRequest

from .models import ResultAuthor, Team, TestCase, Result


@admin.register(ResultAuthor)
class ResultAuthorAdmin(admin.ModelAdmin):
    list_display = ['login', 'token', 'ip', 'team']


def merge_teams(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    if queryset.count() < 2:
        model_admin.message_user(request, 'You have to select at minimal 2 teams.')
        return

    target = queryset.first() # type: Team
    for team in queryset.exclude(pk=target.pk): # type: Team
        team.result_author_team.update(team=target)
        team.delete()


merge_teams.short_description = "Merge selected teams into first selected."


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['leader_login']
    actions = [merge_teams]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['section', 'name', 'info']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['author', 'test_case', 'price', 'x_created']
    date_hierarchy = 'x_created'
    list_filter = ['test_case', 'author']
