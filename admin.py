# -*- coding: utf-8 -*-
import django.contrib.admin
import appomatic_booking.models
import appomatic_renderable.admin

class EventDateInline(django.contrib.admin.TabularInline):
    model = appomatic_booking.models.EventDate

class EventAdmin(appomatic_renderable.admin.ArticleAdmin):
    inlines = [EventDateInline]

django.contrib.admin.site.register(appomatic_booking.models.Event, EventAdmin)

class EventDateBookingInline(django.contrib.admin.TabularInline):
    model = appomatic_booking.models.EventDateBooking

class EventDateAdmin(django.contrib.admin.ModelAdmin):
    inlines = [EventDateBookingInline]

django.contrib.admin.site.register(appomatic_booking.models.EventBooking, EventDateAdmin)
