import math
import random

import numpy as np

import Vehicle


def readfile(filepath, bcar, mcar, scar):
    n = 0  # number of requests
    random.seed(10) #set seed so random loads are the same between runs
    pickuploc = list()
    dropoffloc = list()
    DRT = list()
    LRT = list()
    pickuptime = list()
    with open(filepath) as file:
        for line in file:
            if n == 0:
                tempList = line.rstrip().split('\t')
                depot = [int(float(tempList[1])), int(float(tempList[2]))]
                n += 1
            else:
                tempList = line.rstrip().split('\t')
                pickup = [int(tempList[1]), int(tempList[2])]
                dropoff = [int(tempList[3]), int(tempList[4])]
                pickuploc.append(pickup)
                dropoffloc.append(dropoff)
                DRT.append(int(tempList[5]))
                LRT.append(int(tempList[6]))
                pickuptime.append(int(tempList[7]))
                n += 1
    n -= 1
    # add all requests to a single list
    allrequests = [depot] + pickuploc + dropoffloc + [depot]


    # fixed parameters
    vehiclenum = bcar + mcar + scar
    K = vehiclenum  # number of available vehicles
    L = 480  # Max ride time

    # add different types of vehicles
    vehiclelist = list()
    for q in range(scar):
        vehiclelist.append(Vehicle.Vehicle(0))
    for q in range(mcar):
        vehiclelist.append(Vehicle.Vehicle(1))
    for q in range(bcar):
        vehiclelist.append(Vehicle.Vehicle(2))

    # list parameters:
    vehicles = list()
    vehiclecap = list()
    maxroutedur = list()
    for i in range(K):
        vehicles.append(i)
        vehiclecap.append(vehiclelist[i].capacity())
        maxroutedur.append(480)

    REQ = [0]
    P = list()
    D = list()
    load = [0]  # 0 at depot
    service_time = [0]  # 0 at depot
    earliest_pickup = [0]  # 0 at depot
    latest_dropoff = [1440]  # 1440 at depot (24H)
    for i in range(n):  # pickups
        REQ.append(i + 1)
        P.append(i + 1)
        load.append(random.randint(1, 1))  # add a load
        service_time.append(5)  # 5 minutes service time
        earliest_pickup.append(pickuptime[i])
        latest_dropoff.append(pickuptime[i] + LRT[i])

    for i in range(n):  # drop offs
        REQ.append(n + i + 1)
        D.append(n + i + 1)
        load.append(load[i + 1] * -1)  # each request only has load 1 currently
        service_time.append(5)  # 5 minutes service time
        earliest_pickup.append(pickuptime[i])
        latest_dropoff.append(pickuptime[i] + LRT[i])

    REQ.append(2 * n + 1)
    load.append(0)
    service_time.append(0)
    earliest_pickup.append(0)
    latest_dropoff.append(1440)  # 1440 at depot (24H)

    # matrix parameters
    # At 60km/h 1 km = 1 minute
    distancematrix = list()
    for i in range(len(allrequests)):
        distancerow = list()
        for j in range(len(allrequests)):
            distance = math.sqrt((int(allrequests[i][0]) - int(allrequests[j][0])) ** 2 + (
                        int(allrequests[i][1]) - int(allrequests[j][1])) ** 2)
            distancerow.append(int(distance))
        distancematrix.append(distancerow)

    # cost matrix
    # €30/h = €0,50 per minute
    costmatrix = list()
    for k in range(K):
        costsheet = list()
        for i in range(len(allrequests)):
            costrow = list()
            for j in range(len(allrequests)):
                cost = (distancematrix[i][j] * 50) + (
                            distancematrix[i][j] * 182 * vehiclelist[k].emission())  # wages + fuel cost
                costrow.append(int(cost))
            costsheet.append(costrow)
        costmatrix.append(costsheet)

    # Emission matrix
    emismatrix = list()
    for k in range(K):
        emissheet = list()
        for i in range(len(allrequests)):
            emisrow = list()
            for j in range(len(allrequests)):
                emis = (distancematrix[i][j] * 2300 * vehiclelist[k].emission())  # emission in grams CO2
                emisrow.append(int(emis))
            emissheet.append(emisrow)
        emismatrix.append(emissheet)

    return Darp(n, K, L, np.array(vehiclecap), np.array(maxroutedur), np.array(load), np.array(service_time),
                np.array(earliest_pickup), np.array(latest_dropoff), np.array(distancematrix), np.array(costmatrix),
                np.array(emismatrix))


class Darp:
    def __init__(self, n, k, L, cap, maxr, load, servtime, earl, lated, t_time, t_cost, t_emis):
        self.n = n
        self.k = k
        self.L = L
        self.capacity = cap
        self.max_r_time = maxr
        self.load = load
        self.service_time = servtime
        self.earliest_pickup = earl
        self.latest_dropoff = lated
        self.t_time = t_time
        self.t_cost = t_cost
        self.t_emis = t_emis

        self.vehicles = np.array(range(0, k))
        self.REQ = np.array(range(0, 2 * n + 2))
        self.P = np.array(range(1, n + 1))
        self.D = np.array(range(n + 1, 2 * n + 1))

    # Write data into minizinc dzn file

    def writefile(self, filename):
        f = open(filename + ".dzn", "w")
        f.write("n = " + str(self.n) + ";\n")
        f.write("K = " + str(self.k) + ";\n")
        f.write("L = " + str(self.L) + ";\n")

        f.write("capacity = array1d(0.." + str(len(self.capacity) - 1) + ",[")  # vehiclecapacity
        for i in range(len(self.capacity)):
            if i < len(self.capacity) - 1:
                f.write(str(self.capacity[i]) + ", ")
            else:
                f.write(str(self.capacity[i]) + "]);\n")

        f.write("max_r_time = array1d(0.." + str(len(self.max_r_time) - 1) + ",[")  # maxridetime
        for i in range(len(self.max_r_time)):
            if i < len(self.max_r_time) - 1:
                f.write(str(self.max_r_time[i]) + ", ")
            else:
                f.write(str(self.max_r_time[i]) + "]);\n")

        f.write("load = array1d(0.." + str(len(self.load) - 1) + ",[")  # load
        for i in range(len(self.load)):
            if i < len(self.load) - 1:
                f.write(str(self.load[i]) + ", ")
            else:
                f.write(str(self.load[i]) + "]);\n")

        f.write("service_time = array1d(0.." + str(len(self.service_time) - 1) + ",[")  # servicetime
        for i in range(len(self.service_time)):
            if i < len(self.service_time) - 1:
                f.write(str(self.service_time[i]) + ", ")
            else:
                f.write(str(self.service_time[i]) + "]);\n")

        f.write("earliest_pickup = array1d(0.." + str(len(self.earliest_pickup) - 1) + ",[")  # earliest pickup
        for i in range(len(self.earliest_pickup)):
            if i < len(self.earliest_pickup) - 1:
                f.write(str(self.earliest_pickup[i]) + ", ")
            else:
                f.write(str(self.earliest_pickup[i]) + "]);\n")

        f.write("latest_dropoff = array1d(0.." + str(len(self.latest_dropoff) - 1) + ",[")  # latest dropoff
        for i in range(len(self.latest_dropoff)):
            if i < len(self.latest_dropoff) - 1:
                f.write(str(self.latest_dropoff[i]) + ", ")
            else:
                f.write(str(self.latest_dropoff[i]) + "]);\n")

        f.write("t_time = array2d(0.." + str(2 * self.n + 1) + ",0.." + str(2 * self.n + 1) + ",[")  # distance matrix
        for i in range(len(self.t_time)):
            for j in range(len(self.t_time[i])):
                f.write(str(self.t_time[i][j]))
                if i < len(self.t_time) - 1 or j < len(self.t_time) - 1:
                    f.write(", ")
        f.write("]);\n")
        f.write("t_cost = array3d(0.." + str(2 * self.n + 1) + ",0.." + str(2 * self.n + 1) + ",0.." + str(
            self.k - 1) + ",[")  # travel cost matrix
        for car in range(len(self.t_cost)):
            for i in range(len(self.t_cost[car])):
                for j in range(len(self.t_cost[car][i])):
                    f.write(str(self.t_cost[car][i][j]))
                    if i < len(self.t_cost[car]) - 1 or j < len(self.t_cost[car]) - 1 or car < len(self.t_cost) - 1:
                        f.write(", ")
        f.write("]);\n")
        f.write("t_emission = array3d(0.." + str(self.k - 1) + ",0.." + str(2 * self.n + 1) + ",0.." + str(
            2 * self.n + 1) + ",[")  # emission matrix
        for car in range(len(self.t_emis)):
            for i in range(len(self.t_emis[car])):
                for j in range(len(self.t_emis[car][i])):
                    f.write(str(self.t_emis[car][i][j]))
                    if i < len(self.t_emis[car]) - 1 or j < len(self.t_emis[car]) - 1 or car < len(self.t_emis) - 1:
                        f.write(", ")
        f.write("]);\n")
        f.close()
