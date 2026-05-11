from fastapi import FastAPI
from app.routers.books import router as books_router
from app.routers.users import router as user_router

app = FastAPI()

app.include_router(books_router)
app.include_router(user_router)