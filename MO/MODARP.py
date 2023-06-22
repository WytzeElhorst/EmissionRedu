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
                    routematrix[k][i][j] = x[j + reqnum*i + reqnum*reqnum*k]    # map routes to 3D array
        routes = self.construct_routes(routematrix)
        s_time = self.routetimes(routes)
        c_load = self.vehicleload(routes)
        ride_time = np.zeros(len(self.REQ), len(self.vehicles))

        # objective funtions
        f1 = sum(self.t_emission*routes)
        f2 = sum(self.t_cost*routes)
        f3 = sum(ride_time*routes)

        # equality constraints
        h1 = self.check_constraints(x)

        # inequality constraints
        g1 = 0

        out["F"] = [f1, f2, f3]
        out["G"] = [g1]
        out["H"] = [h1]

    # custom function for the equality constraints
    def check_constraints(self, x, *args, **kwargs):
        constraints = np.zeros(len(self.n_eq_constr))  # Initialize an array to store the constraint values


        # constraint1: each request is only served once
        c1violations = 0
        for i in self.P:
            sum_route = np.sum(x[:, i, :])  # Sum the routes for each vehicle
            if sum(sum_route == 1) != 1:
                c1violations += 1   # adds 1 if constraint is violated
        constraints[0] = c1violations

        # constraint2: each vehicle starts and ends at the depot:
        c2violations = 0
        for k in self.vehicles:
            if sum(x[k,0,:]) != 1:
                c2violations += 1
            if sum(x[k,:,2*self.n+1]) != 1:
                c2violations += 1
        constraints[1] = c2violations

        # constraint3: Ensure pick up and drop off is done by the same vehicle
        c3violations = 0
        for i in self.P:
            for k in self.vehicles:
                if sum(x[k,i,:]) != sum(x[k,i+self.n,:]):
                    c3violations += 1
        constraints[2] = c3violations

        # constraint4: Each non-depot location is traveled to and from once per vehicle
        c4violations = 0
        for i in self.P + self.D:
            for k in self.vehicles:
                if sum(x[k,:,i]) != sum(x[k,i,:]):
                    c4violations += 1
        constraints[3] = c4violations

        return constraints

    def construct_routes(self, routematrix):
        n = self.n
        routes = list()
        for k in range(self.k):
            route = [0]
            i = 0
            while i != 2*n+1:
                i = np.where(routematrix[:,i,k] == 1)[0][0]
                route.append(i)
            routes.append(route)
        return routes

    # calculates at which time each vehicle serves each request
    def routetimes(self, routes):
        s_time = list()
        for k in routes:
            route = []
            destination = routes[k][1]
            s1 = max(self.earliest_pickup[destination], self.t_time[k, 0, destination])    # arrive at earliest pickup of first request if possible, else arrive as early as possible
            s0 = max(s1 - self.t_time[k, 0, destination], 0)    # calculate start time at depot
            route.append(s0)
            route.append(s1)
            for i in range(2, len(routes(k))):
                snew = max(route[k][i-1] + self.service_time[i] + self.t_time[k, i-1, i], self.earliest_pickup[i])
                route.append(snew)
            s_time.append(route)
        return s_time

    # calculates the load of each vehicle at each request
    def vehicleload(self, routes):
        c_load = list()
        for k in routes:
            load = []
            prevload = 0
            for i in routes[k]:
                curload = prevload + self.load(routes[k][i])    # current load is previous load + load of new request
                load.append(curload)
                prevload = curload
        return c_load

    def ridedurations(self, s_time):
        ride_time = list()
        for k in s_time:
            durations = []
            for i in self.P:
                durations.append(s_time[k][i + self.n] - s_time[k][i])  # customer ride duration is time between pickup and drop off
            ride_time.append(durations)
        return ride_time


# for testing
def construct_routes(routematrix):
    n = 2
    routes = list()
    for k in range(2):
        route = [0]
        i = 0
        while i != 2*n+1:
            i = np.where(routematrix[k,i,:] == 1)[0][0]
            route.append(i)
        routes.append(route)
    return routes


testroute = np.zeros((2, 6, 6))
testroute[0, 0, 2] = 1
testroute[0, 2, 4] = 1
testroute[0, 4, 5] = 1
testroute[1, 0, 1] = 1
testroute[1, 1, 3] = 1
testroute[1, 3, 5] = 1
print(sum(sum(testroute[:,1,:]) == 1))
print(construct_routes(testroute))
