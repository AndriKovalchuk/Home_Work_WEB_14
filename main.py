from pathlib import Path

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from middlewares import (BlackListMiddleware, CustomCORSMiddleware,
                         CustomHeaderMiddleware, UserAgentBanMiddleware,
                         WhiteListMiddleware)
from src.conf.config import config
from src.database.db import get_db
from src.routes import auth, contacts, users

app = FastAPI()

app.add_middleware(CustomHeaderMiddleware)  # noqa
app.add_middleware(CustomCORSMiddleware,  # noqa
                   origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )
# app.add_middleware(BlackListMiddleware)  # noqa
# app.add_middleware(WhiteListMiddleware) # noqa
# app.add_middleware(UserAgentBanMiddleware)  # noqa


BASE_DIR = Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, such as databases or caches.
    
    :return: A redis object
    :doc-author: Trelent
    """
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")  # noqa


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    The read_root function is a function that returns the root page of the website.
        It takes in a request object and returns an HTML response with the index.html template.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object, which is a special type of response object
    :doc-author: Trelent
    """
    return templates.TemplateResponse("index.html", {"request": request, "target": "Go IT Students"})


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It will return a 500 error if it cannot connect to the database, and a 200 OK if it can.
    
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary, which is converted to json
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Database is configured correctly"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
