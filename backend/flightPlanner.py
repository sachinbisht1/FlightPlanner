from fastapi import APIRouter, HTTPException, Request
from constants.api_endpoints import flight_planner as endpoints
from models import flight_planner as models

from flightplannerdir.flightplanner import flight_plan
import ast
from fastapi import UploadFile
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.http_status_code import COMMON_EXCEPTION_STATUS_CODE
from constants.utilities_constants import FOCAL_INFO, IMAGE_HEIGHT, IMAGE_WIDTH
# from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from backend import s3_api
from initializers import aws
from constants import aws as Exif_AWS
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
from datetime import datetime
flight_router = APIRouter()


@flight_router.post(endpoints.GENERATE_WPML_DATA)
def generate_wpml_file(data: models.flight_path):
    coordinates = ast.literal_eval(data.coordinates)
    altitude = data.altitude
    quality = data.quality
    Image_width = data.Image_height
    Image_height = data.Image_width
    focal_length = data.focal_length
    overlap_percentage = (data.overlap_percentage)
    project_name = data.project_name
    # print(type(coordinates), Image_height,(type(Image_height)))
    result = flight_plan(coordinates, altitude, quality, data.sensor_width, focal_length,
                         overlap_percentage, project_name,
                         Image_width, Image_height)
    return JSONResponse(content=result)


@flight_router.post(endpoints.GET_DATA)
def get_wpml_file(data: models.PreassignedUrl):
    try:
        name = data.project_name
        name = f"{name}/{name}_wpml_files.zip"
        url = s3_api.get_flight_data_from_s3(name)
        response = {"url": url}
        return JSONResponse(content=response)
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@flight_router.post(endpoints.UPLOAD_IMAGE)
def upload_image(request: Request, file: UploadFile):
    try:
        s3_client = aws.S3_CLIENT
        name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        name = f"{name}_exif.jpg"
        s3_client.upload_fileobj(file.file, Exif_AWS.BUCKET_NAME, name)
        response = s3_client.get_object(Bucket=Exif_AWS.BUCKET_NAME, Key=name)
        image_data = response['Body'].read()
        focal_info = ""
        # gps_info = ""
        with Image.open(BytesIO(image_data)) as img:
            exif_data = img._getexif()
            if exif_data is not None:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "FocalLength":
                        focal_info = float(value)
                        width, height = img.size
                        image_details = {
                            FOCAL_INFO: focal_info,
                            IMAGE_WIDTH: width,
                            IMAGE_HEIGHT: height
                        }
                        s3_client.delete_object(Bucket=Exif_AWS.DP_BUCKET, Key=name)
                        response = JSONResponse(content=image_details)
                        return response
                if focal_info:
                    print("exif data is there")
                else:
                    response = "No EXIF data found"
                    return JSONResponse(content=response)
            else:
                response = "No EXIF data found"
                return JSONResponse(content=response)
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)
