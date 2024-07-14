from fastapi import FastAPI

from base.auth import router
from movies.views import router as movies_router

app = FastAPI()
app.include_router(router)
app.include_router(movies_router)



