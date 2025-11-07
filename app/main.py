from fastapi import FastAPI

app = FastAPI(title="Pizza Pi Calculator")

@app.get("/")
def root():
    return {"message": "Hello Pizza Pi!"}
    
