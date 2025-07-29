
SHIFT_DURATION = 480                # minutes per shift
DAY_DURATION = 2 * SHIFT_DURATION   # number of shifts in a day
SIM_DURATION = 2 * SHIFT_DURATION   # number of shifts simulated
ORDER_INTERARRIVAL_TIME = 2         # mean time between order (minutes)
PICK_TIME_MEAN = 5                  # mean time to pick an order (minutes)
ORDER_LEAD_TIME_MIN = 60            # mimimum lead time to complete an order
ORDER_LEAD_TIME_MAX = 180           # maximum lead time to complete an order


SHIFTS_DEFINITION = [
    {"shift_id": 1, "shift_name": "Day Shift", "start_time": 0.0, "end_time": SHIFT_DURATION},
    {"shift_id": 2, "shift_name": "Night Shift", "start_time": SHIFT_DURATION, "end_time": 2 * SHIFT_DURATION},
]

SKILLS_DEFINITION = [
    {"skill_id": 1, "skill_name": "Junior", "speed_factor": 1.2},
    {"skill_id": 2, "skill_name": "Standard", "speed_factor": 1.0},
    {"skill_id": 3, "skill_name": "Expert", "speed_factor": 0.8}
]

# default pickers configuration for testing and quick simulation run
PICKERS_DEFAULT = [
    {"picker_id": "Picker 1", "shift_id": 1, "skill_id": 1},
    {"picker_id": "Picker 2", "shift_id": 1, "skill_id": 2},
    {"picker_id": "Picker 3", "shift_id": 2, "skill_id": 3}
]