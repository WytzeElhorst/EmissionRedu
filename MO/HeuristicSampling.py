import numpy as np
from pymoo.core.sampling import Sampling
import random


class HeuristicSampling(Sampling):
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
    if len(routes[fv]) > 1:
        actualtime = Darp.earliest_pickup[routes[fv][1]]
    else:
        return 60
    for i in range(2, len(routes[fv])):
        actualtime = max(actualtime + Darp.service_time[routes[fv][i]] + Darp.t_time[routes[fv][i-1], routes[fv][i]], Darp.earliest_pickup[routes[fv][i]])
    actualtime += Darp.service_time[curreq] + Darp.t_time[routes[fv][-1], curreq]
    if actualtime > Darp.latest_dropoff[curreq]:
        return 480
    return abs(targettime - actualtime)


def createroutesample(Darp):
    routematrix = np.zeros((Darp.k, len(Darp.REQ), len(Darp.REQ)))
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
                    routes[k].append(curreq)  # Add drop off to same route
                    found = True
            if not found:
                randorder.append(curreq)  # If pick up is not in the routes, place drop off back at end of list


    for k in range(Darp.k):
        routes[k].append(2 * Darp.n + 1)  # each vehicle ends at depot
    # generate matrix from routes
    for k in range(Darp.k):
        for i in range(len(routes[k]) - 1):
            routematrix[k][routes[k][i]][routes[k][i + 1]] = 1

    # map 3D matrix to sample input
    sample = np.zeros((2 * Darp.n + 2) * (2 * Darp.n + 2) * Darp.k, dtype=bool)
    for i in Darp.REQ:
        for j in Darp.REQ:
            for k in Darp.vehicles:
                sample[j + len(Darp.REQ) * i + len(Darp.REQ) * len(Darp.REQ) * k] = routematrix[k][i][
                                                                                        j] == 1  # map routes to 3D array
    return sample

