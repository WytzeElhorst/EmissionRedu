import random

from pymoo.core.mutation import Mutation
import numpy as np
from CustomCrossover import CustomCrossover


class CustomMutation(Mutation):

    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        if random.randint(1, 10) >= 1:
            n_individuals, n_var = X.shape
            for i in range(n_individuals):
                # Perform mutation on the i-th individual
                individual = X[i, :]
                matrix = problem.maptomatrix(individual)
                routes = problem.construct_routes(matrix)
                pickup1 = random.randint(1, problem.n)                              # randomly pick 2 requests
                pickup2 = random.randint(1, problem.n)
                dropoff1 = pickup1 + problem.n
                dropoff2 = pickup2 + problem.n
                for k in range(problem.k):
                    pindex1, pindex2, dindex1, dindex2 = 0, 0, 0, 0
                    if pickup1 in routes[k]:                                        # find indices of the requests
                        pindex1 = routes[k].index(pickup1)
                        dindex1 = routes[k].index(dropoff1)
                    if pickup2 in routes[k]:
                        pindex2 = routes[k].index(pickup2)
                        dindex2 = routes[k].index(dropoff2)
                    if pindex1 != 0:                                                # perform swap
                        routes[k][pindex1] = pickup2
                        routes[k][dindex1] = dropoff2
                    if pindex2 != 0:
                        routes[k][pindex2] = pickup1
                        routes[k][dindex2] = dropoff1
                    # convert to output
                individual = problem.matrixtooutput(problem.routetomatrix(routes))
                X[i, :] = individual

        return X
