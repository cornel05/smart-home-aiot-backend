import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_sensor import router as sensor_router
from api.routes_device import router as device_router
from database.session import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    loop = asyncio.get_running_loop()

    from mqtt.subscriber import start_subscriber
    thread = threading.Thread(target=start_subscriber, args=(loop,), daemon=True)
    thread.start()

    yield


app = FastAPI(title="Smart Home AIoT", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor_router, prefix="/api")
app.include_router(device_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
