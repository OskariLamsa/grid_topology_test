import map_loader
import pytest
import os
def test_call_loader_no_input():
    with pytest.raises(TypeError, match="missing 1 .* 'file_name'"):
        map_loader.map_loader()

def test_call_loader_too_many_inputs():
    with pytest.raises(TypeError, match="takes .* but 3 were given"):
        map_loader.map_loader("Milan_0.csv", "Paris_0.csv", "Sydney_0")

# Käytetään 3x3test.csv-tiedostoa testiin.
def test_get_image_data():
    data = map_loader.map_loader("3x3test.csv")
    # Ensimmäinen lukupari kertoo kuvan koon.
    # Loput kertovat mustien pikseleiden sijainnin.
    assert data == [(3,3),(0,0),(0,1),(2,1),(2,2),]

def test_invalid_file_name():
    with pytest.raises(FileNotFoundError, match="No such file or directory:"):
        map_loader.map_loader("This_is_not_a_real_map.csv")

def test_invalid_file_type(tmp_path, monkeypatch):
    project_dir = tmp_path / "project_dir"
    maps_data = project_dir / "maps_data"
    maps_data.mkdir(parents=True)

    txt_file = maps_data / "test.txt"
    txt_file.write_text("This is a test.")

    monkeypatch.chdir(project_dir)

    with pytest.raises(ValueError):
        map_loader.map_loader("test.txt")
