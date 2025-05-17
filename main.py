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

# Хранилище активных видео-комнат
active_video_rooms = {}

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
    user_id = data.get('user_id')
    
    if not user_id:
        return {"error": "user_id is required"}
        
    print(f"Заявка от пользователя {user_id}: {description}")

    await db.add_request(description, ticket_id, user_id)

    suggested_reply = "Спасибо! Мы ищем помощника для вашей проблемы..."

    return {
        "status": "waiting",
        "ticket_id": ticket_id,
        "message": suggested_reply
    }

@app.post("/create-video-room")
async def create_video_room(request: Request):
    data = await request.json()
    ticket_id = data.get('ticket_id')
    helper_id = data.get('helper_id')

    # Получаем информацию о заявке из базы
    request_info = await db.get_request_by_ticket(ticket_id)
    if not request_info:
        return {"error": "Заявка не найдена"}

    # Проверяем, что helper не является автором заявки
    if helper_id == request_info["user_id"]:
        return {
            "error": "Вы не можете помогать с собственной заявкой",
            "status": "self_help_forbidden"
        }

    # Создаем уникальный идентификатор комнаты
    room_id = f"room_{uuid4().hex[:8]}"
    
    # Сохраняем информацию о комнате
    active_video_rooms[room_id] = {
        "ticket_id": ticket_id,
        "requester_id": request_info["user_id"],
        "helper_id": helper_id,
        "created_at": request_info["created_at"]
    }

    return {
        "room_id": room_id,
        "domain": "meet.jit.si",
        "requester_id": request_info["user_id"]
    }

@app.post("/end-video-room")
async def end_video_room(request: Request):
    data = await request.json()
    room_id = data.get('room_id')
    user_id = data.get('user_id')

    if room_id in active_video_rooms:
        room = active_video_rooms[room_id]
        # Проверяем, что запрос на завершение пришел от участника комнаты
        if user_id in [room["requester_id"], room["helper_id"]]:
            del active_video_rooms[room_id]
            return {"status": "success", "message": "Комната закрыта"}
    
    return {"status": "error", "message": "Комната не найдена или нет прав"}

@app.get("/check-video-room/{room_id}")
async def check_video_room(room_id: str, user_id: str):
    if room_id in active_video_rooms:
        room = active_video_rooms[room_id]
        # Проверяем, что пользователь является участником комнаты
        if user_id in [room["requester_id"], room["helper_id"]]:
            return {
                "status": "active",
                "room_info": room
            }
    return {"status": "not_found"}

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Ответ: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.get("/get-help-requests")
async def get_help_requests():
    requests_list = await db.get_all_requests()
    return {"requests": requests_list}        

