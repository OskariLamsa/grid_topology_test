from queue import PriorityQueue
import time
from math import sqrt

def oddq_to_cube(row, col):
    q = col
    r = row - (col - (col & 1)) // 2
    s = -q - r
    return q, r, s

def h(p1, p2):
    row1, col1 = p1
    row2, col2 = p2

    x1, y1, z1 = oddq_to_cube(row1, col1)
    x2, y2, z2 = oddq_to_cube(row2, col2)

    calc = (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2
    return calc
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
    draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((h(start.get_pos(), end.get_pos()), 0, count, start))
    start_time = time.time()
    came_from = {}
    g_score = {pixel: float("inf") for row in grid for pixel in row}
    g_score[start] = 0

    closed = set()

    while not open_set.empty():
        queued_f, queued_g, _, current = open_set.get()

        if current in closed:
            continue

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            #time.sleep(5)
            return time.time() - start_time, g_score[end]

        closed.add(current)

        for neighbor in current.neighbors:
            if neighbor in closed:
                continue

            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score

                heuristic = h(neighbor.get_pos(), end.get_pos())
                f_score = temp_g_score + heuristic

                count += 1
                open_set.put((f_score, heuristic, count, neighbor))

                if neighbor != end:
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return "No path was found", ""


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
        v = Visualizer(width=800, dimensions=(int(custom_rows[0]), int(custom_rows[1])), caption="a*", map_data=map_data, mode="hex")
    else:
        print("Called astar with map_data" \
        "")
        map_data = sys.argv[1]
        map_data = map_loader(map_data, None, sys.argv[2])
        v = Visualizer(width=1100, dimensions=250, caption="a*", map_data=map_data, mode = "hex")
    if v.edit_loop():
        resolution_time, distance = v.run_algorithm(algorithm)
    #    resolution_time, distance = v.run(algorithm)  
        print(f"Resolved A* in {resolution_time} seconds")
        print(f"Distance: {distance}")
