from minizinc import Instance, Model, Solver
import Darp

DARP = Model("./Models/Darp7_WALimit€.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gurobi")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(gecode, DARP)

# Read data
Darpinstance = Darp.readfile("Data/5km8hours3n.txt", 3)

# Write data into minizinc dzn file
Darpinstance.writefile("output1k05082n")


def rundarp():
    # Add the data to the minizinc instance
    instance["n"] = Darpinstance.n
    instance["K"] = Darpinstance.k
    instance["L"] = Darpinstance.L
    instance["capacity"] = Darpinstance.capacity
    instance["max_r_time"] = Darpinstance.max_r_time
    instance["load"] = Darpinstance.load
    instance["service_time"] = Darpinstance.service_time
    instance["earliest_pickup"] = Darpinstance.earliest_pickup
    instance["latest_dropoff"] = Darpinstance.latest_dropoff
    instance["t_cost"] = Darpinstance.t_cost
    instance["t_time"] = Darpinstance.t_time
    instance["t_emission"] = Darpinstance.t_emis

    result = instance.solve()

    # Output the array routes
    print(result["ride_time"])

    f = open("./Results/Output.txt", "w")
    f.write("number of requests: " + Darpinstance.n + "\n")
    f.write("number of vehicles: " + Darpinstance.K + "\n")
    f.write("max route duration: " + Darpinstance.L + "\n")
    f.write("Total emission: " + str(sum(result["routes"] * Darpinstance.t_emission)) + "KG Co2 \n")
    f.write("Operational costs: €" + str(sum(result["routes"] * Darpinstance.t_cost)) + "\n")