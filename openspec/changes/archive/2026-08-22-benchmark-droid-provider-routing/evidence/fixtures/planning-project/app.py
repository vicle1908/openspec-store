from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": "test"}

@app.post("/users")
def create_user(name: str):
    return {"id": 1, "name": name}
