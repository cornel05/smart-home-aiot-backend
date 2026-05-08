# smart-home-aiot-backend

# 1. Start infra
docker compose up -d

# 2. Start backend
pip install -r requirements.txt
uvicorn main:app --reload

# 3. Start gateway (separate terminal)
python gateway/gateway.py

# 4. Start frontend
cd frontend && npm install && npm run dev