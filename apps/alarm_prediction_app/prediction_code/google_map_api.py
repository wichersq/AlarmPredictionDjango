import googlemaps
from googleplaces import GooglePlaces
from namedlist import namedlist
import pprint
from ..models import *

# place_fields = ['id', 'name', 'address', 'hours', 'price_level',
#                 'reviews', 'rating', 'type_store', 'url', 'website']
# Place = namedlist('Place', place_fields, default=None)

# Directions = namedlist('Directions', [
#    'distance', 'duration', 'start_address', 'end_address', 'copyrights'], default=None)
pp = pprint.PrettyPrinter(indent=2)


class MapsAPI:
    TRAVEL_BY = {0: 'walking', 1: 'bicycling',
                     2: 'transit', 3: 'driving', 4:'flight'}
    def __init__(self, API_KEY):
        self.gmaps = googlemaps.Client(
            key=API_KEY, queries_per_second=50, retry_over_query_limit=False)
        self.gmaps_get_place_ID = googlemaps.Client(
            key=API_KEY, queries_per_second=50, retry_over_query_limit=False)
        self.google_places = GooglePlaces(API_KEY)

    def set_place_id(self, place, place_address):
        place.google_place_id = self.get_place_id(place_address)
       
    
    def get_place_id(self, place_address):
        result = self.gmaps_get_place_ID.find_place(
            input=place_address, input_type='textquery')
        try:
            place_id = result['candidates'][0]['place_id']
        except IndexError:
            raise ValueError("Place not found")
        pp.pprint(result)
        return place_id

    def safe_index(self, place_detail, index):
        if index in place_detail:
            return place_detail[index]

    def get_store_detail(self, place):
        maps_place = self.google_places.get_place(place.google_place_id)
        maps_place.get_details()
        detail = maps_place.details
        print("-"*50)
        pp.pprint(detail)
        if 'opening_hours' in detail and 'periods' in detail['opening_hours']:
            place.hours = detail['opening_hours']['periods']
        else:
            place.hours = 'NA'
        place.name = self.safe_index(detail, 'name')
        place.address = self.safe_index(detail, 'formatted_address')
        place.price_level = self.safe_index(detail, 'price_level')
        place.url = self.safe_index(detail, 'url')
        place.website = self.safe_index(detail, 'website')
        place.rating = self.safe_index(detail, 'rating')
        place.reviews = self.safe_index(detail, 'user_rating_total')
        place.type_store = self.safe_index(detail, 'types')
        # place.save()

    def get_place_info(self, place, place_name):
        self.get_place_id(place, place_name)
        self.get_store_detail(place)

    def get_time(self, event, arrival_time):
        leg = None
        directions_result = None
        print('get_time event.start_address', event.start_address)
        print('get_time event.end_address', event.end_address)
        print('get_time arrival_time', arrival_time)
        print('get_time mode', type(self.TRAVEL_BY[event.travel_by]))
        # try:
        directions_result = self.gmaps.directions(event.start_address, event.end_address, mode=self.TRAVEL_BY[event.travel_by], arrival_time=arrival_time)
        leg = directions_result[0]['legs'][0]
        # except IndexError or googlemaps.exceptions.ApiError:
        #     raise ValueError("No route")
        print(directions_result)
        event.start_address = leg['start_address']
        event.end_address = leg['end_address']
        print('get_time - event.save()')
        print('event.start_address' , event.start_address)
        print('event.end_address', event.end_address)
        event.travel_distance = leg['distance']['value']  # in meter
        event.travel_duration = leg['duration']['value']  # in second
        print('event.travel_distance' , event.travel_distance)
        print('event.travel_duration', event.travel_duration)
        event.save()
        print('event.travel_duration', event.travel_duration)
        return event
#     def trial_method(self, event):
#         place = event.dest_place
#         place.google_place_id = 'ChIJryH6Apmwj4ARx08eJ5hAaGQ'
#         place.name = 'Walmart'
#         place.address = '600 Showers Dr, Mountain View, CA 94040, USA'
#         # place.hours = [{'close': {'day': 0, 'time': '2200'},
#         #    'open': {'day': 0, 'time': '0700'}},
#         #   {'close': {'day': 1, 'time': '2200'},
#         #    'open': {'day': 1, 'time': '0700'}},
#         #   {'close': {'day': 2, 'time': '2200'},
#         #    'open': {'day': 2, 'time': '0700'}},
#         #   {'close': {'day': 3, 'time': '2200'},
#         #    'open': {'day': 3, 'time': '0700'}},
#         #   {'close': {'day': 4, 'time': '2200'},
#         #    'open': {'day': 4, 'time': '0700'}},
#         #   {'close': {'day': 5, 'time': '2200'},
#         #    'open': {'day': 5, 'time': '0700'}},
#         #   {'close': {'day': 6, 'time': '2200'},
#         #    'open': {'day': 6, 'time': '0700'}}],
#         place.reviews = 2775
#         place.rating = 3.7
#         # place.type_store = ['supermarket',
#         #    'department_store',
#         #    'grocery_or_supermarket',
#         #    'store',
#         #    'point_of_interest',
#         #    'food',
#         #    'establishment']
#         place.url = 'https://maps.google.com/?cid=7235103823606206407'
#         place.website = 'https://www.walmart.com/store/2280/mountain-view-ca/details'
# self
#         event.start_address = '1920 Zanker Rd #20, San Jose, CA 95112, USA',

#         event.end_address = '600 Showers Dr, Mountain View, CA 94040, USA',

#         event.travel_distance = 21618  # in meter
#         event.travel_duration = 1302  # in second
#         event.save()
#         place.save()

# pp.pprint(API_KEY)
# end_place = maps_api.get_place_info('Walmart Mountain View')
# directions = maps_api.get_time('Coding Dojo San Jose', end_place)

# print(end_place, directions)

# googlemaps.exceptions.ApiError: NOT_FOUND
# ValueError: Place not found
# ValueError: No route
