import simpy
import random

from sim import config
from sim import init_db
from sim.logging import SimulationLogger

# Create a dictionary keyed by shift_id for easy access
SHIFT_LOOKUP = {shift["shift_id"]: shift for shift in config.SHIFTS_DEFINITION}
SKILL_LOOKUP = {skill["skill_id"]: skill for skill in config.SKILLS_DEFINITION}


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

    # start simulation processes
    for picker in pickers:
        env.process(picker_process(env, picker['picker_id'], order_queue, 
                                   logger, picker['shift_id'], picker['skill_id']))
    env.process(order_arrival(env, order_queue, logger))
    env.run(until=config.SIM_DURATION)

    # log results
    print("Simulation complete. Writing logs to database...")
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
        #print(f"{env.now}: Order {order_id} has entered the system with a lead time of {lead_time} minutes")

        # add order to pickers' queue
        yield order_queue.put({"order_id": order_id})
        order_id += 1

def picker_process(env, name, order_queue, logger, shift, skill):
    """ Each picker continuously takes the next available order and processes it """
    
    # fetch shift and skill info
    active_shift = SHIFT_LOOKUP[shift]
    shift_start = active_shift["start_time"]
    shift_end = active_shift["end_time"]
    speed_factor = SKILL_LOOKUP[skill]['speed_factor']

    while True:
        time_of_day = env.now % config.DAY_DURATION 

        # check if resource is on shift
        if shift_start <= time_of_day < shift_end:
            time_left_in_shift = shift_end - time_of_day
            # check that there is enough time to complete the next order
            if time_left_in_shift >= (config.PICK_TIME_MEAN * speed_factor):
                try:
                    # Check if the queue has parts before attempting to get
                    if len(order_queue.items) > 0:
                        logger.log_picker_state(name, "getting_order", env.now)
                        pick_part = order_queue.get()
                        end_of_shift = env.timeout(time_left_in_shift - (config.PICK_TIME_MEAN * speed_factor))
                        result = yield pick_part | end_of_shift
                        if pick_part in result:
                            order = result[pick_part]
                            logger.log_picker_state(name, "picking", env.now)
                            logger.log_pick_start(order["order_id"], name, env.now)
                            yield env.timeout(config.PICK_TIME_MEAN * speed_factor)
                            logger.log_pick_end(order["order_id"], env.now)
                        else:
                            # End of shift before getting a part
                            logger.log_picker_state(name, "off_shift", env.now)
                            pass
                    else:
                        # Wait a little before checking again
                        logger.log_picker_state(name, "waiting", env.now)
                        yield env.timeout(config.ORDER_INTERARRIVAL_TIME)
                except simpy.Interrupt:
                    break
            else:
                # Not enough time to process an order, wait until the end of shift
                logger.log_picker_state(name, "waiting", env.now)
                yield env.timeout(time_left_in_shift)
        else:
            # Wait until next shift
            logger.log_picker_state(name, "off_shift", env.now)
            time_until_next_shift = (shift_start - time_of_day) % config.DAY_DURATION
            yield env.timeout(time_until_next_shift)

if __name__ == "__main__":
    run_simulation(config.PICKERS_DEFAULT, seed=42)
