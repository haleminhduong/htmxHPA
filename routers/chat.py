from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from database import db  # Import the database singleton

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    # Generate a unique session ID if not exists
    if not request.session.get("chat_id"):
        request.session["chat_id"] = str(datetime.now().timestamp())

    # Get chat history
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

        # Save user message with new column names
        db.save_message(session_id, message, "user")

        # Save AI response (placeholder)
        ai_response = "This is an AI response placeholder. How can I help you today?"
        db.save_message(session_id, ai_response, "ai")

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
