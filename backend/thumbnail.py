import boto3
import zipfile
import io
from PIL import Image
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
def unzip_and_upload(s3_bucket, s3_zip_key, s3_unzip_folder):
    """
    Unzips a file from S3 and uploads its contents back to S3.
    
    Args:
        s3_bucket: Name of the S3 bucket.
        s3_zip_key: Key of the zip file in S3.
        s3_unzip_folder: Folder where the unzipped files will be uploaded.
    """
    # Get the zip file from S3
    zip_obj = aws.get_object(Bucket=s3_bucket, Key=s3_zip_key)
    zip_file = zipfile.ZipFile(io.BytesIO(zip_obj['Body'].read()))
    
    # Iterate through each file in the zip
    for file_name in zip_file.namelist():
        if file_name.endswith('/'):  # Skip folders
            continue
        file_data = zip_file.read(file_name)
        
        # Upload the file to S3
        aws.put_object(
            Bucket=s3_bucket,
            Key=f"{s3_unzip_folder}/{file_name}",
            Body=file_data
        )
    print("Unzipping and upload complete!")

def resize_and_upload_images(s3_bucket, s3_source_folder, s3_target_folder, resize_width, resize_height):
    """
    Downloads images from a folder in S3, resizes them, and uploads them back to a target folder in S3.
    
    Args:
        s3_bucket: Name of the S3 bucket.
        s3_source_folder: Folder where source images are stored.
        s3_target_folder: Folder where resized images will be uploaded.
        resize_width: Target width for the resized images.
        resize_height: Target height for the resized images.
    """
    # List objects in the source folder
    response = aws.list_objects_v2(Bucket=s3_bucket, Prefix=s3_source_folder)
    for obj in response.get('Contents', []):
        file_key = obj['Key']
        if file_key.endswith('/'):  # Skip folders
            continue
        
        # Get the image from S3
        img_obj = aws.get_object(Bucket=s3_bucket, Key=file_key)
        img_data = img_obj['Body'].read()
        
        # Resize the image using Pillow
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((resize_width, resize_height), Image.ANTIALIAS)
        
        # Save the resized image to a BytesIO object
        output_buffer = io.BytesIO()
        img.save(output_buffer, format=img.format)
        output_buffer.seek(0)
        
        # Upload the resized image to the target folder
        target_key = file_key.replace(s3_source_folder, s3_target_folder, 1)
        aws.put_object(
            Bucket=s3_bucket,
            Key=target_key,
            Body=output_buffer
        )
    print("Resizing and upload complete!")

# Example usage
s3_bucket_name = "your-bucket-name"
s3_zip_path = "path/to/large-zip-file.zip"
s3_unzip_folder = "unzipped-images"
s3_resized_folder = "resized-images"

# Step 1: Unzip and upload files
unzip_and_upload(s3_bucket_name, s3_zip_path, s3_unzip_folder)

# Step 2: Resize and upload images
resize_width = 800  # Example width
resize_height = 600  # Example height
resize_and_upload_images(s3_bucket_name, s3_unzip_folder, s3_resized_folder, resize_width, resize_height)