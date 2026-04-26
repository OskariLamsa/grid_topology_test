from visualizer import Visualizer
from map_loader import map_loader
import astar_square
import astar_hex
import csv
import main

def test_all():
    map_01 = main.list_maps("0.10")
    map_02 = main.list_maps("0.20")
    map_03 = main.list_maps("0.30")
    filename = ("0.10", "0.20", "0.30")
    counter = 0
    list_of_lists = [map_01, map_02, map_03]
    for map_list in list_of_lists:
        with open(f"test_{filename[counter]}.csv", "w") as file:
            writer = csv.writer(file, delimiter=';')
            for i in map_list:
                map_data = map_loader(f"{i}.csv", None, filename[counter])
                square_move_distance = 100/map_data[0][0]
                if i[7] == "s":
                    mode = "square"
                    v = Visualizer(width=1000, dimensions=250, caption=f"{i}", map_data=map_data, mode = "square")
                    time, distance = v.run_algorithm(astar_square.algorithm)
                else:
                    mode = "hex"
                    v = Visualizer(width=1000, dimensions=250, caption=f"{i}", map_data=map_data, mode = "hex")
                    time, distance = v.run_algorithm(astar_hex.algorithm)
                if mode == "square":
                    distance = distance * square_move_distance
                else:
                    distance = distance * square_move_distance * 1.074569932
                time = round(time, 3)
                distance = round(distance, 3)

                writer.writerow([mode, i, f"{map_data[0][2]},{map_data[0][3]}", f"{map_data[0][4]},{map_data[0][5]}", time, distance])
        counter += 1


if __name__ == "__main__":
    test_all()