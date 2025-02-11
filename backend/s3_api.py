"""Api router for all S3 apis."""
from constants import aws as AWS
from initializers import aws
# from fastapi import UploadFile
from constants import utilities_constants
# from constants.aws import AWS_REGION_NAME
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.http_status_code import COMMON_EXCEPTION_STATUS_CODE
from constants.aws import AWS_REGION_NAME


def get_flight_data_from_s3(name: str):
    try:
        key = f"{AWS.WPML_FOLDER}/{name}"
        s3_client = aws.S3_CLIENT
        presigned_url = s3_client.generate_presigned_url("get_object", Params={'Bucket': AWS.BUCKET_NAME, 'Key': key},
                                                         ExpiresIn=utilities_constants.REFRESH_TOKEN_EXPIRE_MINUTES)
        return presigned_url
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


def upload_flight_data_to_s3(file, name: str):
    s3_client = aws.S3_CLIENT
    try:
        name = f"{AWS.WPML_FOLDER}/{name}"
        s3_client.upload_fileobj(file, AWS.BUCKET_NAME, name)
        return f"https://{AWS.WPML_FOLDER}.s3.{AWS_REGION_NAME}.amazonaws.com/{name}"
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)
