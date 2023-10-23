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


class CustomRepair(Repair):

    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        n_individuals, n_var = X.shape
        for i in range(n_individuals):
            # Perform mutation on the i-th individual
            individual = X[i, :]
            matrix = problem.maptomatrix(individual)
            routes = problem.construct_routes(matrix)
            for k in range(len(routes)):
                newroute = fixload(problem, routes[k], problem.capacity[k])
                routes[k] = newroute
            individual = problem.matrixtooutput(problem.routetomatrix(routes))
            X[i, :] = individual
        return X

