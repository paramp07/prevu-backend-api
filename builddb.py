from database.db import Base, engine
from database.models import User  # import your models

Base.metadata.create_all(bind=engine)
print("✅ Tables created.")
