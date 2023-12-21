import csv

import matplotlib
import numpy as np
from matplotlib import pyplot as plt


def showpareto(resultlist):
    ob1v = []
    ob2v = []
    ob3v = []
    for i in resultlist:
        ob1v.append(i.cost)
        ob2v.append(i.emission)
        ob3v.append(i.wait)

    rcmap = matplotlib.cm.get_cmap('copper_r')
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(ob1v, ob3v, c=ob2v, cmap=rcmap, marker='o', alpha=0.7)
    cbar = plt.colorbar(scatter, label='Emission', orientation='vertical')
    plt.xlabel('Operational cost')
    plt.ylabel("Ride Duration")
    plt.title('Pareto front with colour intensity for Emission')
    plt.show()


def get_best_solution(resultlist):
    weights = (0.2, 1, 0.2)
    best_solution = None
    best_score = float('inf')  # Initialize with a large value

    for result in resultlist:
        # Calculate the weighted sum of objectives
        score = weights[0] * result.cost + weights[1] * result.emission + weights[2] * result.wait

        # Update the best solution if the current score is better
        if score < best_score:
            best_solution = result
            best_score = score

    return best_solution


def get_score(result):
    weights = (0.2, 1, 0.2)
    score = weights[0] * result.cost + weights[1] * result.emission + weights[2] * result.wait
    return score


def calculate_spread(pareto_front):
    if len(pareto_front) < 2:
        return 0.0  # Spread is zero if there are fewer than two solutions

    # Extract objective values
    objectives = np.array([[result.cost, result.emission, result.wait] for result in pareto_front])

    # Calculate the range for each objective
    objective_ranges = np.max(objectives, axis=0) - np.min(objectives, axis=0)

    # Calculate spread for each objective
    spread_per_objective = objective_ranges / (1.0 + objective_ranges)

    # Calculate overall spread (average of spreads for each objective)
    s_metric = np.mean(spread_per_objective)

    return s_metric


def calculate_delta(pareto_front):
    if len(pareto_front) < 2:
        return 0.0  # Delta is zero if there are fewer than two solutions

    # Extract objective values
    objectives = np.array([[result.cost, result.emission, result.wait] for result in pareto_front])

    # Calculate the Euclidean distance between consecutive solutions
    delta_values = np.sqrt(np.sum(np.diff(objectives, axis=0) ** 2, axis=1))

    # Calculate the average Delta
    delta_metric = np.mean(delta_values)

    return delta_metric


def read_csv(file_path):
    data_list = []

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            rowdata = []
            try:
                # Convert each element in the row to a float and append to the list
                for item in row:
                    rowdata.append(item)
                data_list.append(rowdata)
            except ValueError as e:
                print(f"Error parsing row {row}: {e}")

    return data_list


def plot_2d_line_graph(data):
    x_values, y_values = zip(*data)

    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.title('2D Line Graph')
    plt.grid(True)
    plt.show()


def plot_2_graphs(data, data2):
    x_values, y_values = zip(*data)
    x2_values, y2_values = zip(*data2)
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.plot(x2_values, y2_values, marker='o', linestyle='-')
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.title('2D Line Graph')
    plt.grid(True)
    plt.show()


class MOresult:
    def __init__(self, cost, emission, wait):
        self.cost = cost
        self.emission = emission
        self.wait = wait

    def __str__(self):
        return f"Cost: {self.cost}, Emission: {self.emission}, Wait: {self.wait}"

    @classmethod
    def readfile(cls, file_path):
        results = []

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    values = line.strip().split(',')
                    if len(values) == 3:
                        cost, emission, wait = map(float, values)
                        mo_result = cls(cost, emission, wait)
                        results.append(mo_result)
                    else:
                        print(f"Skipping invalid line: {line}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")

        return results

    @staticmethod
    # rounds a value to 1 decimal for duplicate checking
    def roundone(value):
        return round(value, 1)

    @classmethod
    def remove_duplicates(cls, resultlist):
        unique_results = []
        seen_values = set()

        for result in resultlist:
            rounded_cost = cls.roundone(result.cost)
            rounded_emission = cls.roundone(result.emission)
            rounded_wait = cls.roundone(result.wait)

            # Create a tuple of rounded values to check for duplicates
            value_tuple = (rounded_cost, rounded_emission, rounded_wait)

            if value_tuple not in seen_values:
                unique_results.append(result)
                seen_values.add(value_tuple)

        return unique_results

    @classmethod
    def non_dominated(cls, list1, list2):
        non_dominated = []
        list1dom = 0
        list2dom = 0

        for result1 in list1:
            if not cls.is_dominated(result1, list2):
                non_dominated.append(result1)
            else:
                list1dom += 1
        for result2 in list2:
            if not cls.is_dominated(result2, list1):
                non_dominated.append(result2)
            else:
                list2dom += 1
        print("Pareto front contains ", len(list1) - list1dom, "non-dominated solutions from the GA")
        print("Pareto front contains ", len(list2) - list2dom, "non-dominated solutions from the MIP")
        print(list1dom, " results from GA pareto are dominated")
        print(list2dom, " results from MIP pareto are dominated")
        return non_dominated

    @classmethod
    def non_dominated_origins(cls, list1, list2):
        non_dominated_ga = []
        non_dominated_mip = []
        list1dom = 0
        list2dom = 0

        for result1 in list1:
            if not cls.is_dominated(result1, list2):
                non_dominated_ga.append(result1)
            else:
                list1dom += 1
        for result2 in list2:
            if not cls.is_dominated(result2, list1):
                non_dominated_mip.append(result2)
            else:
                list2dom += 1
        print("Pareto front contains ", len(list1) - list1dom, "non-dominated solutions from the GA")
        print("Pareto front contains ", len(list2) - list2dom, "non-dominated solutions from the MIP")
        print(list1dom, " results from GA pareto are dominated")
        print(list2dom, " results from MIP pareto are dominated")
        return non_dominated_ga, non_dominated_mip

    @classmethod
    def show2paretos(cls, list1, list2):
        ob1v = []
        ob2v = []
        ob3v = []
        for i in list1:
            ob1v.append(i.cost)
            ob2v.append(i.emission)
            ob3v.append(i.wait)
        ob1v2 = []
        ob2v2 = []
        ob3v2 = []
        for i in list2:
            ob1v2.append(i.cost)
            ob2v2.append(i.emission)
            ob3v2.append(i.wait)

        rcmap = matplotlib.cm.get_cmap('copper_r')
        plt.figure(figsize=(8, 6))
        scatter = plt.scatter(ob1v, ob3v, c=ob2v, cmap=rcmap, marker='o', alpha=0.7, label='20,000')
        scatter = plt.scatter(ob1v2, ob3v2, c=ob2v2, cmap=rcmap, marker='^', alpha=0.7, label='18,000')
        cbar = plt.colorbar(scatter, label='Emission', orientation='vertical')
        plt.xlabel('Operational cost')
        plt.legend()
        plt.ylabel("Total Ride duration")
        plt.title('Pareto front with colour intensity for Emission')
        plt.show()

    @staticmethod
    def is_dominated(result, result_list):
        for other_result in result_list:
            if (
                    result.cost >= other_result.cost
                    and result.emission >= other_result.emission
                    and result.wait >= other_result.wait
                    and (
                    result.cost > other_result.cost
                    or result.emission > other_result.emission
                    or result.wait > other_result.wait
            )
            ):
                return True
        return False


path = "../Data/moderate/output/paretodata/"
paretoga = MOresult.readfile(path + "GGA+30n1220000.csv")
pareto = MOresult.readfile(path + "GGA+30n1218000.csv")
#plot_2_graphs(read_csv(path + "conv30.csv"), read_csv(path + "conv50.csv"))
print("Score ", get_score(get_best_solution(paretoga)) / 50)
print("Spread ", calculate_spread(paretoga))
print("Delta ", calculate_delta(paretoga))
newpareto = MOresult.remove_duplicates(pareto)
nondom = MOresult.non_dominated(paretoga, newpareto)
#showpareto(paretoga)
ndga, ndmip = MOresult.non_dominated_origins(paretoga, newpareto)
MOresult.show2paretos(ndga, ndmip)
#MOresult.show2paretos(paretoga, pareto)
