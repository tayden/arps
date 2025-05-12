from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter
from rich import print
from psarps import lib

app = App()


def __validate_path(type_, value):
    if not value.is_file():
        raise ValueError("File does not exist.")
    if value.suffix not in [".tif", ".tiff"] or not value.stem.endswith("_qa"):
        raise ValueError("File must be a Planet Scope ARPS QA image.")


@app.command
def info(
    image_path: Annotated[Path, Parameter(validator=__validate_path)],
):
    """Get tide height info for a Planet Scope ARPS raster image.

    Parameters
    ----------
    image_path : Path
        Path to the QA raster image.
    """
    tides_info = lib.get_tide_height(str(image_path))
    print(
        f"Acquisition Time: {tides_info['acquisition_time'].strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Tide Height (m): {tides_info['tide_height']:.2f}")
    print(f"Station Name: [cyan]{tides_info['station_name']}[/cyan]")
    print(f"Station Distance (m): {tides_info['station_distance'].m:.0f}")


if __name__ == "__main__":
    app()
