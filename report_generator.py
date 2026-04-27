import os
from pathlib import Path

def find_map_by_name(data, name):
    for map in data:
        map_name = map[1]
        if name == map_name:
            return map
    return "Map not found"
def open_file(file_name):
    base_dir = Path(__file__).resolve().parent
    with open(os.path.join(base_dir, file_name), "r") as f:
        print("Found file ", file_name)
        data = []
        for line in f:
            parts = line.strip().split(";")
            if len(parts) > 1:
                data.append((parts[0], parts[1], parts[2], parts[3], float(parts[4]),
                    float(parts[5]), int(parts[6]), int(parts[7]), int(parts[8]),
                    int(parts[9]), int(parts[10]), int(parts[11])))
            else:
                continue
        return data

def report_generator():
    for density in ["0.10", "0.20", "0.30", "0.40"]:
        with open(f"{density}.md", "w", encoding = "utf-8") as file:
            file.write(f"| Kartta | neliö- kuusioaika | neliö- kuusio etäisyys | A-listan lisäykset | A-listan maksimikoko | A-listan poiminnat | Laajennettujen solmujen määrä | Maksimi avoimien uniikkien solmujen määrä | Stale popit |\n")
            data =open_file(f"test_{density}.csv")
            hex_list = []
            square_list = []
            for map in data:
                if map[0] == "hex":
                    hex_list.append(map)
                elif map[0] == "square":
                    square_list.append(map)
                else:
                    raise ValueError(f"Invalid shape type:{map[0]}")
            for i in range(0, (int(len(square_list)/6))):
                small_square =find_map_by_name(square_list, f"{density}_50x50square{i}")
                medium_square =find_map_by_name(square_list, f"{density}_200x200square{i}")
                large_square =find_map_by_name(square_list, f"{density}_500x500square{i}")
                largest_square =find_map_by_name(square_list, f"{density}_1000x1000square{i}")
                small_hex =find_map_by_name(hex_list, f"{density}_50x50hex{i}")
                medium_hex =find_map_by_name(hex_list, f"{density}_200x200hex{i}")
                large_hex =find_map_by_name(hex_list, f"{density}_500x500hex{i}")
                largest_hex =find_map_by_name(hex_list, f"{density}_1000x1000hex{i}")
                print(small_square)
                print(small_hex)
                file.write(f"| {i}_50x50 | {small_square[4]}/{small_hex[4]} | {small_square[5]}/{small_hex[5]} | {round((small_square[6] /small_hex[6]),3)} | {round((small_square[7] /small_hex[7]),3)} | {round((small_square[8] /small_hex[8]),3)} | {round((small_square[9] /small_hex[9]),3)} | {round((small_square[10] /small_hex[10]),3)} | {round((small_square[11] /small_hex[11]),3)} |\n")
                file.write(f"| {i}_200x200 | {medium_square[4]}/{medium_hex[4]} | {medium_square[5]}/{medium_hex[5]} | {round((medium_square[6] /medium_hex[6]),3)} | {round((medium_square[7] /medium_hex[7]),3)} | {round((medium_square[8] /medium_hex[8]),3)} | {round((medium_square[9] /medium_hex[9]),3)} | {round((medium_square[10] /medium_hex[10]),3)} | {round((medium_square[11] /medium_hex[11]),3)} |\n")
                file.write(f"| {i}_500x500 | {large_square[4]}/{large_hex[4]} | {large_square[5]}/{large_hex[5]} | {round((large_square[6] /large_hex[6]),3)} | {round((large_square[7] /large_hex[7]),3)} | {round((large_square[8] /large_hex[8]),3)} | {round((large_square[9] /large_hex[9]),3)} | {round((large_square[10] /large_hex[10]),3)} | {round((large_square[11] /large_hex[11]),3)} |\n")
                file.write(f"| {i}_1000x1000 | {largest_square[4]}/{largest_hex[4]} | {largest_square[5]}/{largest_hex[5]} | {round((largest_square[6] /largest_hex[6]),3)} | {round((largest_square[7] /largest_hex[7]),3)} | {round((largest_square[8] /largest_hex[8]),3)} | {round((largest_square[9] /largest_hex[9]),3)} | {round((largest_square[10] /largest_hex[10]),3)} | {round((largest_square[11] /largest_hex[11]),3)} |\n")
if __name__ == "__main__":
    report_generator()