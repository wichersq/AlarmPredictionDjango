# from enum import Enum
# from ..models import *
import tensorflow as tf
import pandas as pd
#import ml_model
#import prediction_code.ml_model
from . import ml_model


import numpy as np


class AlarmCalcML():
    def __init__(self):
        ml_model.restore()

    # def calc_alarm_time(self):
    #     sample_x = np.reshape([1302, 1, 1, 3.7, 1, 2775, 1], (1, 7))
    #     # sample_x =[[5.03900000e+03, -1,  0, 5, 1,  3.08975745e-04, 1]]
    #     result = ml_model.inference(sample_x)
    #     print(result)
    #     return result

    def calc_alarm_time(self, event):
        input = self.get_input(event)
        sample_x = np.reshape(input, (1, len(input)))
        # sample_x =[[5.03900000e+03, -1,  0, 5, 1,  3.08975745e-04, 1]]
        result = ml_model.inference(sample_x)[0][0]
        print(result)
        return result

    def get_input(self, event):
        input = [event['travel_duration'],
                 event['dest_place']['price_level'], 0,
                 event['dest_place']['rating'], 0,
                 event['dest_place']['reviews'], 0, event['important_level']]
        print("********************ready_time_calc_ml()---get_input()----event*************", event)
        for i in range(1, 6, 2):
            if input[i] != None:
                input[i+1] = 1
            else:
                input[i] = -1
        print("********************ready_time_calc_ml()---get_input()----input*************", input)
        return input


