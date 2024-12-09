from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/journal", response_class=HTMLResponse)
async def journal(request: Request):
    return templates.TemplateResponse("/journal/journal.html", {"request": request})
