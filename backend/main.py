from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def run_state():
    return {"message": "Running"}