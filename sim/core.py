import simpy
import random
from sim import config
from sim import init_db
from sim.logging import SimulationLogger

def run_simulation(pickers, seed=None):
    """ Initialize environment, order queue, and start processes. """
    if seed is not None:
        random.seed(seed)
    # intialize logs
    logger = SimulationLogger()
    logger.log_pickers(pickers)
    
    # intialize simulation environment
    env = simpy.Environment()
    order_queue = simpy.Store(env)

    # Start picker processes
    for picker in pickers:
        env.process(picker_process(env, picker['picker_id'], order_queue, logger, picker['shift_id']))

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

    while True:
        order = yield order_queue.get()
        logger.log_pick_start(order["order_id"], name, env.now)
        yield env.timeout(config.PICK_TIME_MEAN)
        logger.log_pick_end(order["order_id"], env.now)

if __name__ == "__main__":
    run_simulation(config.PICKERS_DEFAULT, seed=42)