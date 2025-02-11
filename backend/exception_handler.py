# from fastapi import HTTPException

# COMMON_EXCEPTION_STATUS_CODE = 500  # Define your common exception status code


# def handle_http_exception(status_code, error_message):
#     return {"status_code": status_code, "error_message": error_message}


# def exception_handler(func):
#     async def wrapper(*args, **kwargs):
#         try:
#             return await func(*args, **kwargs)
#         except HTTPException as http_error:
#             return handle_http_exception(status_code=http_error.status_code, error_message=http_error.detail)
#         except Exception as error:
#             return handle_http_exception(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=str(error))
#     return wrapper
