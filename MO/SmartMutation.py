import random
import copy
from pymoo.core.mutation import Mutation
import numpy as np
from CustomCrossover import CustomCrossover


def randomswap(problem, routes):
    pickup1 = random.randint(1, problem.n)  # randomly pick 2 requests
    pickup2 = random.randint(1, problem.n)
    dropoff1 = pickup1 + problem.n
    dropoff2 = pickup2 + problem.n
    for k in range(problem.k):
        pindex1, pindex2, dindex1, dindex2 = 0, 0, 0, 0
        if pickup1 in routes[k]:  # find indices of the requests
            pindex1 = routes[k].index(pickup1)
            dindex1 = routes[k].index(dropoff1)
        if pickup2 in routes[k]:
            pindex2 = routes[k].index(pickup2)
            dindex2 = routes[k].index(dropoff2)
        if pindex1 != 0:  # perform swap
            routes[k][pindex1] = pickup2
            routes[k][dindex1] = dropoff2
        if pindex2 != 0:
            routes[k][pindex2] = pickup1
            routes[k][dindex2] = dropoff1
            # convert to output
    return routes


def routeswap(problem, routes):
    rand1 = random.randint(0, problem.k - 1)
    rand2 = random.randint(0, problem.k - 1)
    route1 = copy.deepcopy(routes[rand1])
    route2 = copy.deepcopy(routes[rand2])
    routes[rand1] = route2
    routes[rand2] = route1
    return routes


def randmigration(problem, routes):
    pickup = random.randint(1, problem.n)
    dropoff = pickup + problem.n
    for k in range(problem.k):                  # find and remove chosen request from current vehicle
        pindex, dindex = 0, 0
        if pickup in routes[k]:
            pindex = routes[k].index(pickup)
            dindex = routes[k].index(dropoff)
            del routes[k][dindex]
            del routes[k][pindex]
            break
    vehicle = random.randint(0, problem.k - 1)                  # pick random vehicle
    newindex = random.randint(1, len(routes[vehicle]) - 1)      # pick a random index from the vehicle route
    routes[vehicle].insert(newindex, pickup)                    # insert pick up at this index
    dropindex = random.randint(newindex + 1, len(routes[vehicle]) - 1)      # do same for drop off
    routes[vehicle].insert(dropindex, dropoff)
    return routes


def timingswap(problem, routes):
    while True:
        vehicle = random.randint(0, problem.k - 1)              # pick a random non-empty vehicle
        if len(routes[vehicle]) > 2:
            break
    index = random.randint(1, len(routes[vehicle]) - 2)     # pick a random non depot request
    if index > 1:
        if problem.earliest_pickup[routes[vehicle][index]] < problem.earliest_pickup[routes[vehicle][index - 1]]:   # swap if request window starts before prev request window
            temp = routes[vehicle][index]
            routes[vehicle][index] = routes[vehicle][index - 1]
            routes[vehicle][index - 1] = temp
    elif index < len(routes[vehicle]) - 2:
        if problem.earliest_pickup[routes[vehicle][index]] < problem.earliest_pickup[routes[vehicle][index + 1]]:   # swap if request window starts after next request window
            temp = routes[vehicle][index]
            routes[vehicle][index] = routes[vehicle][index + 1]
            routes[vehicle][index + 1] = temp
    return routes


def routedistance(problem, route):
    distance = 0
    index = 0
    n_index = 0
    for k in range(0, len(route) - 1):
        index = route[k]
        n_index = route[k + 1]
        distance += problem.t_time[index][n_index]
    return distance


def distanceswap(problem, routes):
    while True:
        vehicle = random.randint(0, problem.k - 1)              # pick a random non-empty vehicle
        if len(routes[vehicle]) > 2:
            break
    index = random.randint(1, len(routes[vehicle]) - 2)     # pick a random non depot request
    candidateroute1 = copy.deepcopy(routes[vehicle])        # first candidate route which checks swap with previous request
    if index > 1 & routes[vehicle][index] - problem.n != routes[vehicle][index - 1]:    # if not first request or previous request is corresponding pick up
        candidateroute1[index - 1] = routes[vehicle][index]
        candidateroute1[index] = routes[vehicle][index - 1]
    candidateroute2 = copy.deepcopy(routes[vehicle])                                                           # second candidate route which checks swap with next request
    if index < len(routes[vehicle]) - 2 & routes[vehicle][index] + problem.n != routes[vehicle][index + 1]:    # if not final request or next request is corresponding drop off
        candidateroute2[index + 1] = routes[vehicle][index]
        candidateroute2[index] = routes[vehicle][index + 1]

    originaldis = routedistance(problem, routes[vehicle])
    cand1dis = routedistance(problem, candidateroute1)
    cand2dis = routedistance(problem, candidateroute2)
    if cand1dis < originaldis & cand1dis < cand2dis:    # if candidate 1 route is shortest, use it in actual route
        routes[vehicle] = candidateroute1
    if cand2dis < originaldis & cand2dis < cand1dis:    # if candidate 2 route is shortest, use it in actual route
        routes[vehicle] = candidateroute2
    return routes


def durationredu(problem, routes):
    while True:
        vehicle = random.randint(0, problem.k - 1)              # pick a random non-empty vehicle
        if len(routes[vehicle]) > 2:
            break
    index = random.randint(1, len(routes[vehicle]) - 2)         # pick a random non depot request
    request = routes[vehicle][index]
    if request <= problem.n:                                    # if pick up request
        if routes[vehicle][index + 1] != request + problem.n:       # if next request is not corresponding drop off
            routes[vehicle][index] = routes[vehicle][index + 1]     # Move pick up request 1 step towards drop off
            routes[vehicle][index + 1] = request
    else:                                                       # if drop off request
        if routes[vehicle][index - 1] != request - problem.n:
            routes[vehicle][index] = routes[vehicle][index - 1]     # Move drop off request 1 step closer to pick up
            routes[vehicle][index - 1] = request

    return routes


def routeduration(problem, route):
    if len(route) > 2:
        starttime = problem.earliest_pickup[route[1]]
        endtime = problem.latest_dropoff[route[len(route) - 2]]
        return starttime - endtime
    return 0


def maxrouteredu(problem, routes):
    vehicle = 0
    maxdur = 0
    for k in range(len(routes) - 1):
        if routeduration(problem, routes[k]) > maxdur:
            maxdur = routeduration(problem, routes[k])
            vehicle = k
    coinflip = random.randint(0, 1)
    pickup, dropoff = 0, 0
    if len(routes[vehicle]) > 2:
        if coinflip == 0:                   # remove first request in route + corresponding drop off
            pickup = routes[vehicle][1]
            del routes[vehicle][1]
            dropoff = pickup + problem.n
            dindex = routes[vehicle].index(dropoff)
            del routes[vehicle][dindex]
        else:                               # remove final request in route + corresponding pick up
            index = len(routes[vehicle]) - 2
            dropoff = routes[vehicle][index]
            del routes[vehicle][index]
            pickup = dropoff - problem.n
            pindex = routes[vehicle].index(pickup)
            del routes[vehicle][pindex]
    vehicle = random.randint(0, problem.k - 1)
    for i in range(1, len(routes[vehicle])):
        if problem.latest_dropoff[pickup] < problem.latest_dropoff[routes[vehicle][i]]:
            routes[vehicle].insert(i, pickup)
            routes[vehicle].insert(i + 1, dropoff)
            break
    return routes


class SmartMutation(Mutation):

    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        n_individuals, n_var = X.shape
        for i in range(n_individuals):
            # Perform mutation on the i-th individual
            individual = X[i, :]
            matrix = problem.maptomatrix(individual)
            routes = problem.construct_routes(matrix)
            rng = random.randint(1, 100)
            if rng <= 30:
                routes = randomswap(problem, routes)
            elif rng <= 60:
                routes = randmigration(problem, routes)
            elif rng <= 70:
                routes = distanceswap(problem, routes)
            elif rng <= 80:
                routes = timingswap(problem, routes)
            elif rng <= 90:
                routes = durationredu(problem, routes)
            elif rng <= 95:
                routes = routeswap(problem, routes)
            else:
                routes = maxrouteredu(problem, routes)

            # convert to output
            individual = problem.matrixtooutput(problem.routetomatrix(routes))
            X[i, :] = individual

        return X


