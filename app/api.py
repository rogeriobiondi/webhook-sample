# main.py

import datetime
import hashlib

from art import text2art
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, orm, service
from .database import SessionLocal, engine

orm.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Subscribers Operations
@app.post("/subscriptions")
async def new_subscription(request: models.SubscriptionRequest, db: Session = Depends(get_db)):
    o = models.Subscription(**request.dict())
    o.id = hashlib.md5(str(o.dict()).encode("UTF-8")).hexdigest()
    o.status = "SUBSCRIPTION_CREATED"
    service.create_subscription(db, o)
    return o

# Delete existing subscription
@app.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str, db: Session = Depends(get_db)):
    o = service.get_subscription(db, subscription_id)
    if o:
        db.delete(o)
        return { "status": "SUBSCRIPTION_DELETED" }
    raise HTTPException(status_code=404, detail="Subscription not found")

# Get existing subscription
@app.get("/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: str, db: Session = Depends(get_db)):
    o = service.get_subscription(db, subscription_id)
    if o: return o
    raise HTTPException(status_code=404, detail="Subscription not found")

# Webhook Documentation
@app.webhooks.post("temperature-update")
def temperature_update(body: models.Temperature):
    """
    When a new user subscribes to this service, will receive the temperatures of several places.
    """

# Regular API Operations
@app.get("/")
async def root():
    return {"message": "Hello World"}

print(text2art("API"))
print("starting...\n")
