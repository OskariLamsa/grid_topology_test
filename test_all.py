from visualizer import Visualizer
from map_loader import map_loader
import astar_square
import astar_hex
import csv
import main
def original_square_node_count_from_name(name):
    return int((name[5:]).split("x")[0])
def test_all():
    map_01 = main.list_maps("0.10")
    map_02 = main.list_maps("0.20")
    map_03 = main.list_maps("0.30")
    map_04 = main.list_maps("0.40")
    filename = ("0.10", "0.20", "0.30", "0.40")
    counter = 0
    list_of_lists = [map_01, map_02, map_03, map_04]
    for map_list in list_of_lists:

        # Raportti jokaista tiheyttä varten
        with open(f"test_{filename[counter]}.csv", "w") as file:
            writer = csv.writer(file, delimiter=';')
            for map in map_list:
                map_data = map_loader(f"{map}.csv", None, filename[counter])
                original_node_count = original_square_node_count_from_name(map)
                square_move_distance = 100 / original_node_count
                if "square" in map:
                    mode = "square"
                    v = Visualizer(width=1000, dimensions=250, caption=f"{map}", map_data=map_data, mode = "square")
                    time, distance, stats = v.run_algorithm(astar_square.algorithm, headless = True)
                elif "hex" in map:
                    mode = "hex"
                    v = Visualizer(width=1000, dimensions=250, caption=f"{map}", map_data=map_data, mode = "hex")
                    time, distance, stats = v.run_algorithm(astar_hex.algorithm, headless = True)
                else:
                    raise ValueError(f"Invalid map name: {map}")
                if distance != "":
                    if mode == "square":
                        distance = distance * square_move_distance
                    else:
                        distance = distance * square_move_distance * 1.074569932
                    time = round(time, 3)
                    distance = round(distance, 3)

                writer.writerow([mode, map, f"{map_data[0][2]},{map_data[0][3]}",
                f"{map_data[0][4]},{map_data[0][5]}", time, distance,
                stats["heap_pushes"], stats["max_heap_size"], stats["heap_pops"],
                stats["expanded_nodes"], stats["max_open_unique_nodes"], stats["stale_pops"]])
        counter += 1


if __name__ == "__main__":
    test_all()