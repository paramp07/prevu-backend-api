from pydantic import BaseModel
from typing import List, Optional

class MenuItemBase(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    price: float
    tags: List[str] = []
    image_prompt: Optional[str]
    images: List[str] = []

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemOut(MenuItemBase):
    class Config:
        from_attributes = True  # Pydantic v2 ORM compatibility
