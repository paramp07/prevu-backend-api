from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from database import Base  # Your Base from SQLAlchemy declarative base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String, nullable=True)
    description = Column(Text)
    currency = Column(String, default="USD")
    last_updated = Column(DateTime, default=datetime.utcnow)
    restaurant_image = Column(String, nullable=True)

    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    description = Column(Text)
    priority = Column(Integer)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    restaurant = relationship("Restaurant", back_populates="categories")

    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, index=True)  # like "main_courses_lasagna"
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    price = Column(Float)  # store as float for numeric operations
    tags = Column(ARRAY(String))
    image_prompt = Column(Text)
    images = Column(ARRAY(String))  # URLs of images

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="items")


# User models for future sign-in and preferences
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # preferences stored as JSON or arrays - flexible approach
    cuisine_preferences = Column(ARRAY(String))  # e.g. ['burgers', 'pizza']
    dietary_restrictions = Column(ARRAY(String))  # e.g. ['gluten', 'nuts']
    disliked_ingredients = Column(ARRAY(String))  # e.g. ['onion', 'garlic']

    # relationships for history and favorites
    viewed_restaurants = relationship("Restaurant", secondary="user_viewed_restaurants")
    viewed_menu_items = relationship("MenuItem", secondary="user_viewed_menu_items")
    favorite_restaurants = relationship("Restaurant", secondary="user_favorite_restaurants")
    favorite_menu_items = relationship("MenuItem", secondary="user_favorite_menu_items")



# Pydantic models for User (schemas.py)
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


# Association tables for many-to-many relationships
from sqlalchemy import Table

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