import numpy as np
from pymoo.core.problem import Problem


class DARP(Problem):
    def __init__(self, req, n, capacity, c, t, e, tmax):
        super().__init__(n_var=2 * n + 1, n_obj=2, n_constr=0, xl=0, xu=1)
        self.req = req
        self.n = n
        self.capacity = capacity
        self.costmatrix = c
        self.travelmatrix = t
        self.emissionmatrix = e
        self.tmax = tmax

    def _evaluate(self, X, out, *args, **kwargs):
        routes = self.construct_routes(X)
        total_cost = self.calculate_total_cost(routes)
        out["F"] = total_cost

        # Add feasibility checks and penalize infeasible solutions
        for k in range(self.n):
            if not self.is_feasible(routes[k]):
                out["F"] += 1e6  # Penalize infeasible solutions

    # Return True if the route is feasible, False otherwise
    def is_feasible(self, route):
        total_demand = sum(self.req[node][2] for node in route[1:-1])       # Check if the total demand in the route exceeds the vehicle capacity
        return total_demand <= self.Q

    def construct_routes(self, X):
        n = self.n
        routes = []
        for k in range(n):
            route = []
            for i in range(2 * n + 1):
                if X[i][k] == 1:
                    route.append(i)
            routes.append(route)
        return routes

    # calculate the total cost
    def calculate_total_cost(self, routes):
        total_cost = 0
        for r in routes:
            vehicle_cost = 0
            prev_node = 0  # depot
            for node in r:
                vehicle_cost += self.c[prev_node][node]
                prev_node = node
            vehicle_cost += self.c[prev_node][0]
            total_cost += vehicle_cost
        return total_cost

    # calculate the total emissions
    def calculate_total_emission(self, routes):
        total_emission = 0
        for r in routes:
            vehicle_emission = 0
            prev_node = 0  # depot
            for node in r:
                vehicle_emission += self.emissionmatrix[prev_node][node]
                prev_node = node
            vehicle_emission += self.emissionmatrix[prev_node][0]
            total_emission += vehicle_emission
        return total_emission
