#!/usr/bin/env python3

import math
import random
import sys

class Ant:
    def __init__(self, tour_length, tour, visited):
        self.tour_length = tour_length
        self.tour = tour
        self.visited = visited

def get_cities(cities):
    fin = open(INPUT_FILE, 'r')
    while True:
        line = fin.readline().split()
        if len(line) == 0:
            break
        elif len(line) != 2:
            raise IOError
        else:
            line = [int(l) for l in line]
            cities.append(tuple(line))
    fin.close()

def distance(x, y):
    return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def create_distance_matrix(dist, cities):
    for i in range(len(cities)):
        row = list()
        for j in range(len(cities)):
                row.append(int(distance(cities[i], cities[j])))
        dist.append(row)

def create_nn_list_matrix(nn_list, cities):
    for missing in range(len(cities)):
        row = [city for city in range(len(cities)) if city != missing]
        row.sort(key=lambda city: distance(cities[city], cities[missing]))
        nn_list.append(row)

def nearest_neighbour(cities, nn_list):
    visited = [False] * len(cities)
    tour_length = 0
    last_city = 0
    visited[last_city] = True
    unvisited = len(cities) - 1
    while unvisited > 0:
        for i in range(len(nn_list[last_city])):
            if not visited[nn_list[last_city][i]]:
                break
        next_city = nn_list[last_city][i]
        tour_length += distance(cities[last_city], cities[next_city])
        visited[next_city] = True
        unvisited -= 1
        last_city = next_city
    tour_length += distance(cities[last_city], cities[0])
    return tour_length

def create_pheromone_matrix(pheromone, cities, nn_list):
    tau0 = nearest_neighbour(cities, nn_list)
    for i in range(len(cities)):
        pheromone.append([tau0 for j in range(len(cities))])

def create_choice_info_matrix(choice_info, dist, pheromone):
    for i in range(len(dist)):
        row = list()
        for j in range(len(dist)):
            try:
                row.append(pheromone[i][j]**ALPHA * (1/dist[i][j])**BETA)
            except ZeroDivisionError:
                row.append(0)
        choice_info.append(row)

def initialize_data(cities, dist, nn_list, pheromone, choice_info, ants):
    get_cities(cities)
    create_distance_matrix(dist, cities)
    create_nn_list_matrix(nn_list, cities)
    create_pheromone_matrix(pheromone, cities, nn_list)
    create_choice_info_matrix(choice_info, dist, pheromone)
    for i in range(len(cities)):
        ants.append(Ant(0, [0] * (len(cities) + 1), [False] * len(cities)))

def choose_best_next(ant, step, ants, cities, choice_info):
    v = 0.0
    city = ants[ant].tour[step - 1]
    for i in range(len(cities)):
        if not ants[ant].visited[i] and choice_info[city][i] > v:
            next_city = i
            v = choice_info[city][i]
    ants[ant].tour[step] = next_city
    ants[ant].visited[next_city] = True
    

def neighbour_list_as_decision_rule(ant, step, ants, cities, nn_list, choice_info):
    city = ants[ant].tour[step - 1]
    sum_probabilities = 0.0
    selection_probability = list()
    for i in range(len(nn_list[city])):
        if ants[ant].visited[nn_list[city][i]]:
            selection_probability.append(0.0)
        else:
            selection_probability.append(choice_info[city][nn_list[city][i]])
            sum_probabilities += selection_probability[i]
    if sum_probabilities == 0.0:
        choose_best_next(ant, step, ants, cities, choice_info)
    else:
        r = random.uniform(0.0, sum_probabilities)
        p = 0.0
        for i in range(len(selection_probability)):
            p += selection_probability[i]
            if p >= r:
                break
        ants[ant].tour[step] = nn_list[city][i]
        ants[ant].visited[nn_list[city][i]] = True


def construct_solutions(ants, cities, dist, nn_list, pheromone, choice_info):
    for i in range(len(ants)):
        ants[i].visited = [False] * len(ants[i].visited)
    for i in range(len(ants)):
        r = random.randint(0, len(cities) - 1)
        ants[i].tour[0] = r
        ants[i].visited[r] = True
    for step in range(1, len(cities)):
        for i in range(len(ants)):
            neighbour_list_as_decision_rule(i, step, ants, cities, nn_list, choice_info)
    for i in range(len(ants)):
        ants[i].tour[len(cities)] = ants[i].tour[0]
        ants[i].tour_length = 0
        for j in range(len(ants[i].tour)):
            ants[i].tour_length += dist[ants[i].tour[j - 1]][ants[i].tour[j]]

def update_statistics(ants, best_tour, best_tour_length):
    for i in range(len(ants)):
        if ants[i].tour_length < best_tour_length:
            best_tour_length = ants[i].tour_length
            best_tour = ants[i].tour
    return (best_tour_length, best_tour)

def evaporate(pheromone):
    for i in range(len(pheromone)):
        for j in range(i, len(pheromone)):
            pheromone[i][j] = (1 - RHO) * pheromone[i][j]
            pheromone[j][i] = pheromone[i][j]

def deposit_pheromone(ant, ants, pheromone):
    deltatau = 1/ants[ant].tour_length
    for i in range(len(ants[ant].tour) - 1):
        j = ants[ant].tour[i]
        k = ants[ant].tour[i + 1]
        pheromone[j][k] = pheromone[j][k] + deltatau
        pheromone[k][j] = pheromone[j][k]

def update_pheromone_trails(ants, dist, pheromone, choice_info):
    evaporate(pheromone)
    for i in range(len(ants)):
        deposit_pheromone(i, ants, pheromone)
    create_choice_info_matrix(choice_info, dist, pheromone)

def aco_for_tsp():
    # Initialize data

    cities = list()
    dist = list()
    nn_list = list()
    pheromone = list()
    choice_info = list()
    ants = list()
    best_tour_length = float('inf')
    best_tour = list()

    initialize_data(cities, dist, nn_list, pheromone, choice_info, ants)

    if len(cities) == 0:
        return

    # The algorithm

    for iteration in range(ITERATIONS):
        # Let each (artificial) ant construct it's solution
        construct_solutions(ants, cities, dist, nn_list, pheromone, choice_info)
        # Update the best tour found
        best_tour_length, best_tour = update_statistics(ants, best_tour, best_tour_length)
        # Update phermone trails
        update_pheromone_trails(ants, dist, pheromone, choice_info)

    print(best_tour_length)
    print(best_tour)
    print(nearest_neighbour(cities, nn_list))

if __name__ == '__main__':
    try:
        ITERATIONS = int(sys.argv[1])
        INPUT_FILE = sys.argv[2]
        ALPHA = 1
        BETA = 5
        RHO = 0.5
        aco_for_tsp()
    except (IndexError, ValueError):
        print('Error: Wrong usage.')
        print('Usage: <NUMBER OF ITERATIONS> <INPUT FILE NAME>')
    except IOError:
        print('Error: Wrong input file name or wrong input file format.')
        print('Expected input file format:')
        print('<INTEGER><WHITE CHARACTERS><INTEGER>\\n')
