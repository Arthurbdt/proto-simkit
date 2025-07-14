import simpy
import random

import simpy.exceptions
from sim import config
from sim import init_db
from sim.logging import SimulationLogger

# Create a dictionary keyed by shift_id for easy access
SHIFT_LOOKUP = {shift["shift_id"]: shift for shift in config.SHIFTS_DEFINITION}

def run_simulation(pickers, seed=None):
    """ Initialize environment, order queue, and start processes. """
    if seed is not None:
        random.seed(seed)
    # intialize logs
    logger = SimulationLogger()
    logger.log_pickers(pickers)
    init_db.initialize_database()

    # intialize simulation environment
    env = simpy.Environment()
    order_queue = simpy.Store(env)

    # Start picker processes
    for picker in pickers:
        env.process(picker_process(env, picker['picker_id'], 
                                   order_queue, logger, picker['shift_id']))

    # Start order arrival process
    env.process(order_arrival(env, order_queue, logger))

    env.run(until=config.SIM_DURATION)
    print("Simulation complete. Writing logs to database...")
    
    # After simulation ends, write to database
    logger.flush()
    print("Logs written successfully.")


def order_arrival(env, order_queue, logger):
    """ Generate new orders and place them in the shared queue. """
    order_id = 0

    while True:
        # generate order arrival time and due date
        yield env.timeout(random.expovariate(1./config.ORDER_INTERARRIVAL_TIME))
        lead_time = random.uniform(config.ORDER_LEAD_TIME_MIN, 
                                   config.ORDER_LEAD_TIME_MAX)
        due_date = env.now + lead_time
        logger.log_order_arrival(order_id, env.now, due_date)

        # add order to pickers' queue
        yield order_queue.put({"order_id": order_id})
        order_id += 1

def picker_process(env, name, order_queue, logger, shift):
    """ Each picker continuously takes the next available order and processes it """
    
    active_shift = SHIFT_LOOKUP[shift]
    shift_start = active_shift["start_time"]
    shift_end = active_shift["end_time"]

    while True:
        print(env.now)
        minutes_in_day = env.now % config.DAY_DURATION

        # check if resource is on duty
        if shift_start <= minutes_in_day <= shift_end:
            # Calculate remaining time in shift
            time_left_in_shift = shift_end - minutes_in_day
            
            try:
                # Try to get an order, but timeout if we're approaching shift end
                order = yield order_queue.get() | env.timeout(time_left_in_shift)
                # Check if we got an order or timed out
                if hasattr(order, 'value'):  # We got an order
                    order = order.value
                    
                    # Double-check we still have time to process it
                    minutes_in_day = env.now % config.DAY_DURATION
                    if minutes_in_day + config.PICK_TIME_MEAN <= shift_end:
                        logger.log_pick_start(order["order_id"], name, env.now)
                        yield env.timeout(config.PICK_TIME_MEAN)
                        logger.log_pick_end(order["order_id"], env.now)
                    else:
                        # Not enough time left, put order back
                        order_queue.put(order)
                        break  # End shift
                else:
                    # Timed out - shift is ending
                    break
                    
            except simpy.Interrupt:
                # Handle any interrupts if needed
                break
        else:
            # Wait until the next time we are in shift
            time_until_shift = (shift_start - minutes_in_day) % config.DAY_DURATION
            yield env.timeout(time_until_shift)

if __name__ == "__main__":
    run_simulation(config.PICKERS_DEFAULT, seed=42)