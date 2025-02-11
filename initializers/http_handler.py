"""Initializer to handle exceptions."""
from controllers.api_request_error import HandleHTTPException
HANDLE_HTTP_EXCEPTION = HandleHTTPException().execute
