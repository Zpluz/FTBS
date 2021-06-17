import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .models import *
from django.utils import timezone
from django.db import connection


# Create your views here.

def index(request):
    if get_user_model().objects.filter(username='admin') and \
            request.user == get_user_model().objects.get(username='admin'):
        request.session.flush()
    return redirect('ftbs:Home')


def ftbs_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if form.is_valid() and user is not None:
            login(request, user)
            if username == 'admin':
                return HttpResponseRedirect('/admin/')
            return redirect('ftbs:Home')
        else:
            messages.error(request, '登录失败!')
            storage = messages.get_messages(request)
            return render(request, 'login.html', {'messages': storage})
    else:
        if 'storage' in request.session.keys():
            messages.success(request, request.session['storage'])
        storage = messages.get_messages(request)
        return render(request, 'login.html', {'messages': storage})


def ftbs_logout(request):
    logout(request)
    return redirect('ftbs:Login')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        telephone = request.POST['telephone']
        email = request.POST['email']

        if form.is_valid() and get_user_model().objects.create_user(username=username, password=password,
                                                                    telephone=telephone, email=email):
            request.session['storage'] = '注册成功, 请登录!'
            return redirect('ftbs:Login')

        else:
            messages.error(request, '注册失败!')
            storage = messages.get_messages(request)
            return render(request, 'signup.html', {'messages': storage})
    else:
        storage = messages.get_messages(request)
        return render(request, 'signup.html', {'messages': storage})


@login_required
def home(request):
    order_entries = Order.objects.filter(user__exact=request.user)
    future_flight_entries = Flight.objects.filter(takeoff_time__gt=timezone.now() +
                                                  datetime.timedelta(hours=2)).order_by('takeoff_time')[:10]
    close_order = 0
    for i in order_entries:
        if i.order_state == 1 or i.order_state == 3:
            if i.flight.takeoff_time <= (timezone.now() + datetime.timedelta(days=1)):
                close_order = 1
            elif i.flight.takeoff_time <= (timezone.now() + datetime.timedelta(hours=5)):
                close_order = 2

    if request.method == 'GET':
        storage = messages.get_messages(request)
        return render(request, 'home.html', {'messages': storage, 'order_entries': order_entries,
                                             'flight_entries': future_flight_entries, 'close_order': close_order})
    else:
        form = FlightSearchForm(request.POST)
        code = request.POST['code']
        start = request.POST['start']
        destination = request.POST['destination']
        date = request.POST['date']
        if form.is_valid() and not (date and (code or (start and destination))):
            messages.error(request, '条件不足, 无法搜索！')
            storage = messages.get_messages(request)
            return render(request, 'home.html', {'messages': storage, 'order_entries': order_entries,
                                                 'flight_entries': future_flight_entries, 'close_order': close_order})
        else:
            request.session['code'] = code
            request.session['start'] = start
            request.session['destination'] = destination
            request.session['date'] = date
            return redirect('ftbs:Flights')


@login_required
@transaction.atomic
def flight(request):
    if request.method == 'GET':
        if 'reschedule_order_flight' in request.session.keys() and request.session['reschedule_order_flight']:
            reschedule_id = request.session['reschedule_order_flight']
            reschedule_order = Order.objects.get(id=reschedule_id)
            airline = Airline.objects.filter(pk=reschedule_order.flight.airline.id)
            flight_entries = Flight.objects.filter(airline=airline[0],
                                                   takeoff_time__gt=timezone.now() + datetime.timedelta(hours=2),
                                                   start__exact=reschedule_order.flight.start,
                                                   destination__exact=reschedule_order.flight.destination,
                                                   ).exclude(pk=reschedule_order.flight.id)
            if not flight_entries:
                del request.session['reschedule_order_flight']
            return render(request, 'flights.html', {'entries': flight_entries,
                                                    'reschedule_order_flight': reschedule_order})
        else:
            code = request.session['code']
            start = request.session['start']
            destination = request.session['destination']
            date = request.session['date']
            if not code:
                flight_entries = Flight.objects.filter(start__exact=start, destination__exact=destination,
                                                       takeoff_time__date=date)
            else:
                flight_entries = Flight.objects.filter(code__iexact=code, takeoff_time__date=date)

            return render(request, 'flights.html', {'entries': flight_entries})
    else:
        request.session['flight_id'] = request.POST['flight_id']
        if 'reschedule_order_flight' in request.POST.keys() and request.POST['reschedule_order_flight']:
            request.session['reschedule_order_order'] = request.POST['reschedule_order_flight']
        return redirect('ftbs:Order')


@login_required
@transaction.atomic
def order(request):
    flight_id = int(request.session['flight_id'])
    order_flight = Flight.objects.get(id=flight_id)
    # seats_remain = Seat.objects.raw(
    #     'SELECT * FROM ftbs_seat WHERE id not in '
    #     '(SELECT seat_id FROM ftbs_order WHERE flight_id = %d and order_state < 2)', [flight_id]
    # )
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT `seat_id` AS `id`,`row`,`column` FROM ftbs_view_flightseat WHERE flight_id = %s", [str(flight_id)]
        )
        seats_remain = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT `passenger_id` ,`name`, `identity` FROM ftbs_view_usercandidate WHERE user_id = %s",
            [str(request.user.id)]
        )
        candidates = cursor.fetchall()

    if request.method == 'GET':
        reschedule_order = None
        if 'reschedule_order_order' in request.session.keys() and request.session['reschedule_order_order']:
            reschedule_id = request.session['reschedule_order_order']
            reschedule_order = Order.objects.get(id=reschedule_id)
        return render(request, 'order.html', {'flight_code': order_flight.code, 'remains': len(seats_remain),
                                              'seats_remain': seats_remain, 'reschedule_order_order': reschedule_order,
                                              'candidates': candidates})
    else:
        seat_id = int(request.POST['seat'])
        if not seat_id:
            messages.error(request, '您未选择座位!')
            storage = messages.get_messages(request)
            return render(request, 'order.html', {'messages': storage, 'flight_code': order_flight.code,
                                                  'remains': len(seats_remain), 'seats_remain': seats_remain,
                                                  'candidates': candidates})
        else:
            seat = Seat.objects.get(pk=seat_id)
            if 'reschedule_order_order' in request.POST.keys() and request.POST['reschedule_order_order']:
                reschedule_id = request.POST['reschedule_order_order']
                reschedule_order = Order.objects.get(id=reschedule_id)
                passenger = reschedule_order.passenger

                cur_order = Order(user=request.user, passenger=passenger, flight=order_flight, seat=seat,
                                  order_price=order_flight.flight_price, order_state=0, order_time=timezone.now())
                reschedule_order.order_state = 2
                reschedule_order.save()
                request.session['reschedule_order_info'] = reschedule_id
            else:
                if 'name' in request.POST.keys() and request.POST['name']:
                    form = CandidateForm(request.POST)
                    name = request.POST['name']
                    identity = request.POST['identity']
                    seat_id = int(request.POST['seat'])
                    seat = Seat.objects.get(id=seat_id)
                    passenger = Candidate(name=name, identity=identity)
                    dup_passenger = Candidate.objects.filter(name=name, identity=identity)
                    if dup_passenger:
                        passenger = dup_passenger[0]
                    else:
                        passenger.save()
                    cur_order = Order(user=request.user, passenger=passenger, flight=order_flight, seat=seat,
                                      order_price=order_flight.flight_price, order_state=0, order_time=timezone.now())

                    if not form.is_valid():
                        messages.error(request, '乘客信息无效!')
                        storage = messages.get_messages(request)
                        return render(request, 'order.html', {'messages': storage, 'flight_code': order_flight.code,
                                                              'remains': len(seats_remain), 'seats_remain': seats_remain,
                                                              'candidates': candidates})
                else:
                    passenger_id = int(request.POST['candidate_id'])
                    passenger = Candidate.objects.get(id=passenger_id)
                    cur_order = Order(user=request.user, passenger=passenger, flight=order_flight, seat=seat,
                                      order_price=order_flight.flight_price, order_state=0, order_time=timezone.now())

            if Order.objects.filter(passenger=passenger, flight=order_flight, order_state__lt=2):
                messages.error(request, '您有行程冲突!')
                storage = messages.get_messages(request)
                return render(request, 'order.html', {'messages': storage, 'flight_code': order_flight.code,
                                                      'remains': len(seats_remain), 'seats_remain': seats_remain,
                                                      'candidates': candidates})
            else:
                cur_order.save()
                request.session['order_id'] = cur_order.id
                return redirect('ftbs:OrderInfo')


@login_required
@transaction.atomic
def order_info(request):
    if request.method == 'GET':
        order_id = int(request.session['order_id'])
        cur_order = Order.objects.get(id=order_id)
        reschedule_order = None
        minus_price = cur_order.order_price
        if 'reschedule_order_info' in request.session.keys() and request.session['reschedule_order_info']:
            reschedule_id = request.session['reschedule_order_info']
            reschedule_order = Order.objects.get(id=reschedule_id)
            minus_price = cur_order.order_price - reschedule_order.order_price
        return render(request, 'order_info.html', {'order': cur_order, 'reschedule_order_info': reschedule_order,
                                                   'minus_price': minus_price})
    else:
        action = request.POST['action']
        order_id = int(request.POST['order_id'])
        cur_order = Order.objects.filter(pk=order_id)
        cur_user = get_user_model().objects.filter(pk=request.user.id)
        airline = Airline.objects.filter(pk=cur_order[0].flight.airline.id)
        if action == 'pay':
            minus_price = int(request.POST['minus_price'])
            if cur_user[0].balance and cur_user[0].balance > minus_price:
                cur_user.update(balance=cur_user[0].balance - minus_price)
                airline.update(account=airline[0].account + minus_price)
                if 'reschedule_order_info' in request.POST.keys() and request.POST['reschedule_order_info']:
                    cur_order.update(order_state=3)
                    del request.session['reschedule_order_flight']
                    del request.session['reschedule_order_order']
                    del request.session['reschedule_order_info']
                else:
                    cur_order.update(order_state=1)
                return render(request, 'order_info.html', {'order': cur_order[0]})
            else:
                messages.error(request, '余额不足, 支付失败!')
                storage = messages.get_messages(request)
                return render(request, 'order_info.html', {'order': cur_order[0], 'messages': storage})
        elif action == 'do_reschedule':
            request.session['reschedule_order_flight'] = cur_order[0].id
            return redirect('ftbs:Flights')


@login_required
@transaction.atomic
def myorders(request):
    order_entries = Order.objects.filter(user__exact=request.user)
    if request.method == 'GET':
        return render(request, 'myorders.html', {'order_entries': order_entries})
    else:
        order_id = int(request.POST['order_id'])
        cur_order = Order.objects.filter(pk=order_id)
        cur_user = get_user_model().objects.filter(pk=request.user.id)
        airline = Airline.objects.filter(pk=cur_order[0].flight.airline.id)
        action = request.POST['action']
        if action == 'cancel':
            if cur_order[0].order_state == 0:
                cur_order.update(order_state=4)
            elif cur_order[0].order_state == 1 or cur_order[0].order_state == 3:
                cur_user.update(balance=cur_user[0].balance + cur_order[0].order_price)
                airline.update(account=airline[0].account - cur_order[0].order_price)
                cur_order.update(order_state=4)
            return render(request, 'order_info.html', {'order': cur_order[0]})
        elif action == 'check' or action == 'pay':
            request.session['order_id'] = order_id
            return redirect('ftbs:OrderInfo')
        else:
            cur_order.delete()
            return render(request, 'myorders.html', {'order_entries': order_entries})


@login_required
def profile(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT `name`, `identity` FROM ftbs_view_usercandidate WHERE user_id = %s", [str(request.user.id)]
        )
        candidates = cursor.fetchall()
    if request.method == 'POST':
        if 'username' in request.POST.keys() and request.POST['username']:
            request.user.username = request.POST['username']
        if 'email' in request.POST.keys() and request.POST['email']:
            request.user.email = request.POST['email']
        if 'telephone' in request.POST.keys() and request.POST['telephone']:
            request.user.telephone = request.POST['telephone']
        if 'password' in request.POST.keys() and request.POST['password']:
            request.user.password = request.POST['password']
        if 'balance' in request.POST.keys() and request.POST['balance']:
            if not request.user.balance:
                request.user.balance = 0
            request.user.balance = request.user.balance + int(request.POST['balance'])
        request.user.save()
        return render(request, 'profile.html', {'candidates': candidates})
    else:
        return render(request, 'profile.html', {'candidates': candidates})
