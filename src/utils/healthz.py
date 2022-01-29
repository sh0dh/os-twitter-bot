from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
async def root():
    return {"message": "success", "code": "OK"}
