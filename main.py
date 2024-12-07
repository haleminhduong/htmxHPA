# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("/chat/chat.html", {"request": request})


@app.get("/journal", response_class=HTMLResponse)
async def journal(request: Request):
    return templates.TemplateResponse("/journal/journal.html", {"request": request})


@app.get("/social", response_class=HTMLResponse)
async def social(request: Request):
    return templates.TemplateResponse("/social/social.html", {"request": request})


@app.get("/mood", response_class=HTMLResponse)
async def mood(request: Request):
    return templates.TemplateResponse("/mood/mood.html", {"request": request})

