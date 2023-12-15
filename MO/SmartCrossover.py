from pymoo.core.crossover import Crossover
import numpy as np
import random


def maptoroute(x, Darp):
    n = Darp.n
    routes = [[0] for _ in Darp.vehicles]   # add depot to each vehicle
    for i in range(0, 2 * n):
        routes[int(x[i+2*n])].append(int(x[i]))       # add next request to corresponding vehicle
    for i in Darp.vehicles:                 # add depot to each vehicle
        routes[i].append(2*n+1)
    return routes


def randomcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), 0)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]

        # Map the parents data to routes
        p1routes = maptoroute(p1, problem)
        p2routes = maptoroute(p2, problem)

        # Perform crossover operation
        oroutes = list()
        leftovers = list(range(1, problem.n + 1))     # generate list of requests
        randomorder = list(range(len(p1routes)))
        random.shuffle(randomorder)
        for k in randomorder:
            rand = random.randint(0,1)
            if rand == 0:
                oroutes.append(p1routes[k])          # For each vehicle assign either the route of parent 1 or 2
                leftovers = [x for x in leftovers if x not in p1routes[k]]
                for i in range(len(p2routes)):
                    p2routes[i] = [x for x in p2routes[i] if x not in p1routes[k]]  # Remove duplicate requests from other parent
                    p2routes[i].insert(0, 0)                                        # Add back depot at start of route
                    p2routes[i].append(2 * problem.n + 1)                       # Add back depot at end of route
            else:
                oroutes.append(p2routes[k])
                leftovers = [x for x in leftovers if x not in p2routes[k]]
                for i in range(len(p1routes)):
                    p1routes[i] = [x for x in p1routes[i] if x not in p2routes[k]]  # Remove duplicate requests from other parent
                    p1routes[i].insert(0, 0)
                    p1routes[i].append(2 * problem.n + 1)
        # Add the leftovers
        for l in leftovers:
            randcar = random.randint(0, len(oroutes) - 1)                                 # pick a random vehicle
            ld = l + problem.n
            randindex = random.randint(1, len(oroutes[randcar]) - 1)                  # pick a random point in the route
            oroutes[randcar].insert(randindex, l)                                     # add pick up point
            randindex2 = random.randint(randindex + 1, len(oroutes[randcar]) - 1)     # pick a random point in the route after pickup
            oroutes[randcar].insert(randindex2, ld)

        # transform child routes into output format
        child = routetomap(oroutes, problem)
        # add child to offpring
        offspring[0, m] = child

    return offspring


def maptoroute(x, Darp):
    routes = [[0] for _ in Darp.vehicles]   # add depot to each vehicle
    for i in range(0, 2 * Darp.n):
        routes[int(x[i+2*Darp.n])].append(int(x[i]))       # add next request to corresponding vehicle
    for i in Darp.vehicles:                 # add depot to each vehicle
        routes[i].append(2*Darp.n+1)
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


def guidedcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), 0)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]

        # Map the parents data to matrix and route lists
        p1routes = maptoroute(p1, problem)
        p2routes = maptoroute(p2, problem)

        # Perform crossover operation
        oroutes = p1routes.copy()                              # Copy all routes from one parent
        randvehicle = random.randint(0, problem.k)

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
            window = ldtime - ltime
            shift = random.randint(0, window)
            pickuptime = int(ltime + shift - window/2)
            dropshift = random.randint(0, ldtime + 30 - pickuptime)
            dropofftime = pickuptime + dropshift
            index = 0
            for i in range(1, len(oroutes[randcar])):
                index = i
                if problem.earliest_pickup[oroutes[randcar][i]] > pickuptime:
                    oroutes[randcar].insert(index, l)                           # if earliest pickup of index request is later than l, insert l at this index
                    break
                if i == len(oroutes[randcar]) - 1:
                    oroutes[randcar].insert(index, l)                           # if at final request, add l before depot
                    break

            for i in range(index + 1, len(oroutes[randcar])):                        # if latest drop off of index request is later than ld, insert ld at this index
                if problem.latest_dropoff[oroutes[randcar][i]] > dropofftime:
                    oroutes[randcar].insert(i, ld)
                    break
                if i == len(oroutes[randcar]) - 1:
                    oroutes[randcar].insert(i, ld)                           # if at final request, add l before depot
                    break


        # transform child routes into output format
        child = routetomap(oroutes, problem)
        # add child to offpring
        offspring[0, m] = child
    return offspring


class SmartCrossover(Crossover):

    def __init__(self, s_odds):
        super().__init__(2, 1)  # Specifies the number of parents and offspring for the crossover
        self.odds = s_odds

    def _do(self, problem, X, **kwargs):
        offspring = []
        randint = random.randint(1, 100)
        if randint <= self.odds:
            offspring = guidedcrossover(problem, X)
        else:
            offspring = randomcrossover(problem, X)
        return offspring



