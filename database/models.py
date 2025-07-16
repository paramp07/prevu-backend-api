from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, Table, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID as SQLAlchemyUUID
from database.db import Base  # Your SQLAlchemy Base


# Association tables for many-to-many relationships
user_viewed_restaurants = Table(
    "user_viewed_restaurants",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("restaurant_id", ForeignKey("restaurants.id"), primary_key=True),
)

user_viewed_menu_items = Table(
    "user_viewed_menu_items",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("menu_item_id", ForeignKey("menu_items.id"), primary_key=True),
)

user_favorite_restaurants = Table(
    "user_favorite_restaurants",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("restaurant_id", ForeignKey("restaurants.id"), primary_key=True),
)

user_favorite_menu_items = Table(
    "user_favorite_menu_items",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("menu_item_id", ForeignKey("menu_items.id"), primary_key=True),
)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    restaurant_image = Column(String, nullable=True)

    categories = relationship(
        "Category",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, nullable=True)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    restaurant = relationship("Restaurant", back_populates="categories")

    items = relationship(
        "MenuItem",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, index=True)  # e.g. "main_courses_lasagna"
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    image_prompt = Column(Text, nullable=True)
    images = Column(ARRAY(String), nullable=True)  # URLs of images

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="items")


class User(Base):
    __tablename__ = "users"

    id = Column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        unique=True,
        nullable=False,
    )
    username = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    cuisine_preferences = Column(ARRAY(String), nullable=True)  # e.g., ['burgers', 'pizza']
    dietary_restrictions = Column(ARRAY(String), nullable=True)  # e.g., ['gluten', 'nuts']
    disliked_ingredients = Column(ARRAY(String), nullable=True)  # e.g., ['onion', 'garlic']

    viewed_restaurants = relationship(
        "Restaurant",
        secondary=user_viewed_restaurants,
        backref="viewed_by_users",
    )
    viewed_menu_items = relationship(
        "MenuItem",
        secondary=user_viewed_menu_items,
        backref="viewed_by_users",
    )
    favorite_restaurants = relationship(
        "Restaurant",
        secondary=user_favorite_restaurants,
        backref="favorited_by_users",
    )
    favorite_menu_items = relationship(
        "MenuItem",
        secondary=user_favorite_menu_items,
        backref="favorited_by_users",
    )


# Pydantic models for User (schemas.py)
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool = True  # you may want to add this field in DB later

    model_config = {
        "from_attributes": True,  # Pydantic v2 style instead of orm_mode
        "arbitrary_types_allowed": True,
    }
