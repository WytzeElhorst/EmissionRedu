from pymoo.core.crossover import Crossover
import numpy as np
import random


def maptoroute(x, Darp):
    n = Darp.n
    routes = [[0] for _ in Darp.vehicles]  # add depot to each vehicle
    for i in range(0, 2 * n):
        routes[int(x[i + 2 * n])].append(int(x[i]))  # add next request to corresponding vehicle
    for i in Darp.vehicles:  # add depot to each vehicle
        routes[i].append(2 * n + 1)
    return routes


def maptoroute(x, Darp):
    routes = [[0] for _ in Darp.vehicles]  # add depot to each vehicle
    for i in range(0, 2 * Darp.n):
        routes[int(x[i + 2 * Darp.n])].append(int(x[i]))  # add next request to corresponding vehicle
    for i in Darp.vehicles:  # add depot to each vehicle
        routes[i].append(2 * Darp.n + 1)
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


def randomvehicleselection(k):
    return [random.choice([0, 1]) for _ in range(k)]


def splitlist(lst):
    n = len(lst) // 2
    list1 = lst[:n]
    list2 = lst[n:]
    return list1, list2


def getindex(element, my_array):
    indices = np.where(my_array == element)[0]
    if len(indices) > 0:
        return indices[0]
    else:
        return None  # Element not found in the array


def findswath(my_list):
    indices = [index for index, element in enumerate(my_list) if element != -1]
    return indices


def ppmxcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), 0)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]

        # Perform crossover operation
        # Selects vehicles to inherit from p1
        randvehicles = randomvehicleselection(problem.k + 1)

        child = p1.copy()
        p1n, p1k = splitlist(p1)
        p2n, p2k = splitlist(p2)
        childn, childk = splitlist(child)
        # Remove routes not inherited from p1
        for i in range(problem.n * 2):
            if randvehicles[int(childk[i])] == 0:
                childn[i] = -1
        swath = findswath(childn)
        # Add values from p2 swath
        for i in swath:
            p2v = p2n[i]
            if p2v not in childn:  # If the value in p2 swath is not in the child
                pi = i
                while True:
                    p1v = p1n[pi]
                    ind = getindex(p1v, p2n)
                    if ind in swath:
                        pi = ind
                    else:
                        childn[pi] = p2v
                        childk[pi] = p1k[pi]
                        break

        #   Add remaining values from p2
        for i in range(len(p2n)):
            if childn[i] == -1:
                childn[i] = p2n[i]

        # Fix dropoffs
        for i in range(len(childn)):
            if childn[i] > problem.n:
                childk[i] = childk[getindex(childn[i] - problem.n, childn)]
        # transform child routes into output format
        result = np.concatenate([childn, childk])
        # add child to offpring
        offspring[0, m] = result
    return offspring


def pmxcrossover(problem, X):
    n_parents, n_matings, n_var = X.shape
    n_offspring = n_parents // 2

    # Initialize the offspring array
    offspring = np.full((n_offspring, n_matings, n_var), 0)

    for m in range(n_matings):
        p1, p2 = X[0, m], X[1, m]
        # Perform crossover operation
        # Selects vehicles to inherit from p1
        randvehicles = randomvehicleselection(problem.k + 1)

        child = p1.copy()
        p1n, p1k = splitlist(p1)
        p2n, p2k = splitlist(p2)
        childn, childk = splitlist(child)
        # Remove routes not inherited from p1
        for i in range(problem.n * 2):
            if randvehicles[int(childk[i])] == 0:
                childn[i] = -1
        swath = findswath(childn)
        # Add values from p2 swath
        for i in swath:
            p2v = p2n[i]
            car = p2k[i]
            if p2v not in childn:  # If the value in p2 swath is not in the child
                pi = i
                while True:
                    p1v = p1n[pi]
                    ind = getindex(p1v, p2n)
                    if ind in swath:
                        pi = ind
                    else:
                        childn[ind] = p2v

                        break

        #   Add remaining values from p2
        for i in range(len(p2n)):
            if childn[i] == -1:
                if p2n[i] > problem.n:
                    childn[i] = p2n[i]
                    childk[i] = p1k[i]

        childn = processdups(childn, problem.n)
        # transform child routes into output format
        result = np.concatenate([childn, childk])
        # add child to offpring
        offspring[0, m] = result

        if not containsall(childn, 2 * problem.n):
            offspring[0, m] = p1
        print(maptoroute(result, problem))
    return offspring


def containsall(lst, n):
    return all(i in lst for i in range(1, n + 1))


def processdups(lst, n):
    seen = set()
    for i, value in enumerate(lst):
        if value in seen:
            # This value is a duplicate, add n to it
            lst[i] += n
        else:
            seen.add(value)
    return lst


class PMXCrossover(Crossover):

    def __init__(self):
        super().__init__(2, 1)  # Specifies the number of parents and offspring for the crossover

    def _do(self, problem, X, **kwargs):
        return pmxcrossover(problem, X)
