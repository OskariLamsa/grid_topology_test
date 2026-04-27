from queue import PriorityQueue
from time import sleep
import time
from math import sqrt


def move_cost(a, b):
    x1, y1 = a.get_pos()
    x2, y2 = b.get_pos()

    # viisto liike = 1.41421356237
    if x1 != x2 and y1 != y2:
        return sqrt(2)
    # kardinaali liike = 1
    return 1

def h(p1, p2):
    #Octile distance heuristiikka
    x1, y1 = p1
    x2, y2 = p2
    x_distance = abs(x1 - x2)
    y_distance = abs(y1 - y2)
    result = (max(x_distance,y_distance) + (sqrt(2)-1)*min(x_distance, y_distance))
    return result
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
    draw()


def algorithm(draw, grid, start, end):
    count = 0
    start_time = time.time()
    open_set = PriorityQueue()
    open_set.put((h(start.get_pos(), end.get_pos()), 0, count, start))

    came_from = {}
    g_score = {pixel: float("inf") for row in grid for pixel in row}
    g_score[start] = 0
    closed = set()
    open_nodes = {start}
    #Seuraavat muuttujat kerätään suorituksen aikana tilastoja varten
    stats = {
        "heap_pushes": 1,
        "max_heap_size": 1,
        "heap_pops" : 0,
        "expanded_nodes": 0,
        "max_open_unique_nodes": 1,
        "stale_pops": 0,
    }
    while not open_set.empty():
        queued_f, queued_h, _, current = open_set.get()
        stats["heap_pops"] += 1
        if current in closed:
            stats["stale_pops"] += 1
            continue
        open_nodes.discard(current)
        stats["expanded_nodes"] += 1
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            sleep(5)
            return time.time() - start_time, g_score[end], stats

        closed.add(current)

        for neighbor in current.neighbors:
            if neighbor in closed:
                continue

            temp_g_score = g_score[current] + move_cost(current, neighbor)

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score

                heuristic = h(neighbor.get_pos(), end.get_pos())
                f_score = temp_g_score + heuristic

                count += 1
                open_set.put((f_score, -temp_g_score, count, neighbor))
                stats["heap_pushes"] += 1
                open_nodes.add(neighbor)
                stats["max_heap_size"] = max(
                    stats["max_heap_size"],
                    open_set.qsize())
                stats["max_open_unique_nodes"] = max(
                    stats["max_open_unique_nodes"],
                    len(open_nodes))
                if neighbor != end:
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return "No path was found", "", stats
if __name__ == "__main__":
    import sys
    from visualizer import Visualizer
    from map_loader import map_loader
    map_data = None
    if len(sys.argv) < 2:
        print("Called astar without a map file. Defaulting to empty map.")
        custom_rows = input("How big would you like the grid to be? ")
        try:
            custom_rows = int(custom_rows)
        except ValueError:
            custom_rows = custom_rows.split(",")
        v = Visualizer(width=800, dimensions=(int(custom_rows[0]), int(custom_rows[1])), caption="a*", map_data=map_data)
    else:
        print("Called astar with map_data" \
        "")
        map_data = sys.argv[1]
        map_data = map_loader(map_data, None, sys.argv[2])
        v = Visualizer(width=1100, dimensions=250, caption="a*", map_data=map_data)
    if v.edit_loop():
        resolution_time, distance, stats = v.run_algorithm(algorithm)
    #    resolution_time, distance = v.run(algorithm)  
        print(f"Resolved A* in {resolution_time} seconds")
        print(f"Distance: {distance}")
        print(f"Stats: {stats}")
