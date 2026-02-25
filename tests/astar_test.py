import pytest
from visualizer import Visualizer
import algorithms.astar
def test_heuristic():
    start = (1,1)
    end = (2,4)
    assert algorithms.astar.h(start, end) == 3.414
def test_algorithm():
    # Käytetään 3x3 testikarttaa, joka on annettu map_data muodossa eli listana.
    v = Visualizer(width = 1100, rows=3, caption="testing", map_data=[(3,3),(0,0),(0,1),(2,1),(2,2),], start_pos = (2,0), end_pos = (0,2))
    assert v.run_algorithm(algorithms.astar.algorithm) != ("No path was found", "")
def test_algorithm_impossible_map():
    # Sama kuin aiemmin, mutta tukitaan tahallaan tie, että algo ei onnistu.
    v = Visualizer(width = 1100, rows=3, caption="testing", map_data=[(3,3),(0,0),(0,1),(1,1),(2,1),(2,2),], start_pos = (2,0), end_pos = (0,2))
    assert v.run_algorithm(algorithms.astar.algorithm) == ("No path was found", "")