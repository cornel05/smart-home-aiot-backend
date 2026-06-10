import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from api.routes_sensor import router as sensor_router
from api.routes_device import router as device_router
from database.session import init_db

from services.ai_inference import AIInferenceService



logging.basicConfig(level=logging.INFO)

# --- MỚI: Khởi tạo AI Service ---
ai_service = AIInferenceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP] 1. Khởi tạo Database
    await init_db()

    loop = asyncio.get_running_loop()

    # [STARTUP] 2. Khởi chạy luồng MQTT kết nối phần cứng (Code cũ giữ nguyên)
    from mqtt.subscriber import start_subscriber
    thread = threading.Thread(target=start_subscriber, args=(loop,), daemon=True)
    thread.start()

    # [STARTUP] 3. Kích hoạt luồng chạy ngầm của AI
    ai_task = asyncio.create_task(ai_service.run_monitoring_loop())
    logging.info("🤖 [Backend] Đã khởi chạy luồng AI dự đoán hành vi ngầm.")

    yield # --- Server đang chạy và lắng nghe các API Request ở đây ---

    # [SHUTDOWN] 4. Hủy luồng AI khi tắt server để giải phóng RAM
    ai_task.cancel()
    logging.info("🛑 [Backend] Đã hủy luồng AI ngầm.")


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
