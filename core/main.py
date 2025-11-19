from fastapi import FastAPI, Depends, Response, Request, HTTPException, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from tasks.routs import router as task_routs
from users.routs import router as user_routs
from users.models import UserModel
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.interval import IntervalTrigger
from core.config import settings

import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


jobstores = {
    "default": RedisJobStore(jobs_key="apscheduler.jobs", run_times_key="apscheduler.run_times", host="redis", port=6379, db=1)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

def my_task():
    logging.info("task executed at %s", time.strftime('%Y-%m-%d %H:%M:%S'))

tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to task management — create, update, delete, and list tasks.",
        "externalDocs": {
            "description": "More about tasks",
            "url": "https://example.com/docs/tasks",
        },
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application start up")
    scheduler.add_job(my_task, IntervalTrigger(seconds=10), id="my_task", replace_existing=True)
    scheduler.start()

    yield

    scheduler.shutdown()
    print("Application shutdown")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Application start up")
#     yield
#     print("Application shutdown")


app = FastAPI(
    title="Todo Application",
    description="""
    A simple API for managing tasks.  
    You can create, update, delete, and retrieve tasks using this service.

    ### Features
    - Create and list tasks  
    - Update task status  
    - Delete tasks  
        """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Mohammad Amin Tavakoli",
        "url": "https://linkedin.com/in/mohamad-amin-tavakoli",
        "email": "amin76tavakoli76@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)


app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(task_routs)
app.include_router(user_routs)


# from auth.jwt_auth import get_authenticated_user
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# security = HTTPBearer()

# query_schema = APIKeyQuery(name="api_key")


# @app.get("/public")
# def public_route():
#     return {"message": "this is a public route"}

# @app.get("/private")
# def private_route(user = Depends(get_authenticated_user)):
#     print(user.id)
#     return {"message": "this is a private route"}

# @app.post("/set-cookie")
# def set_cookie(response: Response):
#     response.set_cookie(key="test", value="something")
#     return {"message": "Cookie has been set successfully"}

# @app.get("/get-cookie")
# def get_cookie(request: Request):
#     print(request.cookies.get("test"))
#     return {"message": "Cookie has been set successfully"}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


origins = ["http://127.0.0.1:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": exc.status_code,
        "detail": str(exc.detail)
    }

    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.exception_handler(RequestValidationError)
async def http_validation_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "detail": "There was a problem with your form request",
        "content": exc.errors()
    }

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=error_response)


from fastapi import BackgroundTasks
import random

task_counter = 1

def start_task(task_id):
    print(f"doing the process: {task_id}")
    time.sleep(random.randint(3, 10))
    print(f"finish task: {task_id}")


@app.get("/initiate-task", status_code=200)
async def initiate_task(background_tasks: BackgroundTasks):
    global task_counter
    background_tasks.add_task(start_task, task_id = task_counter)
    task_counter += 1
    return JSONResponse(content={"detail": "task is done"})


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

import httpx

redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend, prefix="fastapi-cache")

async def request_current_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        current_weather = data.get("current", {})
        return current_weather
    else:
        return None

@app.get("/fetch-current-weather", status_code=200)
@cache(expire=10)
async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
    current_weather = await request_current_weather(latitude, longitude)
    if current_weather:
        return JSONResponse(content={"current_weather": current_weather})
    else:
        return JSONResponse(content={"detail": "Failed to fetch weather"}, status_code=500)

from core.email_util import send_email

@app.get("/test-send-mail", status_code=200)
async def test_send_mail():
    await send_email(
        subject="Test email from fastapi",
        recipients=["recipient@example.com"],
        body="This is a test email sent using email util function"
    )
    return JSONResponse(content={"detail": "Email has been sent"})