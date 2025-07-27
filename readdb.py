from sqlalchemy.orm import Session
from database.models import Restaurant, MenuItem, User, Category
from database.db import SessionLocal
from pprint import pprint


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all(db: Session, model):
    return db.query(model).all()


def print_all_data():
    db_gen = get_db()
    db = next(db_gen)

    print("\n--- USERS ---")
    users = get_all(db, User)
    pprint([u.__dict__ for u in users])

    print("\n--- RESTAURANTS ---")
    restaurants = get_all(db, Restaurant)
    pprint([r.__dict__ for r in restaurants])

    print("\n--- CATEGORIES ---")
    categories = get_all(db, Category)
    pprint([c.__dict__ for c in categories])

    print("\n--- MENU ITEMS ---")
    items = get_all(db, MenuItem)
    pprint([i.__dict__ for i in items])

    db_gen.close()


if __name__ == "__main__":
    print_all_data()
