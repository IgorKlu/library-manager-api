from fastapi import FastAPI
from app.routers.books import router as books_router
from app.routers.users import router as users_router
from app.routers.borrowings import router as borrowings_router
app = FastAPI()

app.include_router(books_router)
app.include_router(users_router)
app.include_router(borrowings_router)