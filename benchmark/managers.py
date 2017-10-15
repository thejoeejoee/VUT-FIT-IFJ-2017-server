# coding=utf-8
from datetime import timedelta

from django.db.models.aggregates import Min
from django.db.models.expressions import F
from django.db.models.manager import Manager


def unique(seq):
    seen = set()
    seen_add = seen.add
    return tuple(x for x in seq if not (x in seen or seen_add(x)))


class TestResultManager(Manager):
    def test_case_results(self, test_case):
        # type: (TestCase) -> dict
        start = test_case.result_test_case.earliest('x_created').x_created
        end = test_case.result_test_case.latest('x_created').x_created

        delta = end - start  # timedelta

        days = tuple((start + timedelta(days=i)).date() for i in range(delta.days + 2))
        teams = tuple(unique(
            test_case.result_test_case.values_list(
                'author__team__leader_login',
                flat=True
            ).order_by('author__team__leader_login')
        ))
        data = [
            ['Date', *teams],
            *(
                [day.strftime('%d. %m.'), *(
                    test_case.result_test_case.filter(
                        x_created__date=day,
                        author__team__leader_login=login
                    ).aggregate(min=Min(F('operand_price') + F('instruction_price'))).get('min') for login in teams
                )] for day in days
            )
        ]

        return dict(
            days=days,
            teams=teams,
            data=data
        )
