import logging
import asyncio
from datetime import datetime
import paho.mqtt.client as mqtt
from core.config import settings
from services.rule_engine import evaluate

logger = logging.getLogger(__name__)

_loop: asyncio.AbstractEventLoop | None = None

# Một kho lưu trữ tạm thời vì data được gửi lẻ tẻ
_node_buffer: dict[int, dict] = {}

def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe("#")
        logger.info("MQTT subscriber connected to LOCAL broker - Lắng nghe đa kênh (#)")
    else:
        logger.error("MQTT connect failed: %s", reason_code)

def _on_message(client, userdata, msg):
    try:
        topic = msg.topic
        raw_str = msg.payload.decode().strip()
        logger.info(">>> Nhận: Topic [%s] | Dữ liệu: %s", topic, raw_str)
        
        try:
            val = float(raw_str)
        except ValueError:
            return # Bỏ qua nếu không phải số

        # Phân loại dữ liệu theo đuôi của Topic
        field = None
        if topic.endswith("temperature"): field = "temperature"
        elif topic.endswith("humidity"): field = "humidity"
        elif topic.endswith("light"): field = "light_intensity"
        elif topic.endswith("ir-motion"): field = "ir"
        
        if not field:
            return

        payload = {"node_id": settings.NODE_ID, field: val}
        
        if _loop and not _loop.is_closed():
            asyncio.run_coroutine_threadsafe(_persist(payload), _loop)
            
    except Exception as exc:
        logger.exception("Error processing MQTT message: %s", exc)

async def _persist(payload: dict):
    from database.session import AsyncSessionLocal
    from database.models import SensorTelemetry

    node_id = payload.get("node_id", settings.NODE_ID)
    
    # Khởi tạo buffer nếu chưa có
    if node_id not in _node_buffer:
        _node_buffer[node_id] = {}
        
    # Cập nhật thông số mới vào buffer
    for k, v in payload.items():
        if k != "node_id":
            _node_buffer[node_id][k] = v
            
    buf = _node_buffer[node_id]
    
    # CHỈ LƯU VÀO DATABASE KHI GOM ĐỦ CẢ NHIỆT ĐỘ & ĐỘ ẨM
    if "temperature" in buf and "humidity" in buf:
        async with AsyncSessionLocal() as session:
            row = SensorTelemetry(
                timestamp=datetime.utcnow(),
                node_id=node_id,
                temperature=buf.get("temperature"),
                humidity=buf.get("humidity"),
                light_intensity=buf.get("light_intensity"),
            )
            session.add(row)
            await session.commit()
            logger.info(">>> ĐÃ LƯU DATABASE: T:%.1f H:%.1f L:%s", 
                        buf.get("temperature"), buf.get("humidity"), buf.get("light_intensity"))
        
        # Xóa buffer sau khi lưu để chuẩn bị gom vòng mới
        _node_buffer[node_id] = {}

def start_subscriber(loop: asyncio.AbstractEventLoop):
    global _loop
    _loop = loop
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if settings.MQTT_USER:
        client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
    client.loop_forever()