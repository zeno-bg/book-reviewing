import logging

import uvicorn as uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_pagination import add_pagination
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from exceptions import ObjectNotFoundException, DatabaseException
from routers.users import router as users_router

file_handler = logging.FileHandler('errors.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)

app = FastAPI(root_path="/api/v1")
add_pagination(app)
app.include_router(users_router, tags=["Users"], prefix="/users")


def log_errors(exception: RequestValidationError | ObjectNotFoundException | DatabaseException):
    match exception:
        case RequestValidationError():
            logger.error(exception.errors())
        case ObjectNotFoundException():
            logger.error(exception.detail)
        case DatabaseException():
            logger.error(exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    background_task = BackgroundTask(log_errors, exception)

    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                        content=jsonable_encoder({"errors": exception.errors()}),
                        background=background_task)


@app.exception_handler(ObjectNotFoundException)
async def custom_http_exception_handler(request: Request, exception: ObjectNotFoundException):
    background_task = BackgroundTask(log_errors, exception)
    return JSONResponse(status_code=HTTP_404_NOT_FOUND,
                        content=jsonable_encoder({'detail': exception.detail}),
                        background=background_task)


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exception: DatabaseException):
    background_task = BackgroundTask(log_errors, exception)
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                        content=jsonable_encoder({'detail': "Internal Server Error"}),
                        background=background_task)




if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
