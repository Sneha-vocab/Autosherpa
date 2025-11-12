import time
from fastapi import FastAPI, Request
from .webhook import router as webhook_router
from .chat import router as chat_router
from .db import init_db

app = FastAPI(title="AutoSherpa Backend")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    request.state.process_time = duration
    return response


app.include_router(webhook_router)
app.include_router(chat_router)
@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"service": "autosherpa", "status": "ok"}
