from fastapi import FastAPI
from app.routers import users, credits, plans

app = FastAPI()

# Підключаємо маршрути
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(credits.router, prefix="/credits", tags=["Credits"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"])


@app.get("/")
async def root():
    return {"message": "Hello, HTTP_Service!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
