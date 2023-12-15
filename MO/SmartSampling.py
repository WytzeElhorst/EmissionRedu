import numpy as np
from pymoo.core.sampling import Sampling
import random


class SmartSampling(Sampling):
    def __init__(self, n_samples):
        super().__init__()
        self.n_samples = n_samples

    def _do(self, problem, n_samples, **kwargs):
        X = []
        for _ in range(n_samples):
            sample = createroutesample(problem)
            X.append(sample)
        return X


# creates a random correct permutation of requests
def randomorder(n):
    order = list()
    candidates = list(range(1, n + 1))  # initialize candidate list as all pick up requests
    while candidates:
        rindex = random.randrange(len(candidates))
        request = candidates[rindex]
        del candidates[rindex]
        order.append(request)
        if request <= n:  # if pick up request, add corresponding drop off to candidates
            candidates.append(request + n)
    return order


def freevehicles(Darp, routes, req):
    fvehicles = list()
    for k in range(len(routes)):
        curload = 0
        for i in routes[k]:
            curload += Darp.load[i]
        if curload + Darp.load[req] <= Darp.capacity[k]:
            fvehicles.append(k)
    return fvehicles


def calculatepriority(Darp, curreq, fv, routes):
    targettime = (Darp.earliest_pickup[curreq] + Darp.latest_dropoff[curreq]) / 2
    actualtime = 0
    maxtime = max(Darp.latest_dropoff[1:-1]) + 60
    if len(routes[fv]) > 1:
        actualtime = Darp.earliest_pickup[routes[fv][1]]
    else:
        return maxtime/Darp.k
    for i in range(2, len(routes[fv])):
        actualtime = max(actualtime + Darp.service_time[routes[fv][i]] + Darp.t_time[routes[fv][i-1], routes[fv][i]], Darp.earliest_pickup[routes[fv][i]])
    actualtime += Darp.service_time[curreq] + Darp.t_time[routes[fv][-1], curreq]
    if actualtime > Darp.latest_dropoff[curreq]:
        return 480
    return abs(targettime - actualtime)


def createroutesample(Darp):
    routes = list()
    for k in range(Darp.k):
        routes.append([0])  # each vehicle starts at depot
    randorder = randomorder(Darp.n)
    while randorder:
        curreq = randorder[0]
        del randorder[0]
        if curreq <= Darp.n:
            fvehicles = freevehicles(Darp, routes, curreq)
            if not fvehicles:  # If no free vehicles available
                randorder.append(curreq)  # Place request back at end of list
            else:
                minp = 10000
                selectedv = 0
                for fv in fvehicles:
                    timevalue = calculatepriority(Darp, curreq, fv, routes)
                    if timevalue < minp:  # New minimum found
                        minp = timevalue
                        selectedv = fv

                routes[selectedv].append(curreq)  # Add request to chosen vehicle
        else:
            pickup = curreq - Darp.n
            found = False
            for k in range(len(routes)):
                if pickup in routes[k]:  # If pick up is already in a route
                    found = True
                    index = len(routes[k]) - 1
                    while True:
                        if Darp.latest_dropoff[curreq] > Darp.earliest_pickup[routes[k][index]]:    # check if latest drop off is feasible timewise at end of list
                            routes[k].insert(index + 1, curreq)                                         # Add drop off to route
                            break
                        else:
                            index += -1                                                             # if not feasible at this index, check previous index
            if not found:
                randorder.append(curreq)  # If pick up is not in the routes, place drop off back at end of list


    for k in range(Darp.k):
        routes[k].append(2 * Darp.n + 1)  # each vehicle ends at depot

    sample = np.zeros(4 * Darp.n)
    sindex = 0
    for v in range(len(routes)):
        for i in range(1, len(routes[v]) - 1):
            sample[sindex] = routes[v][i]
            sample[sindex + 2 * Darp.n] = v
            sindex += 1

    return sample

