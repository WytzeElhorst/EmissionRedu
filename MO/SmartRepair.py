import numpy as np
from pymoo.core.repair import Repair
from copy import copy


def fixload(problem, route, cap):
    newroute = []
    changed = False
    curload = 0
    backup = copy(route)
    while route:
        request = route[0]
        del route[0]
        if curload + problem.load[request] <= cap:
            newroute.append(request)
            curload += problem.load[request]
        else:
            for i in range(0, len(route) - 1):
                if route[i] > problem.n:                       # check for drop off request
                    if (route[i] - problem.n) in newroute:      # check if corresponding pick up request is in the route already
                        newroute.append(route[i])
                        curload += problem.load[i]
                        del route[i]
                        break
            newroute.append(request)
            curload += problem.load[request]
    if changed:
        print("old route: ", backup)
        print("new route: ", newroute)
    return newroute


# Swaps back pick up and drop off request if they end up in the wrong order

def swapfix(problem, route):
    n = problem.n
    fixed = False
    routebackup = route.copy()
    depot = route[len(route) - 1]
    del route[len(route) - 1]
    newroute = []
    for i in route:
        if i <= n:
            newroute.append(i)
        else:
            if i - n in newroute:
                newroute.append(i)
            else:
                newroute.append(i - n)
                for x in range(i + 1, len(route)):
                    if route[x] == i - n:
                        route[x] = i
                        fixed = True
    newroute.append(depot)
    if fixed:
        print("og route ", routebackup)
        print("new route ", newroute)
    return newroute


def maptoroute(x, Darp):
    n = Darp.n
    routes = [[0] for _ in Darp.vehicles]   # add depot to each vehicle
    for i in range(0, 2 * n):
        routes[int(x[i+2*n])].append(int(x[i]))       # add next request to corresponding vehicle
    for i in Darp.vehicles:                 # add depot to each vehicle
        routes[i].append(2*n+1)
    return routes


def routetomap(routes, Darp):
    sample = np.zeros(4 * Darp.n)
    sindex = 0
    for v in range(len(routes)):
        for i in range(1, len(routes[v]) - 1):
            sample[sindex] = routes[v][i]
            sample[sindex + 2 * Darp.n] = v
            sindex += 1
    return sample


class SmartRepair(Repair):

    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        n_individuals, n_var = X.shape
        for i in range(n_individuals):
            # Perform mutation on the i-th individual
            individual = X[i, :]
            routes = maptoroute(individual, problem)
            for k in range(len(routes)):
                newroute = fixload(problem, routes[k], problem.capacity[k])
                newroute = swapfix(problem, newroute)
                routes[k] = newroute
            individual = routetomap(routes, problem)
            X[i, :] = individual
        return X
