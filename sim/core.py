import simpy
import random
from sim import config

def run_simulation(num_pickers, seed=None):
    """
    Initialize environment, order queue, and start processes.
    """
    if seed is not None:
        random.seed(seed)

    env = simpy.Environment()
    order_queue = simpy.Store(env)

    # Start picker processes
    for i in range(num_pickers):
        env.process(picker_process(env, f"Picker-{i+1}", order_queue))

    # Start order arrival process
    env.process(order_arrival(env, order_queue))

    env.run(until=config.SIM_DURATION)


def order_arrival(env, order_queue):
    """ 
    Periodically generate new orders and place them in the shared queue.
    """
    order_id = 0
    while True:
        yield env.timeout(config.ORDER_INTERARRIVAL_TIME)
        order_id += 1
        order = {"id": order_id, "arrival_time": env.now}
        print(f"Order-{order_id} arrived at {env.now:.2f}")
        yield order_queue.put(order)

def picker_process(env, name, order_queue):
    """
    Each picker continuously takes the next available order and processes it.
    """
    while True:
        order = yield order_queue.get()
        print(f"{name} started Order-{order['id']} at {env.now:.2f}")
        yield env.timeout(random.expovariate(1.0 / config.PICK_TIME_MEAN))
        print(f"{name} finished Order-{order['id']} at {env.now:.2f}")

if __name__ == "__main__":
    run_simulation(config.NUM_PICKERS, seed=42)