from fastapi import FastAPI

app = FastAPI(title="Delivery Service API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Delivery Service API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
