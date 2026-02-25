import pytest
from visualizer import Visualizer
import algorithms.jps
from visualizer import Spot
def test_heuristic():
    start = (1,1)
    end = (2,4)
    assert algorithms.jps.h(start, end) == 3.414
def test_algorithm():
    # Käytetään 3x3 testikarttaa, joka on annettu map_data muodossa eli listana.
    v = Visualizer(width = 1100, rows=3, caption="testing", map_data=[(3,3),(0,0),(0,1),(2,1),(2,2),], start_pos = (2,0), end_pos = (0,2))
    assert v.run_algorithm(algorithms.jps.algorithm) != ("No path was found", "")
def test_algorithm_impossible_map():
    # Sama kuin aiemmin, mutta tukitaan tahallaan tie, että algo ei onnistu.
    v = Visualizer(width = 1100, rows=3, caption="testing", map_data=[(3,3),(0,0),(0,1),(1,1),(2,1),(2,2),], start_pos = (2,0), end_pos = (0,2))
    assert v.run_algorithm(algorithms.jps.algorithm) == ("No path was found", "")
def test_is_walkable():
    # Tehdään grid-olio, jossa on yksi valkoinen ja yksi musta pikseli, ja testataan,
    # Ovatko ne odotetusti "käveltäviä" tai ei
    grid = [[]]
    white_spot = Spot(0,0,250,250)
    grid[0].append(white_spot)
    barrier_spot = Spot(1,0,250,250)
    barrier_spot.make_barrier()
    grid[0].append(barrier_spot)
    assert algorithms.jps.is_walkable(grid, 0, 0) == True
    assert algorithms.jps.is_walkable(grid, 1, 0) == False

def test_has_forced_neighbor_horizontal():
    # Testataan pakotettujen naapureiden olemassaolo
    # Oikea liike, naapuri ylös-oikealla
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_left, 0, 1, grid) == True

    # Oikea liike, naapuri alas-oikealla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_left.make_barrier()
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_left, 0, 1, grid) == True

    # Oikea liike, tie estetty
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_left, 0, 1, grid) == False

    # Vasen liike, naapuri ylös-vasemmalla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    top_right.make_barrier()
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_right, 0, -1, grid) == True

    # Vasen liike, naapuri alas-vasemmalla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_right, 0, -1, grid) == True

    # Vasen liike, tie estetty
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_right, 0, -1, grid) == False

def test_has_forced_neighbor_vertical():
    # Testataan pakotettujen naapureiden olemassaolo
    # Ylös liike, naapuri ylös-oikealla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_left, -1, 0, grid) == True

    # Ylös liike, naapuri ylös-vasemmalla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_left.make_barrier()
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_right, -1, 0, grid) == True

    # Ylös liike, tie estetty
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_left, -1, 0, grid) == False

    # Alas liike, naapuri alas-oikealla
    top_left = Spot(0,0,250,250)
    top_right = Spot(0,1,250,250)
    top_right.make_barrier()
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_left, 1, 0, grid) == True

    # Alas liike, naapuri alas-vasemmalla
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_right, 1, 0, grid) == True

    # Alas liike, tie estetty
    top_left = Spot(0,0,250,250)
    top_left.make_barrier()
    top_right = Spot(0,1,250,250)
    bot_left = Spot(1,0,250,250)
    bot_right = Spot(1,1,250,250)
    bot_right.make_barrier()
    grid = [[top_left, top_right],[bot_left, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_right, 1, 0, grid) == False
def test_has_forced_neighbor_diagonal():
    # Ylös-oikea diagonaali, naapuri alas-oikea
    top_left = Spot(0,0,250,250)
    top_middle = Spot(0,1,250,250)
    top_right = Spot(0,2,250,250)
    bot_left = Spot(1,0,250,250)
    bot_middle = Spot(1,1,250,250)
    bot_middle.make_barrier()
    bot_right = Spot(1,2,250,250)
    grid = [[top_left, top_middle, top_right],[bot_left, bot_middle, bot_right]]
    assert algorithms.jps.has_forced_neighbor(top_middle, -1, 1, grid) == True

    # Alas-oikea diagonaali, naapuri ylös-oikea
    top_left = Spot(0,0,250,250)
    top_middle = Spot(0,1,250,250)
    top_middle.make_barrier()
    top_right = Spot(0,2,250,250)
    bot_left = Spot(1,0,250,250)
    bot_middle = Spot(1,1,250,250)
    bot_right = Spot(1,2,250,250)
    grid = [[top_left, top_middle, top_right],[bot_left, bot_middle, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_middle, 1, 1, grid) == True

    # Alas-oikea diagonaali, tie estetty
    top_left = Spot(0,0,250,250)
    top_middle = Spot(0,1,250,250)
    top_middle.make_barrier()
    top_right = Spot(0,2,250,250)
    bot_left = Spot(1,0,250,250)
    bot_middle = Spot(1,1,250,250)
    bot_right = Spot(1,2,250,250)
    top_right.make_barrier()
    grid = [[top_left, top_middle, top_right],[bot_left, bot_middle, bot_right]]
    assert algorithms.jps.has_forced_neighbor(bot_middle, -1, 1, grid) == False

def test_reconstruct_path():
    # Testataan, toimiiko polunpiirtäjä-funktio. Sen pitäisi maalata polku violetiksi
    def draw():
        pass
    came_from = {}
    spot0 = Spot(0,0,250,250)
    spot1 = Spot(0,1,250,250)
    came_from[spot1] = (spot0, (0,1), None)
    spot2 = Spot(0,2,250,250)
    came_from[spot2] = (spot1, (0,1), None)
    assert spot1.color == (255, 255, 255)
    algorithms.jps.reconstruct_path(came_from, spot2, draw)
    assert spot1.color == (128, 0, 128)

def test_pruned_directions():
    # Testataan, palauttaako funktio oletetut suunnat
    # Sama suunta kuin syöte jos kardinaaliliike
    # Sama viisto ja kaksi kardinaalia jos viistoliike
    assert algorithms.jps.get_pruned_directions((1,0)) == [(1,0)]
    assert algorithms.jps.get_pruned_directions((0,1)) == [(0,1)]
    assert algorithms.jps.get_pruned_directions((-1,0)) == [(-1,0)]
    assert algorithms.jps.get_pruned_directions((0,-1)) == [(0,-1)]
    assert algorithms.jps.get_pruned_directions((1,1)) == [(1,0),(0,1),(1,1)]
    assert algorithms.jps.get_pruned_directions((1,-1)) == [(1,0),(0,-1),(1,-1)]
    assert algorithms.jps.get_pruned_directions((-1,1)) == [(-1,0),(0,1),(-1,1)]
    assert algorithms.jps.get_pruned_directions((-1,-1)) == [(-1,0),(0,-1),(-1,-1)]

def test_jump_outside_grid():
    def draw():
        pass
    new_spot = Spot(0,0,250,250)
    grid = [[]]
    grid[0].append(new_spot)
    wrong_spot = Spot(-100,-100,250,250)
    assert algorithms.jps.jump(wrong_spot, (0,1), grid, draw) == (None, 0, [])
def test_jump_into_barrier():
    def draw():
        pass
    new_spot = Spot(0,0,250,250)
    barrier_spot = Spot(0,1,250,250)
    barrier_spot.make_barrier()
    grid = [[]]
    grid[0].append(barrier_spot)
    assert algorithms.jps.jump(new_spot, (0,1), grid, draw) == (None, 0, [])
def test_jump_into_end():
    def draw():
        pass
    new_spot = Spot(0,0,250,250)
    end_spot = Spot(0,1,250,250)
    silly_spot = Spot(1,0,250,250)
    funny_spot = Spot(1,1,250,250)
    end_spot.make_end()
    grid = [[],[]]
    grid[0].append(new_spot)
    grid[1].append(end_spot)
    grid[0].append(silly_spot)
    grid[1].append(funny_spot)
    assert algorithms.jps.jump(new_spot, (0,1), grid, draw) == (None, 0, [])