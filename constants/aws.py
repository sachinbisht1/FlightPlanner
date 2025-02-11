"""All constants of AWS."""
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.environ.get("DEFAULT_REGION")
BUCKET_NAME = "3d-mapping-prod"
RECCE_PREFIX = "flight-planner/recce/"
WPML_FOLDER = RECCE_PREFIX+"Wpml_folders"
IMAGE_EXIF_INFO = RECCE_PREFIX+"Exif_folder"
WPML_PATH = RECCE_PREFIX+"wpml_path"
KML_PATH = RECCE_PREFIX+"kml_path"


