# main.py
from alerts.email_alert import send_alert_email
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import asyncio
import json
import threading

from database import engine, get_db, Base
from models import Packet, Alert
from capture.sniffer import start_sniffing, get_buffer, clear_buffer
from detection.rules import run_all_rules

# Create tables
Base.metadata.create_all(bind=engine)

# Connected websocket clients
connected_clients: list[WebSocket] = []

# ─── Background Tasks ─────────────────────────────────
async def analyze_traffic():
    while True:
        await asyncio.sleep(5)
        buffer = get_buffer()
        if buffer:
            alerts = run_all_rules(buffer)
            for alert in alerts:
                await broadcast_alert(alert)
                if alert["severity"] in ["CRITICAL", "HIGH"]:
                    await send_alert_email(alert)
            clear_buffer()

# ─── Lifespan ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(
        target=start_sniffing,
        kwargs={"interface": None},
        daemon=True
    )
    thread.start()
    asyncio.create_task(analyze_traffic())
    print("🐾 PacketHound is running!")
    yield

# ─── App ──────────────────────────────────────────────
app = FastAPI(title="PacketHound 🐾", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── WebSocket ────────────────────────────────────────
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast_alert(alert: dict):
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(alert))
        except:
            connected_clients.remove(client)

# ─── REST Endpoints ───────────────────────────────────
@app.get("/")
def root():
    return {"message": "PacketHound 🐾 is live!"}

@app.get("/api/alerts")
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

@app.get("/api/packets")
def get_packets(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Packet).order_by(Packet.timestamp.desc()).limit(limit).all()

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_packets": db.query(Packet).count(),
        "total_alerts": db.query(Alert).count(),
        "status": "running"
    }