from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    url = Column(String)
    auth_key = Column(String)
    status = Column(String)

    class Config:
           orm_mode = True
