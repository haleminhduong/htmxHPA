from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/social", response_class=HTMLResponse)
async def social(request: Request):
    return templates.TemplateResponse("/social/social.html", {"request": request})
