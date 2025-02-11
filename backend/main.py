"""Main app."""
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.types import Message
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from initializers.logger import LOGGER
from constants.http_status_code import CLIENT_CLOSED_REQUEST_STATUS_CODE, COMMON_EXCEPTION_STATUS_CODE
from backend.flightPlanner import flight_router
from info import APP_NAME, APP_SUMMARY, APP_VERSION, APP_CONTACT
from constants.api_endpoints.flight_planner import FLIGHT_PLANNER_ROUTER
from anyio import EndOfStream
from mangum import Mangum
security = HTTPBasic()
DB_CHECKER = "/check-db"
app = FastAPI(
    title=APP_NAME,
    # description=app_description,
    summary=APP_SUMMARY,
    version=APP_VERSION,
    contact=APP_CONTACT,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
    )


async def set_body(request: Request, body: bytes):
    """Set body to print logs as we are using pydantic models."""
    async def receive() -> Message:
        return {"type": "http.request", "body": body}
    request._receive = receive


async def get_body(request: Request) -> bytes:
    """Response body from request."""
    body = await request.body()
    await set_body(request, body)
    print(f"{body=}")
    return body


@app.middleware("http")
async def print_response_logs(request: Request, call_next):
    """Priniting response logs for every api request."""
    try:
        response: Response = await call_next(request)
        LOGGER.debug(f"Response status code --> {response.status_code}")
        res_body = b''
        async for chunk in response.body_iterator:
            res_body += chunk
        LOGGER.debug(f"Response body --> {res_body}")
        return Response(content=res_body, headers=response.headers, status_code=response.status_code)

    except HTTPException as http_error:
        return Response(content=http_error.detail, status_code=http_error.status_code)
    except EndOfStream as error:
        return Response(content=error, status_code=CLIENT_CLOSED_REQUEST_STATUS_CODE)
    except Exception as error:
        return Response(content=f"{error}", status_code=COMMON_EXCEPTION_STATUS_CODE)


@app.middleware("http")
async def print_request_logs(request: Request, call_next):
    """Print Every request detail for every api request."""
    try:
        LOGGER.debug(f"Request url --> {request.url}")
        LOGGER.debug(f"Request base url --> {request.base_url}")
        LOGGER.debug(f"Requested url {request.url}")

        await set_body(request, await request.body())
        request_body = await get_body(request)
        LOGGER.debug(f"Request body --> {request_body}")
        response = await call_next(request)
        return response

    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION.execute(status_code=http_error.status_code, error_message=http_error.detail)
    except EndOfStream as error:
        return HTTPException(status_code=CLIENT_CLOSED_REQUEST_STATUS_CODE, detail=f"{error}")
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION.execute(status_code=COMMON_EXCEPTION_STATUS_CODE,
                                             error_message=f"{error}")


app.include_router(flight_router, prefix=FLIGHT_PLANNER_ROUTER)
handler = Mangum(app=app)
