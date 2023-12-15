import random
import copy
from pymoo.core.mutation import Mutation
import numpy as np


def randomswap(problem, routes):
    pickup1 = random.randint(1, problem.n)  # randomly pick 2 requests
    pickup2 = random.randint(1, problem.n)
    v1 = 0
    v2 = 0
    dropoff1 = pickup1 + problem.n
    dropoff2 = pickup2 + problem.n
    pindex1, pindex2, dindex1, dindex2 = 0, 0, 0, 0
    for k in problem.vehicles:
        if pickup1 in routes[k]:  # find indices of the requests
            pindex1 = routes[k].index(pickup1)
            dindex1 = routes[k].index(dropoff1)
            v1 = k
        if pickup2 in routes[k]:
            pindex2 = routes[k].index(pickup2)
            dindex2 = routes[k].index(dropoff2)
            v2 = k
    if pindex1 != 0:  # perform swap
        routes[v1][pindex1] = pickup2
        routes[v1][dindex1] = dropoff2
    if pindex2 != 0:
        routes[v2][pindex2] = pickup1
        routes[v2][dindex2] = dropoff1
        # convert to output
    return routes


class CustomMutation(Mutation):

    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        n_individuals, n_var = X.shape
        for i in range(n_individuals):
            # Perform mutation on the i-th individual
            individual = X[i, :]
            routes = maptoroute(individual, problem)
            routes = randomswap(problem, routes)
            individual = routetomap(routes, problem)
            X[i, :] = individual

        return X


def routetomap(routes, Darp):
    sample = np.zeros(4 * Darp.n)
    sindex = 0
    for v in range(len(routes)):
        for i in range(1, len(routes[v]) - 1):
            sample[sindex] = routes[v][i]
            sample[sindex + 2 * Darp.n] = v
            sindex += 1
    return sample


def maptoroute(x, Darp):
    n = Darp.n
    routes = [[0] for _ in Darp.vehicles]  # add depot to each vehicle
    for i in range(0, 2 * n):
        routes[int(x[i + 2 * n])].append(int(x[i]))  # add next request to corresponding vehicle
    for i in Darp.vehicles:  # add depot to each vehicle
        routes[i].append(2 * n + 1)
    return routes
