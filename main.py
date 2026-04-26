import os
import runpy
import sys
"""
def list_algorithms():
    path = os.path.join(os.path.dirname(__file__), "algorithms")
    files = os.listdir(path)

    algorithms = [
        f[:-3] for f in files
        if f.endswith(".py") and f != "__init__.py"
    ]

    return algorithms
"""
def list_maps(maps_data_folder="maps_data"):
    path = os.path.join(os.path.dirname(__file__), maps_data_folder)
    files = os.listdir(path)
    maps = [
        f[:-4] for f in files
        if f.endswith(".csv")
    ]
    return sorted(maps)


def main():
    grid_choice = input("\nWhich grid type do you want to run? ")

    if grid_choice != "square" and grid_choice != "hex":
        print(f"Error: '{grid_choice}' is not a valid grid type. Please choose between 'square' and 'hex'.")
        return
    folder_choice = input("\nWhich folder's maps? (0.10, 0.20, 0.30) ")
    maps = list_maps(folder_choice)
    for i in maps:
        print(f" - {i}")

    print("Which map do you want to choose? ")
    map_choice = input(f"You can also type \"custom\" to draw your own map. ")
    if grid_choice == "all":
        if map_choice == "custom":
            runpy.run_module(f"visualizer", run_name="__main__")
            return
        if map_choice not in maps:
            print(f"Error. {map_choice} is not a valid map name.")
            return
        sys.argv = ["", map_choice + ".csv"]
        runpy.run_module(f"visualizer", run_name="__main__")
        return
   
    elif map_choice == "custom":
        runpy.run_module(f"astar_{grid_choice}", run_name="__main__")
    elif map_choice in maps: 
        sys.argv = ["", map_choice + ".csv", folder_choice]
        runpy.run_module(f"astar_{grid_choice}", run_name="__main__")
    else:    
        print(f"Error. {map_choice} is not a valid map name.")
        return

if __name__ == "__main__":
    main()
