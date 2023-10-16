import numpy as np
from pymoo.core.sampling import Sampling
import random


class CustomSampling(Sampling):
    def __init__(self, n_samples):
        super().__init__()
        self.n_samples = n_samples

    def _do(self, problem, n_samples, **kwargs):
        X = []
        for _ in range(n_samples):
            sample = createroutesample(problem)
            X.append(sample)
        return X


def createroutesample(Darp):
    routematrix = np.zeros((Darp.k, len(Darp.REQ), len(Darp.REQ)))

    routes = list()
    for k in range(Darp.k):
        routes.append([0])                          # each vehicle starts at depot
    randomorder = list(range(1, Darp.n+1))
    random.shuffle(randomorder)
    for i in randomorder:
        randcar = random.randint(0, Darp.k - 1)     # choose random vehicle
        routes[randcar].append(i)                   # add pickup request to the chosen vehicle
        routes[randcar].append(i + Darp.n)          # add dropoff request too
    for k in range(Darp.k):
        routes[k].append(2*Darp.n + 1)               # each vehicle ends at depot

    # generate matrix from routes
    for k in range(Darp.k):
        for i in range(len(routes[k]) - 1):
            routematrix[k][routes[k][i]][routes[k][i+1]] = 1

    # map 3D matrix to sample input
    sample = np.zeros((2*Darp.n+2)*(2*Darp.n+2)*Darp.k, dtype=bool)
    for i in Darp.REQ:
        for j in Darp.REQ:
            for k in Darp.vehicles:
                sample[j + len(Darp.REQ)*i + len(Darp.REQ)*len(Darp.REQ)*k] = routematrix[k][i][j] == 1   # map routes to 3D array
    return sample
