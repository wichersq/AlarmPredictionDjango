from .ready_time_calc_ml import AlarmCalcML


def test_calc():
    calendar_event = {'attendees': [{'email': 'example@gmail.com',
                              'responseStatus': 'needsAction'},
                             {'email': 'example1@gmail.com',
                              'organizer': True,
                              'responseStatus': 'accepted',
                              'self': True}],
               'created': '2019-06-21T04:43:59.000Z',
               'creator': {'email': 'example1@gmail.com', 'self': True},
               'description': 'Hiking at Castle Rock',
               'end': {'dateTime': '2019-06-22T11:30:00-07:00'},
               'etag': '"3122184478890000"',
               'htmlLink': 'https://www.google.com/calendar/event?eid=rdjgff',
               'iCalUID': 'fhfkghjhgkj@google.com',
               'id': 'fgfkfjgjhkglytgyu',
               'kind': 'calendar#event',
               'location': 'Stevens Creek County Park, 11401 Stevens Canyon '
                           'Rd, Cupertino, CA 95014, USA',
               'organizer': {'email': 'example1@gmail.com', 'self': True},
               'reminders': {'useDefault': True},
               'sequence': 0,
               'start': {'dateTime': '2019-06-22T10:30:00-07:00'},
               'status': 'confirmed',
               'summary': 'Hiking with Friends',
               'updated': '2019-06-21T04:43:59.445Z'}

    ex_event = {'name': calendar_event['description'],
                'start_address': '150 S Taaffe St, Sunnyvale, CA 94086',
                'end_address': calendar_event['location'],
                'start_time': calendar_event['start']['dateTime'],
                'important_level': 1,
                'travel_by': 3,
                'summary': 'Hiking with Friends'}

    ex_event['travel_duration'] = 38*60
    ex_event['travel_distance'] = 14150
    ex_event['dest_place'] = {'price_level': None,
                            'reviews': 444,
                            'rating': 4.6}

    my_calc = AlarmCalcML()
    alarm_time = my_calc.calc_alarm_time(ex_event)

    assert alarm_time > 3000
    assert alarm_time < 6000