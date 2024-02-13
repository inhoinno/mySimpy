"""
Carwash example.

Covers:

- Waiting for other processes
- Resources: Resource

Scenario:
  A carwash has a limited number of washing machines and defines
  a washing processes that takes some (random) time.

  Car processes arrive at the carwash at a random time. If one washing
  machine is available, they start the washing process and wait for it
  to finish. If not, they wait until they can use one.

"""

import itertools
import random
import simpy

# fmt: off
RANDOM_SEED = 42
NUM_MACHINES = 4        # Number of machines in the carwash
WASHTIME = 0.45           # Minutes it takes to clean a car
T_INTER = 2             # Create a car every ~7 minutes
SIM_TIME = 10000       # Simulation time in minutes
# fmt: on

class Channel:
    def __init__(self, env, xfertime):
        self.env = env
        self.xfertime = xfertime
        self.busy = simpy.Resource(env, 1)

    def transfer(self, way, name):
        yield self.env.timeout(self.xfertime)
        
        with way.register.request() as request:
            yield request
            #yield :
            print(f'{name} sent to the plane at {env.now:.2f}.')
            yield env.process(way.read())    #go to reading
            print(f'{name} return to the chnl at {env.now:.2f}.')



class Plane:
    def __init__(self, env, num_register, readtime, writetime, erasetime):
        self.env = env
        self.register = simpy.Resource(env, num_register)
        self.writetime = writetime
        self.readtime = readtime

    def write(self):
        yield self.env.timeout(self.writetime)

    def read(self):
        yield self.env.timeout(self.readtime)

class NANDFlashController:
    def __init__(self, env, ch, way):
        self.env=env
        #self.channels=simpy.Resource(env, num_channels)
        #self.planes = simpy.Resource(env, num_ways)
        self.cpu = simpy.Resource(env, 1)
        self.chnl= ch
        self.way = way

    def send(self, ch, way):
        with ch.busy.request() as request:
            yield request
            #yield :
            print(f' sent to the chnl at {env.now:.2f}.')
            yield env.process(ch.transfer(way))    #go to washing
            print(f' return to the ctrl at {env.now:.2f}.')
    
    def schedule(self, name):
        self.env.timeout(1) 
        #self.send(self.chnl, self.way)
        with self.chnl.busy.request() as request:
            yield request
            #yield :
            print(f'{name} sent to the chnl at {env.now:.2f}.')
            yield env.process(self.chnl.transfer(self.way, name))    #go to washing
            print(f'{name} return to the ctrl at {env.now:.2f}.')



class Carwash:
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.

    'Cars' have to request one of 'the machines'. 
    When they got one, they
    can start the washing processes and wait for it to finish (which
    takes ``washtime`` minutes).

    """
    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime
        self.readtime = 0.65
        self.writetime =0.450

    def wash(self, car):
        """The washing processes. It takes a ''car'' processes and tries to clean it"""
        yield self.env.timeout(self.washtime)
        pct_dirt = random.randint(50,99)
        print(f"Carwash removed {pct_dirt}% of {car}'s dirt.")

    def read(self, car):
        yield self.env.timeout(self.readtime)
        print(f"Carwash read.")

    def write(self, car):
        yield self.env.timeout(self.writetime)
        print(f"Carwash write.")

def car(env, name, nand, opcode):
    """The car process (each car has a ``name``) arrives at the carwash
    (``cw``) and requests a cleaning machine.

    It then starts the washing process, waits for it to finish and
    leaves to never come back ...

    """
    print(f'{name} arrives at the NANDCtrl at {env.now:.2f}.')
    with nand.cpu.request() as request:   
        #cw.machine.request() this calls carwash machine and send request
        yield request
        #yield : 
        print(f'{name} enters the NANDCtrl at {env.now:.2f}.')
        yield env.process(nand.schedule(name))    #go to washing
        print(f'{name} leaves the NANDCtrl at {env.now:.2f}.')


def setup(env, num_chnls, num_ways, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    #nand = NANDFlashController(env, 1, 1)
    ch = Channel(env, 10)
    way = Plane(env, 1, 65, 45, 2000)
    car_count = itertools.count()

    nand = NANDFlashController(env, ch, way)

    for i in range(4):
        env.process(car(env, f'Car {next(car_count)}', nand, 1))

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        env.process(car(env, f'Car {next(car_count)}', nand, 1))


# Setup and start the simulation
print('Carwash')
print('Check out http://youtu.be/fXXmeP9TvBg while simulating ... ;-)')
random.seed(RANDOM_SEED)  # This helps to reproduce the results

# Create an environment and start the setup process
env = simpy.Environment()
#env.process(setup(env, NUM_MACHINES, WASHTIME, T_INTER))
env.process(setup(env, 1, 1, T_INTER))
# Execute!
env.run(until=SIM_TIME)















