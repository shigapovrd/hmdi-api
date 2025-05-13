from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from Database import Database

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_CONFIG = {
    "user": "hmdi_db_user",
    "password": "uXAtRHPu7lUaXgs9BWA1z4eO9v3SNmam",
    "database": "hmdi_db",
    "host": "dpg-d0hlbqbuibrs739s2ir0-a.oregon-postgres.render.com",
    "port": 5432
}

db = Database(DB_CONFIG)

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.post("/request-help")
async def request_help(request: Request):
    data = await request.json()
    ticket_id = f"req_{uuid4().hex[:6]}"
    description = data.get('description', 'Нет описания')
    print(f"Заявка от: {description}")

    # Добавляем заявку в базу данных
    await db.add_request(description, ticket_id)

    # Заглушка для AI-ответа
    suggested_reply = "Спасибо! Мы ищем помощника для вашей проблемы..."

    return {
        "status": "waiting",
        "ticket_id": ticket_id,
        "message": suggested_reply
    }

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Ответ: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")