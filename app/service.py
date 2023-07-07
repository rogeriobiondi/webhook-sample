import hashlib
import json

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.kafka import json_serializer, produce_message

from . import models, orm


# Subscriptions
def get_subscription(db: Session, id: str):
    return db.query(orm.Subscriptions).filter(orm.Subscriptions.id == id).first()

def get_subscriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.Subscriptions).offset(skip).limit(limit).all()

def create_subscription(db: Session, subscription: models.Subscription):
    o = orm.Subscriptions(**subscription.dict())
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

def get_subscription_by_name(db: Session, name: str):
    return db.query(orm.Subscriptions).filter(orm.Subscriptions.name == name).first()

# DLQ Messages
def get_dlq(db: Session, dlq_id: str):
    return db.query(orm.DLQ).filter(orm.DLQ.dlq_id == dlq_id).first()

def get_dlqs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.DLQ).offset(skip).limit(limit).all()

def create_dlq(db: Session, msg: str):
    o = orm.DLQ(event = msg)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

def delete_dlq(db: Session, dlq_id):
    o = get_dlq(db, dlq_id=dlq_id)
    if o:
        db.delete(o)
        db.commit()
        return True
    return False

def republish_dlq_event(db: Session, dlq_id: str):
    o = get_dlq(db, dlq_id)
    if o:
        event = json.loads(o.event)
        if produce_message(event):
            delete_dlq(db, dlq_id)

def republish_dlq_events(db: Session, events):
    for evt in events:
        print (f"Republishing DLQ event {evt}...")
        republish_dlq_event(db, evt)
