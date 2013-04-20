# -*- coding: utf-8 -*-

import django.conf.urls

urlpatterns = django.conf.urls.patterns(
    '',
    (r'^auth/', django.conf.urls.include('django.contrib.auth.urls'))
)

