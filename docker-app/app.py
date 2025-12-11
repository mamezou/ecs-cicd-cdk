from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import datetime
import platform
import os
import time
import psutil
import fastapi

# アプリ起動時刻を記録
start_time = datetime.datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    yield
    # 終了時の処理


app = FastAPI(lifespan=lifespan)

# staticファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request, name: str = "FastAPI-demo"):
    current_time = datetime.datetime.now()
    python_version = platform.python_version()
    aws_platform = os.environ.get('PLATFORM', 'Amazon Web Services')

    return templates.TemplateResponse("hello.html", {
        "request": request,
        "platform": aws_platform,
        "fastapi_version": fastapi.__version__,
        "python_version": python_version,
        "fastapi_url": "https://fastapi.tiangolo.com/",
        "time": current_time,
        "name": name
    })


@app.get("/health")
async def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy"}


@app.get("/status")
async def status():
    """システムステータス - ダッシュボード用"""
    # Uptime計算
    uptime = datetime.datetime.now() - start_time
    uptime_str = str(uptime).split('.')[0]  # マイクロ秒を除去

    # システム情報
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    return {
        "status": "healthy",
        "uptime": uptime_str,
        "uptime_seconds": int(uptime.total_seconds()),
        "started_at": start_time.isoformat(),
        "current_time": datetime.datetime.now().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": round(memory.used / 1024 / 1024, 1),
            "memory_total_mb": round(memory.total / 1024 / 1024, 1),
        },
        "environment": {
            "platform": os.environ.get('PLATFORM', 'Unknown'),
            "python_version": platform.python_version(),
            "fastapi_version": fastapi.__version__,
            "hostname": platform.node(),
        }
    }


@app.get("/ping")
async def ping():
    """レイテンシ計測用エンドポイント"""
    request_time = time.time()
    return {
        "pong": True,
        "timestamp": request_time,
        "server_time": datetime.datetime.now().isoformat()
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8000))
    )
