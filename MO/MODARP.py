import numpy as np
from pymoo.core.problem import Problem


import numpy as np
from pymoo.core.problem import ElementwiseProblem


class DARP(Problem):

    def __init__(self, n, k, l, capacity, max_r_time, load, service_time, earliest_pickup, latest_dropoff, t_cost, t_emission, t_time):
        super().__init__(n_var=(2*n+1)*(2*n+1)*k,
                         n_obj=3,
                         n_ieq_constr=9,
                         n_eq_constr=8,
                         xl=np.array([0]),
                         xu=np.array([1]))
        self.n = n
        self.k = k
        self.l = l
        self.capacity = capacity
        self.max_r_time = max_r_time
        self.load = load
        self.service_time = service_time
        self.earliest_pickup = earliest_pickup
        self.latest_dropoff = latest_dropoff
        self.t_cost = t_cost
        self.t_emission = t_emission
        self.t_time = t_time
        self.vehicles = np.array(range(0, k))
        self.REQ = np.array(range(0, 2*n+2))
        self.P = np.array(range(1, n+1))
        self.D = np.array(range(n+1, 2*n+1))




    def _evaluate(self, x, out, *args, **kwargs):
        REQ = self.REQ
        reqnum = len(REQ)

        # define extra parameters
        routematrix = np.zeros(reqnum, reqnum, self.k)
        for i in range(REQ):
            for j in range(REQ):
                for k in self.vehicles:
                    routematrix[i][j][k] = x[1*i + reqnum*j + reqnum*reqnum*k] #map routes to 3D array

        s_time = np.zeros(reqnum, self.k)
        routes = list()
        for k in self.vehicles:
            route = list([0]) # add depot
            for i in REQ:
                if routes
                s_time[i][k] =
        c_load = np.zeros(reqnum, len(self.vehicles))
        ride_time = np.zeros(len(self.REQ), len(self.vehicles))

        # objective funtions
        f1 = sum(self.t_emission*routes)
        f2 = sum(self.t_cost*routes)
        f3 = sum(ride_time*routes)

        # equality constraints
        h1 = 0;

        # inequality constraints
        g1 = 0;

        out["F"] = [f1, f2, f3]
        out["G"] = [g1]
        out["H"] = [h1]

    def construct_routes(self, routematrix):
        n = self.n
        routes = []
        for k in range(n):
            route = []
            for i in range(2 * n + 1):
                if X[i][k] == 1:
                    route.append(i)
            routes.append(route)
        return routes
