# from enum import Enum
import math
from ..models import *


class AlarmCalc():
    DEFAULT_PREPARE_SEC = 10*60
    SEC_PER_MIN = 60
    MIN_PER_HOUR = 60
    SEC_PER_HOUR = 60*60
    TRAVEL_SEC_PER_BREAK = {'CYCLING': 1 * SEC_PER_HOUR, 'DRIVING': 2 *
                            SEC_PER_HOUR, 'TRANSIT': 4 * SEC_PER_HOUR, 'WALKING': 1 * SEC_PER_HOUR}
    BREAK_TIME_SEC = {'CYCLING': 15 * SEC_PER_MIN, 'DRIVING': 20*SEC_PER_MIN, 'TRANSIT':30*SEC_PER_MIN, 'WALKING': 30 * SEC_PER_MIN}

    def calc_alarm_time(self, event):
        event.prep_duration = self.update_prepare_sec(event)
        arrival_sec = event.early_arrival_sec
        travel_break_sec = self.calc_break_time(event.travel_duration, event.get_travel_by_display().upper())
        print(type(arrival_sec),type(travel_break_sec),type(event.prep_duration),type(event.travel_duration) )
        recommended_ready_sec = arrival_sec + travel_break_sec + event.prep_duration + event.travel_duration
        return recommended_ready_sec

    def update_prepare_sec(self, event):
        prepare_sec = self.DEFAULT_PREPARE_SEC * event.importance_level
        travel_mode =  event.get_travel_by_display().upper()
        print("travel_by", travel_mode)
        if event.travel_duration > (2*self.SEC_PER_HOUR):
            prepare_sec += (5*self.SEC_PER_MIN)*(event.travel_duration/(2*self.SEC_PER_HOUR))
            print((event.travel_duration/(2*self.SEC_PER_HOUR)))
        if travel_mode == 'TRANSIT':
            prepare_sec += (5*self.SEC_PER_MIN)
        return prepare_sec

    def calc_break_time(self,duration_in_sec, travel_mode):
        num_of_break = math.floor(duration_in_sec / self.TRAVEL_SEC_PER_BREAK[travel_mode])
        travel_break_in_sec = int(num_of_break) * self.BREAK_TIME_SEC[travel_mode]
        return travel_break_in_sec

    def calc_sec_arrive(self,reviews, price_level, rating):
        print(reviews, rating, price_level)
        sec = 0
        if(price_level == None):
            sec = 3*60
        else:
            sec = 2*60 * price_level
        if rating != None and rating < 3.0:
            sec += (3-rating) * 2*60
        if reviews == None:
            reviews = 0
        return (0.5 * reviews) + sec


