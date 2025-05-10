from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/request-help")
async def request_help(request: Request):
    data = await request.json()
    ticket_id = f"req_{uuid4().hex[:6]}"
    print(f"Заявка от: {data['description']}")
    
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