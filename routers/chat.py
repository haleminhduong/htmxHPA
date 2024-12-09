from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from database import db
from services.vector_service import VectorService

router = APIRouter()
templates = Jinja2Templates(directory="templates")
vector_service = VectorService()


@router.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    if not request.session.get("chat_id"):
        request.session["chat_id"] = str(datetime.now().timestamp())
    chat_history = db.get_chat_history(request.session["chat_id"])
    return templates.TemplateResponse(
        "/chat/chat.html",
        {"request": request, "chat_history": chat_history}
    )


@router.post("/chat/send")
async def chat_message(request: Request):
    try:
        data = await request.form()
        message = str(data["message"]).strip()
        if not message:
            raise HTTPException(
                status_code=400, detail="Message cannot be empty")

        # Get or create session ID
        session_id = request.session.get(
            "chat_id", str(datetime.now().timestamp()))

        try:
            # Save user message to database and get message ID
            user_message_id = db.save_message(session_id, message, "user")

            # Only store vector if we have a valid message ID
            if user_message_id:
                # Create and store embedding for user message
                user_embedding = vector_service.create_embedding(message)
                vector_service.store_vector(
                    entry_id=user_message_id,
                    vector=user_embedding,
                    collection_name="chat_messages"
                )
        except Exception as e:
            print(f"Error saving user message: {str(e)}")
            # Continue with chat even if vector storage fails

        # Generate AI response (placeholder)
        ai_response = "This is an AI response placeholder. How can I help you today?"

        try:
            # Save AI response to database
            ai_message_id = db.save_message(session_id, ai_response, "ai")

            # Only store vector if we have a valid message ID
            if ai_message_id:
                # Create and store embedding for AI response
                ai_embedding = vector_service.create_embedding(ai_response)
                vector_service.store_vector(
                    entry_id=ai_message_id,
                    vector=ai_embedding,
                    collection_name="chat_messages"
                )
        except Exception as e:
            print(f"Error saving AI response: {str(e)}")
            # Continue with chat even if vector storage fails

        # Return HTML response
        html = f"""
        <div class="flex w-full mt-2 space-x-3 max-w-md ml-auto justify-end">
            <div>
                <div class="bg-blue-600 text-white p-3 rounded-l-lg rounded-br-lg">
                    <p class="text-sm">{message}</p>
                </div>
            </div>
        </div>
        <div class="flex w-full mt-2 space-x-3 max-w-md">
            <div>
                <div class="bg-gray-200 p-3 rounded-r-lg rounded-bl-lg">
                    <p class="text-sm text-gray-800">{ai_response}</p>
                </div>
            </div>
        </div>
        """
        return HTMLResponse(html)
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
