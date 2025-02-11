"""All account request models."""
from pydantic import BaseModel


class flight_path(BaseModel):
    """Account signup Api request model."""
    project_name: str
    coordinates: str
    altitude: float
    quality: str
    overlap_percentage: float
    sensor_width: float
    focal_length: float
    sensor_height: float
    Image_height: float
    Image_width: float


class PreassignedUrl(BaseModel):
    """Account signup Api request model."""
    project_name: str
