from minizinc import Instance, Model, Solver
from scipy.spatial import distance

# Load n-Queens model from file
nqueens = Model("./Models/Dial-A-Ride.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(gecode, nqueens)

# Read data
n = 0   # number of requests
pickuploc = list()
dropoffloc = list()
DRT = list()
LRT = list()
pickuptime = list()
directtraveltime = list()
with open("./Data/growth_SD12hrs_SA10km_c50.txt") as file:
    for line in file:
        if n == 0:
            tempList = line.rstrip().split('\t')
            depot = (tempList[1], tempList[2])
        else:
            tempList = line.rstrip().split('\t')
            pickup = (tempList[1], tempList[2])
            dropoff = (tempList[3], tempList[4])
            pickuploc.append(pickup)
            dropoffloc.append(dropoff)
            DRT.append(tempList[5])
            LRT.append(tempList[6])
            pickuptime.append(tempList[7])
            n += 1


# fixed parameters
k = 5   # number of available vehicles
L = 300  # Max ride time
vehiclecap = [3, 3, 3, 3, 3]
maxroutedur = [300, 300, 300, 300, 300]
load = [0]  # 0 at depot
service_time = [0]  #0 at depot
latest_dropoff = list()

# list parameters:
for i in range(n):  # pickups
    load.append(1)  # each request only has load 1 currently
    service_time.append(5)  # hardcoded 5 minutes service time
    latest_dropoff.append(pickuptime[i] + LRT[i])

for i in range(n):  #dropoffs
    load.append(1)  # each request only has load 1 currently
    service_time.append(5)  # hardcoded 5 minutes service time
    latest_dropoff.append(pickuptime[i] + LRT[i])

# matrix parameters
distancematrix = list[range(n)]
travelmatrix = list[range(n)]
costmatrix = list[range(n)]
for i in range(n):
    distancematrix[i] = list[range(n)]
    for j in range(n):
        distancematrix[i][j] = distance.euclidean()
instance["n"] = 4
result = instance.solve()
# Output the array q
print(result["q"])
