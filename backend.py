from fastapi import FastAPI
import uvicorn

#Init
app = FastAPI()

uvicorn.run(app host="127.0.0.1", port='8000')

@app.get("/")
async def root():
    return {"message": "Hello World"}
