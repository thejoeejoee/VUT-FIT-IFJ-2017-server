# coding=utf-8
from .settings_default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ifj_test',
        'USER': 'ifj',
        'PASSWORD': 'DvyCPfL7829pPOrXrK',
        'HOST': 'localhost',
        'PORT': '9000',
    }
}