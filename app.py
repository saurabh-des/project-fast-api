app = FastAPI(title="Product API", version="1.1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
