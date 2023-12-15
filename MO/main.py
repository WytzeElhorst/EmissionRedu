import os

import numpy as np
import Darp
from HeuristicSampling import HeuristicSampling
from SmartSampling import SmartSampling
from PMXCrossover import PMXCrossover
from SmartCrossover import SmartCrossover
from CustomMutation import CustomMutation
from SmartMutation import SmartMutation
from SmartRepair import SmartRepair
from MODARP import DARP
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
import timeit

# Read data
start = timeit.default_timer()
bigcar = 8
medcar = 8
smallcar = 8
vehiclenum = bigcar + medcar + smallcar
scenario = "moderate"
requestnum = 50
generations = 2000
smart = 100
filename = "GA"
guided = True
if guided:
    filename = "GGA"
if smart > 0:
    if smart < 100:
        filename += "h"
    else:
        filename += "+"

darp = Darp.readfile("../Data/" + scenario + "/" + scenario + str(requestnum) + ".txt", bigcar, medcar, smallcar)
darp.writefile("../Data/" + scenario + "/minizinc/" + scenario + str(requestnum) + 'n' + str(vehiclenum))
f = open("../Data/" + scenario + "/output/" + filename + str(requestnum) + 'n' + str(vehiclenum) + ".csv", "w")
moDarp = DARP(darp.n, darp.k, darp.L, darp.capacity, darp.max_r_time, darp.load, darp.service_time,
              darp.earliest_pickup, darp.latest_dropoff, darp.t_cost, darp.t_emis, darp.t_time)

# Run NSGA-III algorithm
mut = CustomMutation()
cross = SmartCrossover(smart)
if guided:
    mut = SmartMutation()

algorithm = NSGA3(
        pop_size=500,
        sampling=SmartSampling(500),
        crossover=cross,
        mutation=mut,
        repair=SmartRepair(),
        ref_dirs=get_reference_directions("das-dennis", 3, n_partitions=24),
        n_offsprings=100
    )

res = minimize(moDarp,
               algorithm,
               termination=('n_gen', generations),
               verbose=True)

# Retrieve solution and objective values
X = res.X
F = res.F
stop = timeit.default_timer()
avaragecost = 0
avarageemi = 0
avaragewait = 0
maxcost = 0
maxemi = 0
maxwait = 0
mincost = 100000
minemi = 100000
minwait = 100000
for i in range(len(F)):
    print("Operational costs: €", round(res.F[i][0], 2))
    print("Total Emission: ", res.F[i][1], "kg CO2")
    print("Waiting time: ", res.F[i][2], " minutes")
    data = f"{round(res.F[i][0], 2)},{res.F[i][1]},{res.F[i][2]}"
    f.write(data)
    f.write("\n")
    avaragecost += res.F[i][0]
    avarageemi += res.F[i][1]
    avaragewait += res.F[i][2]
    if maxcost < res.F[i][0]:
        maxcost = res.F[i][0]
    if maxemi < res.F[i][1]:
        maxemi = res.F[i][1]
    if maxwait < res.F[i][2]:
        maxwait = res.F[i][2]
    if mincost > res.F[i][0]:
        mincost = res.F[i][0]
    if minemi > res.F[i][1]:
        minemi = res.F[i][1]
    if minwait > res.F[i][2]:
        minwait = res.F[i][2]
    print(" ")

print("Avarage operational cost: €", round(avaragecost / len(F), 2))
print("Total Emission: ", avarageemi / len(F), "kg CO2")
print("Waiting time: ", avaragewait / len(F), " minutes")
print(" ")

print("Max operational cost: €", round(maxcost, 2))
print("Max Total Emission: ", maxemi, "kg CO2")
print("Max Waiting time: ", maxwait, " minutes")
print(" ")

print("Min operational cost: €", round(mincost, 2))
print("Min Total Emission: ", minemi, "kg CO2")
print("Min Waiting time: ", minwait, " minutes")
print(" ")

# calculate best overal solution
bestsolution = 10000
index = 0
for i in range(len(F)):
    score1 = (res.F[i][0] / mincost) - 1
    score2 = (res.F[i][1] / minemi) - 1
    score3 = (res.F[i][2] / minwait) - 1
    score = (score1 + score2 + score3) / 3
    if score < bestsolution:
        bestsolution = score
        index = i

print("Best solution's operational cost: €", round(res.F[index][0], 2))
print("Best solution's Total Emission: ", res.F[index][1], "kg CO2")
print("Best solution's Waiting time: ", res.F[index][2], " minutes")
print("Best solution score: ", bestsolution)
print("Number of solutions: ", len(res.F))
print("Runtime: ", stop - start)

# 2D pareto front using colour mapping
ob1v = F[:, 0]
ob2v = F[:, 1]
ob3v = F[:, 2]
plt.figure(figsize=(8, 6))
scatter = plt.scatter(ob1v, ob3v, c=ob2v, cmap='Greys', marker='o', alpha=0.7)
cbar = plt.colorbar(scatter, label='Emission', orientation='vertical')
plt.xlabel('Operational cost')
plt.ylabel("Ride Duration")
plt.title('Pareto front with colour intensity for Emission')

plt.show()

# 3D pareto front
# Scatter().add(res.F).show()
