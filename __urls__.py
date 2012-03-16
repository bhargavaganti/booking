# -*- coding: utf-8 -*-

import django.conf.urls.defaults

urlpatterns = django.conf.urls.defaults.patterns(
    '',
    django.conf.urls.defaults.url(r'^booking/?$', 'appomatic_booking.views.event', name="booking_event_list"),
    django.conf.urls.defaults.url(r'^booking/(?P<slug>\w+)/?$', 'appomatic_booking.views.event', name="booking_event"),
    django.conf.urls.defaults.url(r'^booking/(?P<slug>\w+)/remove-date/(?P<date_id>\d+)/?$', 'appomatic_booking.views.remove_event_date', name="booking_event_remove_date"),
)
