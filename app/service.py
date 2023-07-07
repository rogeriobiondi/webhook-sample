from sqlalchemy.orm import Session

from . import orm, models

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
