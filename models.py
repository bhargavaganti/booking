# -*- coding: utf-8 -*-
import django.db.models
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _
import django.contrib.contenttypes
import django.contrib.contenttypes.models
import django.core.urlresolvers
import ckeditor.fields
import appomatic_redhogorg_data.models
import appomatic_account.models
import datetime
import userena.models

class Event(appomatic_redhogorg_data.models.Article):
    min_bookings = django.db.models.IntegerField(_('min_bookings'))
    ideal_bookings = django.db.models.IntegerField(_('ideal_bookings'))
    max_bookings = django.db.models.IntegerField(_('max_bookings'))

    @property
    def sorted_dates(self):
        return self.dates.order_by("date")

    @property
    def date_tree(self):
        ed = []
        last_year = {'year': None, 'nr_dates':0}
        last_month = {'month': None, 'nr_dates':0}
        for date in self.sorted_dates:
            if date.date.year != last_year['year']:
                last_month = {'month':date.date.month, 'dates':[date], 'nr_dates':1}
                last_year = {'year':date.date.year, 'months':[last_month], 'nr_dates':1}
                ed.append(last_year)
            elif date.date.month != last_month['month']:
                last_month = {'month':date.date.month, 'dates':[date], 'nr_dates':1}
                last_year['months'].append(last_month)
                last_year['nr_dates'] += 1
            else:
                last_month['dates'].append(date)
                last_month['nr_dates'] += 1
                last_year['nr_dates'] += 1
        return ed


    def send_reset_password_mail(self, request, user = None):
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

    def handle_edit(self, request, style = 'page.html'):
        if request.method != "POST":
            return {}

        u = request.user        

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
                return {}

            self.send_reset_password_mail(request, u)

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
            event_booking = u.event_bookings.get(event__id = self.id)
        except:
            event_booking = EventBooking(booker=u, event=self)
        event_booking.save()

        for date in event_booking.dates.all():
            date.delete()

        for date in dates:
            d = self.dates.get(date=date)
            EventDateBooking(event_booking = event_booking, date=d).save()

        return {}


class EventDate(django.db.models.Model):
    date = django.db.models.DateField(_('date'))
    event = django.db.models.ForeignKey(Event, related_name="dates")

    @property
    def color(self):
        count = self.bookings.count() - self.event.min_bookings
        ideal = self.event.ideal_bookings - self.event.min_bookings
        maxb = self.event.max_bookings - self.event.min_bookings

        if count < 0 or count > maxb:
            return "#ff0000"

        if count <= ideal:
            p = float(count) / ideal
        else:
            count -= ideal
            maxb -= ideal
            p = float(maxb - count) / maxb
        
        p = int(p * 4)
        return ['#eeffee',
                '#ccffcc',
                '#88ff88',
                '#44ff44',
                '#00ff00'][p]


    def __unicode__(self):
        return "%s @ %s" % (self.event, self.date)

class EventBooking(django.db.models.Model):
    booker = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="event_bookings")
    event = django.db.models.ForeignKey(Event, related_name="bookings")
    comment = django.db.models.TextField(_('comment'))

    @property
    def sorted_dates(self):
        return self.dates.order_by("date__date")

    def __unicode__(self):
        return "%s @ %s" % (self.booker, self.event)


class EventDateBooking(django.db.models.Model):
    event_booking = django.db.models.ForeignKey(EventBooking, related_name="dates")
    date = django.db.models.ForeignKey(EventDate, related_name="bookings")

    def __unicode__(self):
        return "%s @ %s" % (self.event_booking, self.date.date)

class Profile(userena.models.UserenaLanguageBaseProfile):
    pass
