import numpy as np
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from SimpleTest import MyProblem

# Example data
num_requests = 5
num_vehicles = 3
requests = np.array([10, 8, 5, 6, 7])
vehicles = np.array([20, 15, 25])
testarray = np.array([1, 2, 3])

problem = MyProblem(testarray)

# Run NSGA-III algorithm
algorithm = NSGA3(
    pop_size=100,
    ref_dirs=get_reference_directions("das-dennis", 2, n_partitions=12),
    n_offsprings=50
)

res = minimize(problem,
               algorithm,
               termination=('n_gen', 100),
               seed=1,
               verbose=True)

# Retrieve solution and objective values
X = res.X
F = res.F

# Show design space
xl, xu = problem.bounds()
plt.figure(figsize=(7, 5))
plt.scatter(X[:, 0], X[:, 1], s=30, facecolors='none', edgecolors='r')
plt.xlim(xl[0], xu[0])
plt.ylim(xl[1], xu[1])
plt.title("Design Space")
plt.show()

plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
plt.title("Objective Space")
plt.show()
