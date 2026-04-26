import os
import csv
from pathlib import Path

def map_loader(file_name, base_dir=None, maps_data_folder="maps_data"):
    #Ottaa tiedostonimen, ja palauttaa listan tupleja 
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent
        print(file_name, maps_data_folder)
    path = os.path.join(base_dir, maps_data_folder)
    if not os.path.isdir(path):
        return print(f"{maps_data_folder} not found")
    if file_name.suffix if isinstance(file_name, Path) else not file_name.endswith(".csv"):
        raise ValueError("Invalid file type")
    with open(os.path.join(path, file_name), "r") as f:
        print("Found file ", file_name)
        map_data = []
        for line in f:
            parts = line.strip().split(";")
            if len(parts) == 6:
                map_data.append((int(parts[0]), int(parts[1]), parts[2], parts[3], parts[4], parts[5]))
            else:
                map_data.append((int(parts[0]), int(parts[1])))
        return map_data
if __name__ == "__main__":
    map_loader("Berlin_0.csv")