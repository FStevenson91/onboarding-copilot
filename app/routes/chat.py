from fastapi import APIRouter
from app.models.schemas import ChatMessage
from app.services.llm import get_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])

# --- Historial temporal en memoria (después será base de datos) ---
chat_history: list[dict] = []

@router.post("/message")
def send_message(message: ChatMessage):
    chat_history.append(message.model_dump())

    # Por ahora respuesta dummy, después conectamos el LLM
    assistant_response = ChatMessage(
        role= "assistant",
        content= get_chat_response(chat_history),
        source= None
    )
    chat_history.append(assistant_response.model_dump())

    return {
        "response": assistant_response.model_dump(),
        "history_length": len(chat_history)
    }

@router.get("/history")
def get_history():
    return {"history": chat_history}