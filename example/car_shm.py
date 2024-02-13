import simpy
def car(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the BCS
    yield env.timeout(driving_time)
    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    #If you use the resource with the with statement as shown above, ther resource is automatically being released.
    #If you call request without with, you are responsible to call release() once you are done using the resource
    with bcs.request() as req:
        yield req
        # Charge the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))



env = simpy.Environment()

bcs = simpy.Resource(env, capacity=2)

for i in range(4):
    env.process(car(env, 'Car %d' % i , bcs, i*2, 5))

env.run()
