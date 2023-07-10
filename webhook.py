import datetime
import hashlib
from typing import Optional, Annotated

from art import text2art
from fastapi import FastAPI, HTTPException, Request
from pydantic import AnyHttpUrl, BaseModel
from pysondb import db

app = FastAPI()

# Webhook Message Payloads
class Temperature(BaseModel):
    city: str
    reading: str
    unit: str 
    timestamp: datetime.datetime

# Regular API Operations
@app.post("/")
async def root(temperature: Temperature, request: Request):
    print("Authorization header received:")
    print(request.headers["Authorization"])
    print("Data received:")
    print(temperature)
    print("===\n")
    return {
        "data": temperature,
        "status": "DATA_RECEIVED"
    }

print(text2art("WebHook"))
print("starting...\n")