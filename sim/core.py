import simpy
import random

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
        #print(f"{env.now}: Order {order_id} has entered the system with a lead time of {lead_time} minutes")

        # add order to pickers' queue
        yield order_queue.put({"order_id": order_id})
        order_id += 1


def picker_process(env, name, order_queue, logger, shift):
    """ Each picker continuously takes the next available order and processes it """
    
    active_shift = SHIFT_LOOKUP[shift]
    shift_start = active_shift["start_time"]
    shift_end = active_shift["end_time"]

    while True:
        time_of_day = env.now % config.DAY_DURATION 
        
        # Debug print
        print(f"[DEBUG] {name} at time {env.now} (day minute {time_of_day}), shift: {shift_start}-{shift_end}")

        # check if resource is on shift
        if shift_start <= time_of_day < shift_end:
            # Calculate remaining time in shift
            time_left_in_shift = shift_end - time_of_day
            
            print(f"[DEBUG] {name} on duty, time left: {time_left_in_shift}")
            
            # Check if there is enough time to complete an order
            if time_left_in_shift >= config.PICK_TIME_MEAN:
                try:
                    # Try to get an order, but timeout if we're approaching shift end
                    pick_part = order_queue.get()
                    end_of_shift = env.timeout(time_left_in_shift - config.PICK_TIME_MEAN)
                    
                    print(f"[DEBUG] {name} waiting for order or timeout ({time_left_in_shift - config.PICK_TIME_MEAN})")
                    result = yield pick_part | end_of_shift
                    
                    # Check which event triggered
                    if pick_part:
                        order = pick_part.value
                        print(f"[DEBUG]{env.now}: {name} got order {order['order_id']}")
                        logger.log_pick_start(order["order_id"], name, env.now)
                        yield env.timeout(config.PICK_TIME_MEAN)
                        logger.log_pick_end(order["order_id"], env.now)
                        print(f"[DEBUG]{env.now}: {name} finished order {order['order_id']}")
                    else:
                        # Picker waited until the end of the shift
                        print(f"[DEBUG] {name} timed out waiting for order")
                        pass
                        
                except simpy.Interrupt:
                    print(f"[DEBUG] {name} interrupted")
                    break
            else:
                # Not enough time left for another pick, wait until shift ends
                print(f"[DEBUG] {name} not enough time left ({time_left_in_shift} < {config.PICK_TIME_MEAN}), waiting {time_left_in_shift}")
                yield env.timeout(time_left_in_shift)
        else:
            # Wait until the next time we are in shift
            time_until_next_shift = (shift_start - time_of_day) % config.DAY_DURATION
            print(f"[DEBUG] {name} off duty, waiting {time_until_next_shift} minutes")
            yield env.timeout(time_until_next_shift)

if __name__ == "__main__":
    run_simulation(config.PICKERS_DEFAULT, seed=42)