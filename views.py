# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import appomatic_booking.models
import appomatic_booking.forms
import settings
import datetime
import django.contrib.auth.tokens
import django.contrib.sites.models
import django.template.loader
import django.utils.http
import appomatic_account.models
import django.contrib.messages
import django.http
import django.core.urlresolvers
from django.utils.translation import ugettext_lazy as _
import django.core.mail
import django.contrib.sites.models
import django.template
import django.contrib.auth.tokens
import django.utils.http


def send_reset_password_mail(request, user = None):
    if not user: user = request.user
    current_site = django.contrib.sites.models.get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain

    t = django.template.loader.get_template('appomatic_booking/new_account_message.txt')
    c = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': django.utils.http.int_to_base36(user.id),
        'user': user,
        'token': django.contrib.auth.tokens.default_token_generator.make_token(user),
        'protocol': request.is_secure() and 'https' or 'http',
    }
    body = t.render(django.template.Context(c))
    try:
        django.core.mail.send_mail(_("Your new account on %s") % site_name, body, None, [user.email])
    except Exception, e:
        django.contrib.messages.warning(request, "Unable to send welcome email: " + str(e))

def event(request, slug):
    events = appomatic_booking.models.Event.objects.all()

    if slug is not None:
        u = request.user
        es = events.filter(slug = slug)

        if es:
            return edit_event(request, es[0])
        else:
            return add_event(request, slug)
    else:
        return list_events(request, events)

def list_events(request, events):
    return django.shortcuts.render_to_response("appomatic_booking/event_list.html", {
        "events": events,
        "user": request.user,
    }, context_instance=django.template.RequestContext(request))

def remove_event_date(request, slug, date_id):
    events = appomatic_booking.models.Event.objects.all()

    e = events.get(slug = slug)
    u = request.user
    assert e.owner.id == u.id

    for date in e.dates.filter(id = date_id):
        date.delete()
    
    redirect_to = django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":e.slug})
            
    return django.http.HttpResponseRedirect(redirect_to)

def edit_event(request, e):
    u = request.user
    if request.method == "POST":
        form = appomatic_booking.forms.EditEventForm(u, request.POST, instance=e)
        if e.owner.id == u.id and form.is_valid():
            e = form.save()
            if form.cleaned_data['add_date']:
                if not e.dates.filter(date = form.cleaned_data['add_date']).count():
                    appomatic_booking.models.EventDate(date=form.cleaned_data['add_date'], event=e).save()

        username = request.POST['username'].lower()
        email = request.POST['email'].lower()
        phone = request.POST['phone']
        dates = [datetime.datetime(*[int(x) for x in day.split("-")]) for day in request.POST.getlist("days")]

        if u.is_anonymous():
            u = django.contrib.auth.models.User(username=username, email=email)
            u.set_unusable_password()
            try:
                u.save()
            except django.db.utils.IntegrityError:
                django.contrib.messages.warning(request, "Unable to register: Username not unique. Please choose another one")
                return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":e.slug}))

            send_reset_password_mail(request, u)

        u.email = email
        u.username = username

        u.save()

        try:
            i = u.info
        except:
            i = None
        if i:
            i.phone = phone
            i.save()
        else:
            appomatic_account.models.UserInfo(user = u, phone = phone).save()

        try:
            event_booking = u.event_bookings.get(event__id = e.id)
        except:
            event_booking = appomatic_booking.models.EventBooking(booker=u, event=e)
        event_booking.save()

        for date in event_booking.dates.all():
            date.delete()

        for date in dates:
            d = e.dates.get(date=date)
            appomatic_booking.models.EventDateBooking(event_booking = event_booking, date=d).save()

        return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":e.slug}))
    else:
        form = appomatic_booking.forms.EditEventForm(u, instance=e)

    return django.shortcuts.render_to_response(
        "appomatic_booking/event.html", 
        {
            "event": e,
            "user": u,
            'static_url': settings.STATIC_URL,
            "form": form,
            },
        context_instance=django.template.RequestContext(request))


def add_event(request, slug):
    if request.method == "POST":
        if request.user.is_authenticated():
            form = appomatic_booking.forms.EventForm(request.user, request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.owner = request.user
                event.save()
                django.contrib.messages.add_message(request, django.contrib.messages.SUCCESS,
                                                    _("added event '%s'") % event.name)
                return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":event.slug}))
    form = appomatic_booking.forms.EventForm(request.user)    
    return django.shortcuts.render_to_response("appomatic_booking/event_add.html", {"form": form}, context_instance=django.template.RequestContext(request))


