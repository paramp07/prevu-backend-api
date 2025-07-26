from sqlalchemy.orm import Session
from database.models import Restaurant, MenuItem, User, Category
import uuid
from database.db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # --- Create ---
# def create_object(db: Session, model, data: dict):
#     obj = model(id=str(uuid.uuid4()), **data)
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj

def create_object(db, model, data):
    data.pop('id', None)  # Remove id if present
    obj = model(id=str(uuid.uuid4()), **data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj



# --- Get All ---
def get_all(db: Session, model):
    return db.query(model).all()

# --- Get One ---
def get_one(db: Session, model, object_id: str):
    return db.query(model).filter(model.id == object_id).first()

# --- Update ---
def update_object(db: Session, model, object_id: str, update_data: dict):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        return None
    for key, value in update_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

# --- Delete ---
def delete_object(db: Session, model, object_id: str):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    db_user = User(id=str(uuid.uuid4()), email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_restaurant_with_menu(db: Session, parsed_data: dict):
    restaurant = create_object(db, Restaurant, {
        "name": parsed_data["restaurant_name"],
        "location": parsed_data.get("location"),
        "description": parsed_data.get("description"),
        "currency": parsed_data.get("currency"),
        "last_updated": parsed_data.get("last_updated"),
        "restaurant_image": parsed_data.get("restaurant_image"),
    })

    for category_data in parsed_data.get("menu", []):
        category = create_object(db, Category, {
            "restaurant_id": restaurant.id,
            "category": category_data["category"],
            "description": category_data.get("description"),
            "priority": category_data.get("priority", 0),
        })

        for item_data in category_data.get("items", []):
            item_data["category_id"] = category.id
            create_object(db, MenuItem, item_data)

    return restaurant