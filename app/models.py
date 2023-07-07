import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel

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
    
    class Config:
        orm_mode = True

# Webhook Message Payloads
class Temperature(BaseModel):
    city: str
    reading: str
    unit: str 
    timestamp: datetime.datetime
