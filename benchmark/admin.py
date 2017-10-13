# coding=utf-8
from django.contrib import admin

# Register your models here.
from .models import ResultAuthor, Team, TestCase, Result


@admin.register(ResultAuthor)
class ResultAuthorAdmin(admin.ModelAdmin):
    list_display = ['login', 'token', 'ip', 'team']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['leader_login']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['section', 'name', 'info']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['author', 'test_case', 'price']
