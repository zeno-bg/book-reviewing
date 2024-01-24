import uvicorn as uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from exceptions import ObjectNotFoundException, DatabaseException
from routers.users import router as users_router

app = FastAPI(root_path="/api/v1")
app.include_router(users_router, tags=["Users"], prefix="/users")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    print("error4e!")
    print(exception.errors())

    return await request_validation_exception_handler(request, exception)
    #return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    #                    content=jsonable_encoder({"errors": exception.errors()}))
    # TODO: logging


@app.exception_handler(ObjectNotFoundException)
async def custom_http_exception_handler(request: Request, exception: ObjectNotFoundException):
    print("NOT FOUND4E!")
    raise HTTPException(status_code=404, detail=exception.detail)


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exception: DatabaseException):
    print("DATABASE EXCEPTION!")
    print(exception)
    raise HTTPException(status_code=500, detail="Database exception occurred!")




if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
