from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/mood", response_class=HTMLResponse)
async def mood(request: Request):
    return templates.TemplateResponse("/mood/mood.html", {"request": request})
