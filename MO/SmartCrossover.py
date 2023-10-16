from pymoo.core.crossover import Crossover
import numpy as np
import random


def maptomatrix(X, Darp):
    REQ = Darp.REQ
    reqnum = len(Darp.REQ)
    routematrix = np.zeros((Darp.k, reqnum, reqnum))
    for i in REQ:
        for j in REQ:
            for k in Darp.vehicles:
                routematrix[k][i][j] = X[j + reqnum*i + reqnum*reqnum*k]    # map routes to 3D array
    return routematrix


def routetomatrix(problem, routes):
    childmatrix = np.zeros((problem.k, len(problem.REQ), len(problem.REQ)))

    # generate matrix from routes for child
    for k in range(problem.k):
        for i in range(len(routes[k]) - 1):
            childmatrix[k][routes[k][i]][routes[k][i+1]] = 1
    return childmatrix


def matrixtooutput(darp, routematrix):
    output = np.zeros((2*darp.n+2)*(2*darp.n+2)*darp.k, dtype=bool)
    for i in darp.REQ:
        for j in darp.REQ:
            for k in darp.vehicles:
                output[j + len(darp.REQ)*i + len(darp.REQ)*len(darp.REQ)*k] = routematrix[k][i][j] == 1   # map routes to 3D array
    return output


def randomcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), False)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]

        # Map the parents data to matrix and route lists
        p1matrix = maptomatrix(p1, problem)
        p2matrix = maptomatrix(p2, problem)
        p1routes = problem.construct_routes(p1matrix)
        p2routes = problem.construct_routes(p2matrix)

        # Perform crossover operation
        oroutes = p1routes.copy()                              # Copy all routes from one parent
        randvehicle = random.randint(0, problem.k - 1)

        route1 = p1routes[randvehicle]
        route2 = p2routes[randvehicle]

        duplicates = [x for x in route2 if x not in route1]     # generate list of requests that are only in the route of route 2
        leftovers = [x for x in route1 if x not in route2]    # generate list of requests that are only in the route of route 1

        for i in range(0, len(oroutes)):
            oroutes[i] = [x for x in oroutes[i] if x not in duplicates]     # Remove duplicate requests from child

        leftovers = [x for x in leftovers if x <= problem.n]

        oroutes[randvehicle] = route2                          # Change one random route into a route of the other parent

        # Add the leftovers
        for l in leftovers:
            randcar = random.randint(0, len(oroutes) - 1)                                 # pick a random vehicle
            ld = l + problem.n                                                        # Drop off request ID
            ltime = problem.earliest_pickup[l]
            ldtime = problem.latest_dropoff[ld]
            index = 0
            for i in range(1, len(oroutes[randcar])):
                index = i
                if problem.earliest_pickup[oroutes[randcar][i]] > ltime:
                    oroutes[randcar].insert(index, l)                           # if earliest pickup of index request is later than l, insert l at this index
                    break
                if i == len(oroutes[randcar]) - 1:
                    oroutes[randcar].insert(index, l)                           # if at final request, add l before depot
                    break

            for i in range(index + 1, len(oroutes[randcar])):                        # if latest drop off of index request is later than ld, insert ld at this index
                if problem.latest_dropoff[oroutes[randcar][i]] > ldtime:
                    oroutes[randcar].insert(i, ld)
                    break
                    if i == len(oroutes[randcar]) - 1:
                        oroutes[randcar].insert(i, ld)                           # if at final request, add l before depot
                        break


        # transform child routes into output format
        childmatrix = routetomatrix(problem, oroutes)
        child = matrixtooutput(problem, childmatrix)
        # add child to offpring
        offspring[0, m] = child
    return offspring


def guidedcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), False)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]

        # Map the parents data to matrix and route lists
        p1matrix = maptomatrix(p1, problem)
        p2matrix = maptomatrix(p2, problem)
        p1routes = problem.construct_routes(p1matrix)
        p2routes = problem.construct_routes(p2matrix)

        # Perform crossover operation
        oroutes = p1routes.copy()                              # Copy all routes from one parent
        randvehicle = random.randint(0, problem.k - 1)

        route1 = p1routes[randvehicle]
        route2 = p2routes[randvehicle]

        duplicates = [x for x in route2 if x not in route1]     # generate list of requests that are only in the route of route 2
        leftovers = [x for x in route1 if x not in route2]    # generate list of requests that are only in the route of route 1

        for i in range(0, len(oroutes)):
            oroutes[i] = [x for x in oroutes[i] if x not in duplicates]     # Remove duplicate requests from child

        leftovers = [x for x in leftovers if x <= problem.n]

        oroutes[randvehicle] = route2                          # Change one random route into a route of the other parent

        # Add the leftovers
        for l in leftovers:
            randcar = random.randint(0, len(oroutes) - 1)                                 # pick a random vehicle
            ld = l + problem.n                                                        # Drop off request ID
            ltime = problem.earliest_pickup[l]
            ldtime = problem.latest_dropoff[ld]
            index = 0
            for i in range(1, len(oroutes[randcar])):
                index = i
                if problem.earliest_pickup[oroutes[randcar][i]] > ltime:
                    oroutes[randcar].insert(index, l)                           # if earliest pickup of index request is later than l, insert l at this index
                    break
                if i == len(oroutes[randcar]) - 1:
                    oroutes[randcar].insert(index, l)                           # if at final request, add l before depot
                    break

            for i in range(index + 1, len(oroutes[randcar])):                        # if latest drop off of index request is later than ld, insert ld at this index
                if problem.latest_dropoff[oroutes[randcar][i]] > ldtime:
                    oroutes[randcar].insert(i, ld)
                    break
                if i == len(oroutes[randcar]) - 1:
                    oroutes[randcar].insert(i, ld)                           # if at final request, add l before depot
                    break


        # transform child routes into output format
        childmatrix = routetomatrix(problem, oroutes)
        child = matrixtooutput(problem, childmatrix)
        # add child to offpring
        offspring[0, m] = child
    return offspring


class SmartCrossover(Crossover):

    def __init__(self):
        super().__init__(2, 1)  # Specifies the number of parents and offspring for the crossover

    def _do(self, problem, X, **kwargs):
        offspring = []
        randint = random.randint(1, 10)
        if randint > 5:
            offspring = guidedcrossover(problem, X)
        else:
            offspring = randomcrossover(problem, X)
        return offspring



