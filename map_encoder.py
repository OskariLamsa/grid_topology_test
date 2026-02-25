#Tämä skripti tekee karttakuvista .csv-tiedostoja.
from PIL import Image
import os
import csv

def main(maps_dir_to_set, maps_data_dir_to_set):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    maps_dir = os.path.join(base_dir, maps_dir_to_set)
    maps_data = os.path.join(base_dir, maps_data_dir_to_set)
    if not os.path.isdir(maps_dir):
        print(f"maps directory not found.")
        return
    if not os.path.isdir(maps_data):
        print(f"maps_data directory not found.")
        return
    
    maps_files = os.listdir(maps_dir)
    maps_data_files = os.listdir(maps_data)

    for file in maps_files:
        map_file_path = os.path.join(maps_dir, file)
        if os.path.isfile(map_file_path):
            csv_name = file[0:-4] + ".csv"
            if csv_name in maps_data_files:
                print(f"{csv_name} exists in maps_data!")
            else:
                print(f"{csv_name} is missing from maps_data")
                maps_data_encoder(csv_name, map_file_path, maps_dir, maps_data)
                
def maps_data_encoder(csv_name, map_file_path, maps_dir, maps_data):
    #Ottaa maps ja maps_data kirjastot, kuvan nimen, ja halutun map_data-tiedoston nimen.
    #Ei palauta mitään, mutta kirjoittaa maps_data-kansioon .csv tiedoston.
    black_pixels_array = pixel_reader(os.path.join(maps_dir, map_file_path))
    with open(os.path.join(maps_data, csv_name), "w") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(black_pixels_array)
        print(f"Wrote {csv_name} in {maps_data}!")


def pixel_reader(file_path):
    # Ottaa tiedosto-osoitteen, palauttaa pikselit listassa

    img = Image.open(file_path).convert("RGB")
    pixels = img.load()
    width, height = img.size
    black_pixels_array = []
    black_pixels_array.append((width, height))
    for i in range(height):
        for j in range(width):
            r, g, b = pixels[j, i]
            if (r, g, b) == (0,0,0):
                black_pixels_array.append((i,j))
    return black_pixels_array


if __name__ == "__main__":
    main("maps", "maps_data")