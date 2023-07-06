# main.py

import datetime
import hashlib
from typing import Optional

from art import text2art
from fastapi import FastAPI, HTTPException
from pydantic import AnyHttpUrl, BaseModel
from pysondb import db

app = FastAPI()

fakedb = db.getDb("./fakedb.json")

### Client configuration 

# Subscribers payload models

# API Request
class SubscriptionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    url: AnyHttpUrl
    auth_key: Optional[str]

# API Response
class SubscriptionResponse(SubscriptionRequest):
    id: Optional[str]
    status: Optional[str]

# Model class
class Subscription(SubscriptionResponse):
    pass
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

# Webhook Message Payloads
class Temperature(BaseModel):
    city: str
    reading: str
    unit: str 
    timestamp: datetime.datetime


# Subscribers Operations
@app.post("/subscriptions")
async def new_subscription(request: SubscriptionRequest):
    o = Subscription(**request.dict())
    o.id = hashlib.md5(str(o.dict()).encode("UTF-8")).hexdigest()
    o.status = "SUBSCRIPTION_CREATED"
    fakedb.add(o.__dict__)
    return o

# Delete existing subscription
@app.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: int):
    o = fakedb.getBy({"id": subscription_id })
    if o:
        fakedb.deleteById(subscription_id)
        return { "status": "SUBSCRIPTION_DELETED" }
    raise HTTPException(status_code=404, detail="Subscription not found")

# Get existing subscription
@app.get("/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: int):
    o = fakedb.getBy({"id": subscription_id })
    if len(o) > 0:
        return o[0]
    raise HTTPException(status_code=404, detail="Subscription not found")

# Webhook Documentation
@app.webhooks.post("temperature-update")
def temperature_update(body: Temperature):
    """
    When a new user subscribes to this service, will receive the temperatures of several places.
    """

# Regular API Operations
@app.get("/")
async def root():
    return {"message": "Hello World"}

print(text2art("API"))
print("starting...\n")
