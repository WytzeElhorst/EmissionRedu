import numpy as np
from pymoo.core.problem import ElementwiseProblem
import Darp

import numpy as np
from pymoo.core.problem import ElementwiseProblem


class DARP(ElementwiseProblem):

    def __init__(self, n, k, l, capacity, max_r_time, load, service_time, earliest_pickup, latest_dropoff, t_cost,
                 t_emission, t_time):
        super().__init__(n_var=(2 * n + 2) * (2 * n + 2) * k,
                         n_obj=3,
                         n_ieq_constr=0,
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
        self.REQ = np.array(range(0, 2 * n + 2))
        self.P = np.array(range(1, n + 1))
        self.D = np.array(range(n + 1, 2 * n + 1))

    def _evaluate(self, x, out, *args, **kwargs):
        REQ = self.REQ
        reqnum = len(REQ)
        # define extra parameters
        routematrix = np.zeros((self.k, reqnum, reqnum))
        for i in REQ:
            for j in REQ:
                for k in self.vehicles:
                    routematrix[k][i][j] = x[j + reqnum * i + reqnum * reqnum * k]  # map routes to 3D array
        routes = self.construct_routes(routematrix)
        s_time = self.routetimes(routes)
        c_load = self.vehicleload(routes)
        ride_time = self.ridedurations(s_time, routes)
        totaltime = self.routeduration(s_time)
        totaldur = self.totalduration(ride_time)
        wage = 16.15  # avarage US dial a ride wage is $17,50 =  €16,15 per hour
        wagecost = (totaltime / 60) * wage
        totalemission = sum(sum(sum(self.t_emission * routematrix)))
        totalfuel = totalemission / 2300  # 2.3kg CO2 = 1l fuel
        fuelcost = totalfuel * 2.11  # incl. carbon tax 1l fuel = €2.11
        # objective funtions
        f1 = wagecost + fuelcost  # operational costs: the € hourly wages + fuel costs
        f2 = totalemission / 1000  # emissions in KG CO2
        f3 = totaldur  # total customer ride duration in minutes

        # equality constraints
        h1 = self.check_constraints(routematrix, routes, s_time, c_load, ride_time)

        # inequality constraints
        g1 = 0

        out["F"] = [f1, f2, f3]
        out["H"] = [h1]

    # custom function for the equality constraints
    def check_constraints(self, routematrix, routes, s_time, c_load, ride_time):
        total = 0
        # print("Checking contraints.. \n")
        constraints = np.zeros(self.n_eq_constr)  # Initialize an array to store the constraint values

        # constraint1: each request is only served once
        c1violations = 0
        for i in self.P:
            sum_route = np.sum(routematrix[:, i, :])  # Sum the routes for each vehicle
            if sum_route != 1:
                c1violations += 1  # adds 1 if constraint is violated
                print("violation 1 detected")
                total += 1
        constraints[0] = c1violations

        # constraint2: each vehicle starts and ends at the depot:
        c2violations = 0
        for k in self.vehicles:
            if sum(routematrix[k, 0, :]) != 1:
                c2violations += 1
                print("violation 2a detected")
                total += 1
            if sum(routematrix[k, :, 2 * self.n + 1]) != 1:
                c2violations += 1
                print("violation 2b detected")
                total += 1
        constraints[1] = c2violations

        # constraint3: Ensure pick up and drop off is done by the same vehicle
        c3violations = 0
        for i in self.P:
            for k in self.vehicles:
                if sum(routematrix[k, i, :]) != sum(routematrix[k, i + self.n, :]):
                    c3violations += 1
                    print("violation 3 detected")
                    total += 1
        constraints[2] = c3violations

        # constraint4: Each non-depot location is traveled to and from once per vehicle
        c4violations = 0
        for i in range(1, 2 * self.n + 1):
            for k in self.vehicles:
                if sum(routematrix[k, :, i]) != sum(routematrix[k, i, :]):
                    c4violations += 1
                    print("violation 4 detected")
                    total += 1
        constraints[3] = c4violations

        # constraint5: total route duration can not exceed max route time
        c5violations = 0
        for k in self.vehicles:
            if s_time[k][len(s_time[k]) - 1] - s_time[k][0] > self.max_r_time[k]:
                c5violations += 1
                #print("violation 5 detected")
                total += 1
        constraints[4] = c5violations

        # constraint6: start time for each request is between earliest pickup and latest dropoff
        c6violations = 0
        for k in self.vehicles:
            for i in range(len(routes[k])):
                if self.earliest_pickup[routes[k][i]] > s_time[k][i] or s_time[k][i] > self.latest_dropoff[routes[k][i]]:
                    c6violations += 1
                    #print("violation 6 detected")
                    total += 1
        constraints[5] = c6violations

        # constraint7: time from pick up to drop off < user ride time and does not exceed max ride time
        c7violations = 0
        for k in self.vehicles:
            for i in range(len(ride_time[k])):
                if ride_time[k][i] > self.l:
                    c7violations += 1
                    #print("violation 7 detected")
                    total += 1
        constraints[6] = c7violations

        # constraint8: current load does not exceed max load
        c8violations = 0
        for k in self.vehicles:
            for i in range(len(routes[k])):
                if c_load[k][i] > min(self.capacity[k], self.capacity[k] + self.load[routes[k][i]]):
                    c8violations += 1
                    #print("violation 8 detected")
                    total += 1
        constraints[7] = c8violations

       # if total == 0:
       #     print("feasible", routes)
        return constraints

    def construct_routes(self, routematrix):
        # print("constructing routes \n")
        n = self.n
        routes = list()
        for k in self.vehicles:
            route = [0]
            i = 0
            while i != 2 * n + 1:
                i = np.where(routematrix[k, i, :] == 1)[0][0]
                route.append(i)
            routes.append(route)
        return routes

    # calculates at which time each vehicle serves each request
    def routetimes(self, routes):
        # print("Calculating route times \n")
        s_time = list()
        for k in range(len(routes)):
            route = []
            destination = routes[k][1]
            s1 = max(self.earliest_pickup[destination], self.t_time[
                0, destination])  # arrive at earliest pickup of first request if possible, else arrive as early as possible
            s0 = max(s1 - self.t_time[0, destination], 0)  # calculate start time at depot
            route.append(s0)
            route.append(s1)
            for i in range(2, len(routes[k])):
                snew = max(
                    route[i - 1] + self.service_time[routes[k][i - 1]] + self.t_time[routes[k][i - 1], routes[k][i]],
                    self.earliest_pickup[routes[k][i]])  # satisfies constraint 6
                route.append(snew)
            s_time.append(route)
        return s_time

    # calculate total route duration for wages
    def routeduration(self, s_time):
        totaltime = 0
        for k in range(len(s_time)):
            if len(s_time[k]) > 2:
                totaltime += s_time[k][len(s_time[k]) - 1] - s_time[k][0]  # add total route duration for each car
        return totaltime

    # calculate total customer ride time duration
    def totalduration(self, ride_time):
        totaldur = 0
        for k in range(len(ride_time)):
            for i in range(len(ride_time[k])):
                totaldur += ride_time[k][i]
        return totaldur

    # calculates the load of each vehicle at each request
    def vehicleload(self, routes):
        # rint("Calculating vehicle loads \n")
        c_load = list()
        for k in range(len(routes)):
            load = []
            prevload = 0
            for i in range(len(routes[k])):
                curload = prevload + self.load[routes[k][i]]  # current load is previous load + load of new request
                load.append(curload)
                prevload = curload
            c_load.append(load)
        return c_load

    def ridedurations(self, s_time, routes):
        # print("Calculating ride durations \n")
        ride_time = []
        for k in range(len(s_time)):
            durations = []
            if len(s_time[k]) > 2:
                for i in range(1, int(len(s_time[k]))):
                    if routes[k][i] <= self.n:
                        pickup = s_time[k][i]
                        dropoff = s_time[k][np.where(routes[k] == (routes[k][i] + self.n))[0][0]]
                        durations.append(dropoff - (pickup + self.service_time[
                            routes[k][i]]))  # customer ride duration is time between pickup and drop off
            ride_time.append(durations)
        return ride_time

    def maptomatrix(self, X):
        REQ = self.REQ
        reqnum = len(self.REQ)
        routematrix = np.zeros((self.k, reqnum, reqnum))
        for i in REQ:
            for j in REQ:
                for k in self.vehicles:
                    routematrix[k][i][j] = X[j + reqnum * i + reqnum * reqnum * k]  # map routes to 3D array
        return routematrix

    def routetomatrix(self, routes):
        childmatrix = np.zeros((self.k, len(self.REQ), len(self.REQ)))

        # generate matrix from routes for child
        for k in range(self.k):
            for i in range(len(routes[k]) - 1):
                childmatrix[k][routes[k][i]][routes[k][i + 1]] = 1
        return childmatrix

    def matrixtooutput(self, routematrix):
        output = np.zeros((2 * self.n + 2) * (2 * self.n + 2) * self.k, dtype=bool)
        for i in self.REQ:
            for j in self.REQ:
                for k in self.vehicles:
                    output[j + len(self.REQ) * i + len(self.REQ) * len(self.REQ) * k] = routematrix[k][i][
                                                                                            j] == 1  # map routes to 3D array
        return output
