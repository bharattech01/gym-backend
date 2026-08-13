from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.schemas.ai_chat import ChatRequest
from app.services.ai_chat_service import AIChatService


router = APIRouter(prefix="/ai/chat", tags=["AI Chat"])


@router.post("/start")
def start_chat(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    existing_chat = (
        db.query(Chat)
        .filter(Chat.user_id == current_user["user_id"])
        .order_by(Chat.id.desc())
        .first()
    )

    if existing_chat:

        return {
            "chat_id": existing_chat.id,
            "is_new_chat": False
        }

    chat = Chat(
        user_id=current_user["user_id"]
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    welcome = (
        "Hey! I'm your IronPulse AI Coach 🤖💪\n\n"
        "I can help you with:\n"
        "• Personalized workout plans\n"
        "• Diet & nutrition advice\n"
        "• Form correction tips\n\n"
        "What would you like to work on today?"
    )

    first_message = ChatMessage(
        chat_id=chat.id,
        role="assistant",
        message=welcome
    )

    db.add(first_message)
    db.commit()

    return {
        "chat_id": chat.id,
        "is_new_chat": True
    }


@router.get("/history/{chat_id}")
def get_chat_history(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
        )
    history.reverse()

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return {
        "chat_id": chat.id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "message": msg.message,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.post("/message")
def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    chat = (
        db.query(Chat)
        .filter(
            Chat.id == request.chat_id,
            Chat.user_id == current_user["user_id"]
        )
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    # Save user message
    user_message = ChatMessage(
        chat_id=chat.id,
        role="user",
        message=request.message
    )

    db.add(user_message)
    db.commit()

    # Load conversation history
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    llm_messages = []

    for msg in history:
        llm_messages.append({
            "role": msg.role,
            "content": msg.message
        })

    # Ask Groq
    reply = AIChatService.ask_ai(
        llm_messages,
        request.message
    )

    # Save assistant reply
    assistant = ChatMessage(
        chat_id=chat.id,
        role="assistant",
        message=reply
    )

    db.add(assistant)
    db.commit()

    return {
        "reply": reply
    }