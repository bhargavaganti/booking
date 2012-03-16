# -*- coding: utf-8 -*-
import django.contrib.admin
import appomatic_booking.models

django.contrib.admin.site.register(appomatic_booking.models.Event)
django.contrib.admin.site.register(appomatic_booking.models.EventDate)
django.contrib.admin.site.register(appomatic_booking.models.EventBooking)
django.contrib.admin.site.register(appomatic_booking.models.EventDateBooking)
