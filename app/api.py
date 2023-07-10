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

# List subscriptions
@app.get("/subscriptions")
async def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    To avoid a security issue, 
    this operation should not be public
    in production environment
    """
    # TODO if environment == production => Operation not supported
    list_o = service.get_subscriptions(db, skip = skip, limit = limit)
    return list_o

# Patch OAuth key
@app.patch("/subscriptions/{subscription_id}")
async def patch_subscription(subscription_id: str, 
                     request: models.SubscriptionPatchRequest, db: Session = Depends(get_db)):
    update_data = request.dict(exclude_unset = True)
    service.patch_subscription(db, subscription_id, update_data)
    return { "status": "SUBSCRIPTION_UPDATED" }

# Webhook Documentation
@app.webhooks.post("temperature-update")
def temperature_update(body: models.Temperature):
    """
    When a new user subscribes to this service, will receive the temperatures of several places.
    """
    pass

# DLQ Operations
@app.get("/dlqs")
async def get_dlqs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return service.get_dlqs(db, skip=skip, limit=limit)

@app.post("/dlqs")
async def republish_dlq(request: models.DLQRepublishRequest, db: Session = Depends(get_db)):
    service.republish_dlq_events(db, request.dlqs)
    return { "status": "SUCCESS" }

# Regular API Operations
@app.get("/")
async def root():
    return {"message": "Hello World"}

print(text2art("API"))
print("starting...\n")
