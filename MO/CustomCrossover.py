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


class CustomCrossover(Crossover):

    def __init__(self):
        super().__init__(2, 1)  # Specifies the number of parents and offspring for the crossover

    def _do(self, problem, X, **kwargs):
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
                        p2routes[i].append(len(p2matrix[0][0])-1)                       # Add back depot at end of route
                else:
                    oroutes.append(p2routes[k])
                    leftovers = [x for x in leftovers if x not in p2routes[k]]
                    for i in range(len(p1routes)):
                        p1routes[i] = [x for x in p1routes[i] if x not in p2routes[k]]  # Remove duplicate requests from other parent
                        p1routes[i].insert(0, 0)
                        p1routes[i].append(len(p1matrix[0][0])-1)
            # Add the leftovers
            for l in leftovers:
                randcar = random.randint(0, len(oroutes) - 1)                                 # pick a random vehicle
                ld = l + problem.n
                randindex = random.randint(1, len(oroutes[randcar]) - 1)                  # pick a random point in the route
                oroutes[randcar].insert(randindex, l)                                     # add pick up point
                randindex2 = random.randint(randindex + 1, len(oroutes[randcar]) - 1)     # pick a random point in the route after pickup
                oroutes[randcar].insert(randindex2, ld)

            # transform child routes into output format
            childmatrix = routetomatrix(problem, oroutes)
            child = matrixtooutput(problem, childmatrix)
            # add child to offpring
            offspring[0, m] = child
        return offspring
