import tempfile
from datetime import datetime

import numpy as np
import pytest
import rasterio
from rasterio import transform, profiles
from shapely import Point

from psarps import (
    get_acquisition_time,
    get_closest_tide_station,
    get_raster_center,
    get_tide_height,
    get_tide_stations,
)


@pytest.fixture
def mock_planet_qa_raster():
    profile = profiles.default_gtiff_profile  # ty: ignore[unresolved-attribute]
    profile.update(
        {
            "count": 1,
            "width": 10,
            "height": 10,
            "dtype": "uint8",
            "crs": "EPSG:32609",
            "transform": transform.from_bounds(  # ty: ignore[unresolved-attribute]
                west=576000.0,
                south=5712000.0,
                east=600000.0,
                north=5736000.0,
                width=10,
                height=10,
            ),
        }
    )
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp_file:
        with rasterio.open(tmp_file.name, "w", **profile) as dataset:
            data = np.zeros((10, 10), dtype="uint8")
            dataset.write(data, 1)
            dataset.update_tags(
                **{
                    "SCENE_IDS[LAYER_2_VALUE]": (
                        "PSScene/20210728_191039_1009[15]\n"
                        "PSScene/20210728_191040_1009[16]\n"
                        "PSScene/20210728_191041_1009[17]\n"
                        "PSScene/20210728_191042_1009[18]\n"
                        "PSScene/20210728_184303_31_2427[207]\n"
                        "PSScene/20210728_184305_78_2427[208]\n"
                        "None[-999]"
                    )
                }
            )

        yield tmp_file


def test_get_acquisition_time(mock_planet_qa_raster):
    expected_acquisition_time = datetime(2021, 7, 28, 19, 1, 28)

    # Check if the acquisition time is a datetime object
    with rasterio.open(mock_planet_qa_raster.name) as dataset:
        assert "SCENE_IDS[LAYER_2_VALUE]" in dataset.tags()

    # Call the function to test
    acquisition_time = get_acquisition_time(mock_planet_qa_raster.name)

    # Assert that the acquisition time is as expected
    assert acquisition_time == expected_acquisition_time


def test_get_tide_stations():
    # Call the function to test
    stations = get_tide_stations()

    # Check if the result is a list
    assert isinstance(stations, list)

    # Check if each station is a dictionary with the expected keys
    for station in stations:
        assert isinstance(station, dict)
        assert "station_name" in station
        assert "station_location" in station
        assert isinstance(station["station_location"], Point)
        assert isinstance(station["station_name"], str)


def test_get_image_center(mock_planet_qa_raster):
    # Call the function to test
    center = get_raster_center(mock_planet_qa_raster.name)

    # Check if the center is a Point object
    assert isinstance(center, Point)

    # Assert that the center coordinates are as expected
    expected_center = Point(-127.72773488188726, 51.66009056735026)
    assert center.x == pytest.approx(expected_center.x)
    assert center.y == pytest.approx(expected_center.y)


def test_get_closest_station(mock_planet_qa_raster):
    closest_station = get_closest_tide_station(mock_planet_qa_raster.name)

    assert closest_station["station_name"] == "Addenbroke Isl."


def test_get_tide_height(mock_planet_qa_raster):
    # Call the function to test
    tide_height = get_tide_height(mock_planet_qa_raster.name)["tide_height"]

    # Check if the tide height is a float
    assert isinstance(tide_height, float)
    assert tide_height == pytest.approx(1.052, abs=0.001)
