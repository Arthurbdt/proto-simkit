
SIM_DURATION = 60 * 24          # minutes * hours 
DAY_DURATION = 60 * 24          # minutes * hours
ORDER_INTERARRIVAL_TIME = 2     # mean time between order (minutes)
NUM_PICKERS = 2                 # number of pickers in the warehouse
PICK_TIME_MEAN = 5              # mean time to pick an order (minutes)
LABOR_COST_PER_HOUR = 20        # cost of labor per hour
LATE_PENALTY_PER_ORDER = 5      # penalty for late orders
ORDER_LEAD_TIME_MIN = 60        # mimimum lead time to complete an order
ORDER_LEAD_TIME_MAX = 180       # maximum lead time to complete an order

SHIFTS_DEFINITION = [
    {"shift_id": 1, "shift_name": "Day Shift", "start_time": 0.0, "end_time": 480.0},
    {"shift_id": 2, "shift_name": "Night Shift", "start_time": 480.0, "end_time": 960.0},
]

PICKERS_DEFAULT = [
    {"picker_id": "Picker 1", "shift_id": 1}
]

'''
PICKERS_DEFAULT = [
    {"picker_id": "Picker 1", "shift_id": 1},
    {"picker_id": "Picker 2", "shift_id": 1},
    {"picker_id": "Picker 3", "shift_id": 2},
]
'''