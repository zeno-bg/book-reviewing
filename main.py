import uvicorn as uvicorn
from fastapi import FastAPI

from routers.users import router as users_router

app = FastAPI(root_path="/api/v1")
app.include_router(users_router, tags=["Users"], prefix="/users")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
