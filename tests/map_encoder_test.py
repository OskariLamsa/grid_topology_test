import csv
from pathlib import Path
import io
import pytest
from PIL import Image

import map_encoder

def create_test_image(path: Path, size=(3, 2), black_pixels=None):
    #Luodaan uusi kuva testejä varten
    img = Image.new("RGB", size, "white")
    if black_pixels:
        for x, y in black_pixels:
            img.putpixel((x, y), (0, 0, 0))
    img.save(str(path))

def read_csv_semicolon(path: Path):
    # Apufunktio .csv tiedoston lukemiseen
    rows = []
    with path.open("r", newline='') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            converted = []
            for v in row:
                try:
                    converted.append(int(v))
                except ValueError:
                    converted.append(v)
            rows.append(tuple(converted))
    return rows


def test_pixel_reader_direct(tmp_path):
    # Testataan, että map_encoder.pixel_reader toimii
    img_path = tmp_path / "m.png"
    create_test_image(img_path, size=(3,2), black_pixels=[(1,0), (2,1)])
    result = map_encoder.pixel_reader(str(img_path))
    assert result[0] == (3, 2)
    assert (0, 1) in result
    assert (1, 2) in result


def test_main_creates_csv_when_missing(tmp_path, monkeypatch):
    # Tehdään väliaikaiset maps ja maps_data kansiot
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    maps = project_dir / "maps"
    maps_data = project_dir / "maps_data"
    maps.mkdir()
    maps_data.mkdir()

    #Tehdään uusi kuva-tiedosto maps kansioon, ja katsotaan että .csv luodaan.
    img_file = maps / "testmap.png"
    create_test_image(img_file, size=(3,2), black_pixels=[(0,0)])
    monkeypatch.setattr(map_encoder, "__file__", str(project_dir / "dummy_module.py"))
    map_encoder.main("maps", "maps_data")
    csv_path = maps_data / "testmap.csv"
    assert csv_path.exists()


def test_main_does_not_overwrite_existing_csv(tmp_path, monkeypatch):
    # Tehdään väliaikaiset maps ja maps_data kansiot
    project_dir = tmp_path / "project2"
    project_dir.mkdir()
    maps = project_dir / "maps"
    maps_data = project_dir / "maps_data"
    maps.mkdir()
    maps_data.mkdir()

    #Luodaan kartta-kuva
    img_file = maps / "mapA.png"
    create_test_image(img_file, size=(2,2), black_pixels=[(1,1)])

    #Luodaan .csv tiedosto. Tätä EI saa ylikirjoittaa
    csv_path = maps_data / "mapA.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([999, 999]) #Random rivi .csv -tiedostolle

    monkeypatch.setattr(map_encoder, "__file__", str(project_dir / "dummy.py"))

    # Ajetaan main, katsotaan ylikirjoittaako se meidän .csv:n
    map_encoder.main("maps", "maps_data")
    rows_after = read_csv_semicolon(csv_path)

    # Random rivi pitäisi vielä löytyä
    assert rows_after[0] == (999, 999)
