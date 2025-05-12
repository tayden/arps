# PSARPS - Planet Scope ARPS Satellite Imagery Metadata Tool

A Python library and CLI tool for retrieving tide metadata for Planet Scope ARPS (Automated Rapid Preprocessing System) satellite imagery.

## Features

- Extract acquisition time from ARPS QA raster images
- Find the closest tide station to the image location
- Get the tide height at the time of image acquisition
- Simple command-line interface

## Installation

### From PyPI

```bash
pip install psarps
```

### From GitHub

```bash
pip install git+https://github.com/tayden/psarps.git
```

## Usage

### Command Line Interface

Get tide information for a Planet Scope ARPS QA raster image:

```bash
arps info path/to/your_image_qa.tif
```

Example output:
```
Acquisition Time: 2023-05-01 14:30:45
Tide Height (m): 2.34
Station Name: Victoria
Station Distance (m): 5432
```

### Python API

```python
import psarps

# Get tide information
tide_info = psarps.get_tide_height("path/to/your_image_qa.tif")

# Access the tide data
acquisition_time = tide_info['acquisition_time']
tide_height = tide_info['tide_height']
station_name = tide_info['station_name']
station_distance = tide_info['station_distance']

# Get just the acquisition time
acq_time = psarps.get_acquisition_time("path/to/your_image_qa.tif")

# Get the closest tide station
closest_station = psarps.get_closest_tide_station("path/to/your_image_qa.tif")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/tayden/psarps.git
cd psarps

# Install with development dependencies
uv pip install ".[dev]"
```

### Common Development Commands

- Run tests: `pytest`
- Lint code: `ruff check src/ tests/`
- Format code: `ruff format src/ tests/`

## Requirements

- Python 3.13+
- See pyproject.toml for dependencies

## License

MIT