from fastapi import FastAPI

from app.database import Base, engine
from app.routes.datasets import router as datasets_router
from app.routes.kpis import router as kpis_router
from app.routes.uploads import router as uploads_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(datasets_router)
app.include_router(kpis_router)
app.include_router(uploads_router)


@app.get("/")
def root():
    return {"message": "Welcome to the Sales KPI API!"}
