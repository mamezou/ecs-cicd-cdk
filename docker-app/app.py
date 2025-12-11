from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import datetime
import platform
import os
import fastapi

app = FastAPI()

# staticファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request, name: str = "FastAPI-demo"):
    time = datetime.datetime.now()
    python_version = platform.python_version()
    aws_platform = os.environ.get('PLATFORM', 'Amazon Web Services')
    
    return templates.TemplateResponse("hello.html", {
        "request": request,
        "platform": aws_platform,
        "fastapi_version": fastapi.__version__,
        "python_version": python_version,
        "fastapi_url": "https://fastapi.tiangolo.com/",
        "time": time,
        "name": name
    })


@app.get("/health")
async def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8000))
    )
