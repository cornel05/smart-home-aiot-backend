import asyncio
import joblib
import pandas as pd
import traceback
from sqlalchemy import text

# IMPORT KẾT NỐI DATABASE CỦA NHÓM BẠN
from database.session import engine

ROOM_STATUS = {0: "Empty", 1: "Active", 2: "Sleeping"}

class AIInferenceService:
    def __init__(self):
        try:
            self.model = joblib.load("ai/activity_model.pkl")
            print("🤖 [AI Service] Đã tải mô hình activity_model.pkl thành công!")
        except Exception as e:
            self.model = None
            print(f"❌ [AI Service] Lỗi load mô hình: {e}")

    # ==========================================
    # CẬP NHẬT: LẤY DỮ LIỆU THẬT TỪ TIMESCALEDB
    # ==========================================
    async def get_latest_data(self):
        try:
            async with engine.connect() as conn:
                query = text("""
                    SELECT temperature, humidity, light_intensity 
                    FROM sensor_telemetry 
                    ORDER BY "timestamp" DESC 
                    LIMIT 1;
                """)
                result = await conn.execute(query)
                row = result.fetchone()
                
                if row:

                    return {
                        "temp": float(row.temperature or 0), 
                        "hum": float(row.humidity or 0), 
                        "light": float(row.light_intensity or 0), 
                        "ir": 0  
                    }
                else:
                    print("⚠️ [AI Service] Bảng sensor_telemetry đang trống!")
                    return None
                    
        except Exception as e:
            print(f"❌ [AI Service] Lỗi truy vấn Database: {e}")
            return None

    async def run_monitoring_loop(self):
        print("▶️ [AI Service] Bắt đầu theo dõi hành vi...")
        while True:
            if self.model is not None:
                try:
                    data = await self.get_latest_data()
                    
                    # Nếu có dữ liệu thì mới dự đoán
                    if data is not None:
                        df = pd.DataFrame([data])
                        
                        # Lấy ĐẦY ĐỦ 4 thông số (Bổ sung thêm IR)
                        temp = data.get("temp", 0)
                        hum = data.get("hum", 0)
                        light = data.get("light", 0)
                        ir = data.get("ir", 0)
                        
                        # AI Dự đoán trạng thái
                        pred_code = self.model.predict(df[['temp', 'hum', 'light', 'ir']])[0]
                        current_state = ROOM_STATUS.get(pred_code, "Unknown")
                        
                        print(f"🔮 [AI Predict] {current_state} (Nhiệt: {temp}°C, Ẩm: {hum}%, Sáng: {light}, IR: {ir})")

                        # ==========================================
                        # Scenario Automation 
                        # ==========================================
                        if current_state == "Empty":
                            print("📡 [AI Action] Phòng trống an toàn -> TẮT toàn bộ thiết bị.")
                                
                        elif current_state == "Active":
                            print("📡 [AI Action] Chế độ sinh hoạt.")
                            if light < 100:
                                print("   -> BẬT ĐÈN (Trời tối)")
                            else:
                                print("   -> TẮT ĐÈN (Đủ sáng)")
                                
                            if temp >= 26.0 or hum >= 70.0:
                                print(f"   -> BẬT QUẠT (Chống oi bức)")
                            else:
                                print(f"   -> TẮT QUẠT (Phòng thoáng mát)")

                        elif current_state == "Sleeping":
                            print("📡 [AI Action] Chế độ ban đêm.")                        
                            if temp >= 27.0 or hum >= 75.0: 
                                print(f"   -> BẬT QUẠT (Phòng hầm bí ban đêm)")
                            else:
                                print(f"   -> TẮT QUẠT (Tránh cảm lạnh)")

                except Exception as e:
                    print(f"❌ Lỗi xử lý AI: {e}")
                    traceback.print_exc()

            await asyncio.sleep(10)