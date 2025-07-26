import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RestaurantCreate(BaseModel):
    name: str
    location: Optional[str]
    description: Optional[str]
    currency: Optional[str]
    last_updated: Optional[datetime]
    restaurant_image: Optional[str]

class RestaurantOut(BaseModel):
    id: uuid.UUID
    name: str
    location: Optional[str]
    description: Optional[str]
    currency: Optional[str]
    last_updated: Optional[datetime]
    restaurant_image: Optional[str]

    class Config:
        from_attributes = True
