# coding=utf-8
import threading

from django.utils.text import slugify


def async_call(target, *args, **kwargs):
    """
    Call target asynchronously.
    :param target: callable to call
    :param args: args to give to callable
    :param kwargs: kwargs to give to callable
    :return: Thread instance
    """
    thread = threading.Thread(
        target=target,
        name=slugify(target),
        args=args,
        kwargs=kwargs
    )
    thread.deamon = True
    thread.start()
    return thread
