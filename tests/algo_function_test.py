import pytest
from visualizer import Visualizer
from map_loader import map_loader
import algorithms.astar
import algorithms.jps

def test_diagonal_all_algorithms():
    # astar
    results = []
    for i in ["test_diagonal.csv", "test_diagonal_90.csv", "test_diagonal_180.csv", "test_diagonal_270.csv"]:
        map_data = map_loader(i)
        if i == "test_diagonal.csv":
            start_pos = (0,0)
            end_pos = (0,49)
        elif i == "test_diagonal_90.csv":
            start_pos = (0,49)
            end_pos = (49,49)
        elif i == "test_diagonal_180.csv":
            start_pos = (49,49)
            end_pos = (49,0)
        else:
            start_pos = (49,0)
            end_pos = (0,0)
        v = Visualizer(width = 1100, rows = 3, caption="testing", map_data=map_data, start_pos = start_pos, end_pos = end_pos)
        time, distance = v.run_algorithm(algorithms.astar.algorithm)
        results.append(str(round(float(distance), 3)))
    assert results[0] == results[1] == results[2] == results[3] =='152.782'
    # jps
    results_jps = []
    for i in ["test_diagonal.csv", "test_diagonal_90.csv", "test_diagonal_180.csv", "test_diagonal_270.csv"]:
        map_data = map_loader(i)
        if i == "test_diagonal.csv":
            start_pos = (0,0)
            end_pos = (0,49)
        elif i == "test_diagonal_90.csv":
            start_pos = (0,49)
            end_pos = (49,49)
        elif i == "test_diagonal_180.csv":
            start_pos = (49,49)
            end_pos = (49,0)
        else:
            start_pos = (49,0)
            end_pos = (0,0)
        v = Visualizer(width = 1100, rows = 3, caption="testing", map_data=map_data, start_pos = start_pos, end_pos = end_pos)
        time, distance = v.run_algorithm(algorithms.jps.algorithm)
        results_jps.append(str(round(float(distance), 3)))
    assert results_jps[0] == results_jps[1] == results_jps[2] == results_jps[3] =='152.782'
    assert results_jps == results

def test_cardinal_all_algorithms():
    # astar
    results = []
    for i in ["test_cardinal.csv", "test_cardinal_90.csv", "test_cardinal_180.csv", "test_cardinal_270.csv"]:
        map_data = map_loader(i)
        if i == "test_cardinal.csv":
            start_pos = (0,0)
            end_pos = (11,28)
        elif i == "test_cardinal_90.csv":
            start_pos = (0,49)
            end_pos = (28,38)
        elif i == "test_cardinal_180.csv":
            start_pos = (49,49)
            end_pos = (38,21)
        else:
            start_pos = (49,0)
            end_pos = (21,11)
        v = Visualizer(width = 1100, rows = 3, caption="testing", map_data=map_data, start_pos = start_pos, end_pos = end_pos)
        time, distance = v.run_algorithm(algorithms.astar.algorithm)
        print(i, distance)
        results.append(str(round(float(distance), 3)))
    assert results[0] == results[1] == results[2] == results[3] =='176.841'
    # jps
    results_jps = []
    for i in ["test_cardinal.csv", "test_cardinal_90.csv", "test_cardinal_180.csv", "test_cardinal_270.csv"]:
        map_data = map_loader(i)
        if i == "test_cardinal.csv":
            start_pos = (0,0)
            end_pos = (11,28)
        elif i == "test_cardinal_90.csv":
            start_pos = (0,49)
            end_pos = (28,38)
        elif i == "test_cardinal_180.csv":
            start_pos = (49,49)
            end_pos = (38,21)
        else:
            start_pos = (49,0)
            end_pos = (21,11)
        v = Visualizer(width = 1100, rows = 3, caption="testing", map_data=map_data, start_pos = start_pos, end_pos = end_pos)
        time, distance = v.run_algorithm(algorithms.jps.algorithm)
        print(i, distance)
        results_jps.append(str(round(float(distance), 3)))
    assert results_jps[0] == results_jps[1] == results_jps[2] == results_jps[3] =='176.841'
    assert results_jps == results