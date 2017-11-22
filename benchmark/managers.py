# coding=utf-8
from operator import methodcaller
from typing import Dict, Iterable

from django.db.models import QuerySet
from django.db.models.manager import Manager


def unique(seq):
    seen = set()
    seen_add = seen.add
    return tuple(x for x in seq if not (x in seen or seen_add(x)))


class TestResultManager(Manager):
    def test_case_results(self, test_case: "models.TestCase") -> Dict[str, Iterable]:
        """
        {
            "teams": [
                "xharmi00",
                "xhraba12",
                "xkobel02",
                ...
            ],
            "data": [
                [
                    "Date",
                    "xharmi00",
                    "xhraba12",
                    "xkobel02",
                    ...
                ],
                [
                    "12. 11.",
                    null,
                    null,
                    33,
                    25,
                    null,
                    null,
                    null
                ],
            ],
            "days": [
                "2017-11-12",
                "2017-11-13",
                ...
            ]
        }
        :return:
        """
        progresses = test_case.v_benchmark_result_price_progress_test_case.order_by('-day')[:10]  # type: QuerySet

        days = tuple(map(methodcaller('strftime', '%d. %m.'), progresses.values_list('day', flat=True)[::-1]))
        progresses = list(progresses)
        teams = []
        teams = list(
            unique([name for progress in progresses for name in progress.team_leader_logins])
        )
        data = [
                   ['Date'] + teams
               ] + [
                   [days[day_i]] + [
                       progress.prices[progress.team_leader_logins.index(team)]
                       if team in progress.team_leader_logins
                       else None
                       for team in teams
                   ]
                   for day_i, progress in enumerate(progresses[::-1])
               ]

        return dict(
            days=days,
            teams=teams,
            data=data
        )
