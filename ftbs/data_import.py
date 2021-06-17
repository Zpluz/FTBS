import string
import random
from rstr import Rstr
from ftbs.models import *
import datetime


def airplane_import(num):
    airplane_types = ['B737-700', 'B737-800', 'B737-900', 'A-319', 'A-320', 'A-321']
    random.seed(10)
    for i in range(num):
        random.shuffle(airplane_types)
        plane_type = random.choice(airplane_types)
        duration = random.randint(1, 12)
        capacity = 132
        airplane = Airplane(type=plane_type, duration=duration, capacity=capacity)
        airplane.save()


def airline_import():
    airline_list = ['国际航空', '东方航空', '南方航空', '海南航空', '上海航空', '深圳航空', '四川航空', '厦门航空']
    address_list = ['北京', '上海', '广州', '海南', '上海', '深圳', '四川', '厦门']
    for i in range(8):
        name = airline_list[i]
        address = address_list[i]
        account = 0
        airline = Airline(name=name, address=address, account=account)
        dup_airline = Airline.objects.filter(name=name, address=address, account=account)
        if dup_airline:
            continue
        else:
            airline.save()


def seat_import():
    for i in range(31, 53):
        row = i
        column_list = ['A', 'B', 'C', 'J', 'K', 'L']
        for j in range(6):
            column = column_list[j]
            seat = Seat(row=row, column=column)
            seat.save()


def flight_import():
    rs = Rstr(random.SystemRandom())
    airlines = list(Airline.objects.all())
    planes = list(Airplane.objects.all())
    times = []
    thistime = datetime.datetime.now()
    for i in range(1, 5):
        nexttime = thistime + datetime.timedelta(hours=i)
        times.append(nexttime)
    hour_intervals = [datetime.timedelta(hours=2), datetime.timedelta(hours=1, minutes=30),
                      datetime.timedelta(hours=2, minutes=30)]
    day_intervals = [datetime.timedelta(days=0), datetime.timedelta(days=1),
                     datetime.timedelta(days=2), datetime.timedelta(days=3)]
    airline_dict = {'南方航空': 'CZ', '东方航空': 'MU', '国际航空': 'CA', '海南航空': 'HU',
                    '上海航空': 'FM', '深圳航空': 'ZH', '四川航空': '3U', '厦门航空': 'MF'}
    locations = ['北京', '深圳', '上海', '广州', '武汉', '成都', '南昌', '合肥', '深圳', '天津', '济南',
                 '重庆', '香港', '海口', '郑州', '南京', '乌鲁木齐', '拉萨', '兰州', '石家庄', '沈阳', '厦门']
    prices = [599, 699, 799, 899, 1099]
    while True:
        if not planes:
            break
        else:
            random.shuffle(airlines)
            random.shuffle(planes)
            random.shuffle(times)
            random.shuffle(locations)
            random.shuffle(hour_intervals)
            random.shuffle(day_intervals)
            random.shuffle(times)
            airline = random.choice(airlines)
            airline_name = airline.name
            code_prefix = airline_dict[airline_name]
            plane = random.choice(planes)
            planes.remove(plane)
            code = code_prefix + rs.rstr(string.digits, 4)
            loc_sample = random.sample(locations, 2)
            start = loc_sample[0]
            destination = loc_sample[1]
            time = random.choice(times)
            h_interval = random.choice(hour_intervals)
            for i in day_intervals:
                takeoff_time = time + i
                landing_time = takeoff_time + h_interval
                takeoff_time = takeoff_time.strftime('%Y-%m-%d %H:%M')
                landing_time = landing_time.strftime('%Y-%m-%d %H:%M')
                flight_price = random.choice(prices)
                flight = Flight(airline=airline, plane=plane, code=code, start=start, destination=destination,
                                takeoff_time=takeoff_time, landing_time=landing_time, flight_price=flight_price)
                dup_flight = Flight.objects.filter(airline=airline, plane=plane, code=code, start=start,
                                                   destination=destination, takeoff_time=takeoff_time,
                                                   landing_time=landing_time, flight_price=flight_price)
                if dup_flight:
                    continue
                else:
                    flight.save()



# airline_import()
# seat_import()
# airplane_import(50)
# flight_import()
