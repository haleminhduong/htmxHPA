from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.vector_service import VectorService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_vector_service():
    service = VectorService()
    try:
        yield service
    finally:
        pass


@router.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("/chat/chat.html", {"request": request})


@router.post("/chat/send")
async def chat_message(
    request: Request,
    vector_service: VectorService = Depends(get_vector_service)
):
    try:
        data = await request.form()
        message = str(data["message"]).strip()

        if not message:
            raise HTTPException(
                status_code=400, detail="Message cannot be empty")

        # Create embedding and store user message
        message_embedding = vector_service.create_embedding(message)
        vector_service.store_message(
            message=message,
            is_ai=False,
            vector=message_embedding
        )

        # Search for similar messages
        similar_messages = vector_service.search_similar(
            vector=message_embedding,
            limit=3
        )

        # Generate AI response based on context
        ai_response = "This is an AI response placeholder. "
        # > 1 because the first will be the current message
        if similar_messages and len(similar_messages) > 1:
            ai_response += f"I found {len(similar_messages) -
                                      1} similar messages in our chat history."

        # Store AI response
        ai_embedding = vector_service.create_embedding(ai_response)
        vector_service.store_message(
            message=ai_response,
            is_ai=True,
            vector=ai_embedding
        )

        # Generate HTML response
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
