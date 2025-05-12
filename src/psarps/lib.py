import re
from datetime import datetime, timedelta
from typing import Any

import pyproj
import rasterio
import requests
from geopy.distance import distance
from shapely.geometry import Point


def get_acquisition_time(image_qr_path: str) -> datetime:
    """
    Get the acquisition time a Planet Scope ARPS raster image.

    Args:
        image_path (str): Path to the raster image.

    Returns:
        datetime: Approximate acquisition time.
    """

    ts_pattern = re.compile(r"PSScene/(\d{4})(\d{2})(\d{2})_(\d\d)(\d\d)(\d\d)_.*")

    with rasterio.open(image_qr_path) as f:
        scene_ids = f.tags()["SCENE_IDS[LAYER_2_VALUE]"].split("\n")

        dts = []
        for si in scene_ids:
            m = ts_pattern.match(si)
            if m is not None:
                dt = datetime(
                    year=int(m.group(1)),
                    month=int(m.group(2)),
                    day=int(m.group(3)),
                    hour=int(m.group(4)),
                    minute=int(m.group(5)),
                    second=int(m.group(6)),
                )
                dts.append(dt)

        if not len(dts):
            raise ValueError("No valid scene ids")
        dt = datetime.fromtimestamp(sum([dt.timestamp() for dt in dts]) / len(dts))
        if dt.microsecond >= 500_000:
            dt += timedelta(seconds=1)
        acquisition_time = dt.replace(microsecond=0)
        return acquisition_time


def get_raster_center(image_qr_path: str) -> Point:
    """
    Get the center of a Planet Scope ARPS raster image.

    Args:
        image_path (str): Path to the raster image.

    Returns:
        tuple: Center coordinates and reference system (longitude, latitude, crs).
    """

    with rasterio.open(image_qr_path) as f:
        bounds = f.bounds
        center_lon = (bounds.left + bounds.right) / 2
        center_lat = (bounds.top + bounds.bottom) / 2
        source_crs = f.crs

    # Convert the coordinates to the WGS84 reference system
    target_crs = pyproj.CRS("EPSG:4326")
    transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)
    lon, lat = transformer.transform(center_lon, center_lat)
    return Point(lon, lat)


def get_tide_stations() -> list[dict[str, Any]]:
    res = requests.get("https://tides.server.hakai.app/stations?include_coords=true")
    stations = res.json()
    stations = [
        {
            "station_name": s["name"],
            "station_location": Point(s["longitude"], s["latitude"]),
        }
        for s in stations
    ]
    return stations


def get_closest_tide_station(image_qr_path: str) -> dict[str, Any]:
    """
    Get the closest tide station to a Planet Scope ARPS raster image.
    :param image_qr_path:
    :return:
    """
    raster_center = get_raster_center(image_qr_path)
    stations = get_tide_stations()
    station_dists = [
        {
            "station_name": s["station_name"],
            "station_location": s["station_location"],
            "distance": distance(
                (raster_center.y, raster_center.x),
                (s["station_location"].y, s["station_location"].x),
            ),
        }
        for s in stations
    ]
    return min(station_dists, key=lambda s: s["distance"])


def get_tide_height(image_qr_path: str) -> dict[str, Any]:
    """
    Get the tide height at the time of acquisition of a Planet Scope ARPS raster image.

    Args:
        image_path (str): Path to the raster image.

    Returns:
        float: Tide height in meters.
    """
    # Get the acquisition time of the image
    raster_acq_time = get_acquisition_time(image_qr_path)
    dt_str = raster_acq_time.strftime("%Y-%m-%dT%H:%M:%S")

    # Find the closest station
    closest_station = get_closest_tide_station(image_qr_path)
    station = closest_station["station_name"]

    # Get the tide height at the acquisition time for that station
    res = requests.get(
        f"https://tides.server.hakai.app/tides/at/{station}?date_time={dt_str}&tz=UTC"
    )
    tide_height = res.json()["height"]
    return {
        "tide_height": tide_height,
        "station_name": station,
        "station_distance": closest_station["distance"],
        "acquisition_time": raster_acq_time,
    }
