import simpy
import random
from sim import config
from sim.logging import SimulationLogger

def run_simulation(num_pickers, seed=None):
    """ Initialize environment, order queue, and start processes. """
    if seed is not None:
        random.seed(seed)
    env = simpy.Environment()
    logger = SimulationLogger()
    order_queue = simpy.Store(env)

    # Start picker processes
    for i in range(num_pickers):
        env.process(picker_process(env, f"Picker-{i+1}", order_queue, logger))

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
        yield env.timeout(config.ORDER_INTERARRIVAL_TIME)
        logger.log_order_arrival(order_id, env.now)

        yield order_queue.put({"order_id": order_id})
        order_id += 1

def picker_process(env, name, order_queue, logger):
    """ Each picker continuously takes the next available order and processes it """

    while True:
        order = yield order_queue.get()
        logger.log_pick_start(order["order_id"], name, env.now)
        yield env.timeout(config.PICK_TIME_MEAN)
        logger.log_pick_end(order["order_id"], env.now)

if __name__ == "__main__":
    run_simulation(config.NUM_PICKERS, seed=42)