# -*- coding: utf-8 -*-

import django.conf.urls

urlpatterns = django.conf.urls.patterns(
    '',
    (r'^accounts/', django.conf.urls.include('userena.urls')),
    (r'^auth/', django.conf.urls.include('django.contrib.auth.urls'))
)
